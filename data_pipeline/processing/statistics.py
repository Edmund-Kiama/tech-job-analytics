from typing import Any, Dict

import numpy as np
import pandas as pd


def prepare_salary_arrays(df: pd.DataFrame) -> Dict[str, np.ndarray]:
    """
    Extract valid salary observations from a cleaned DataFrame
    and convert them into NumPy arrays.
    """

    salary_min = (
        pd.to_numeric(
            df["normalized_salary_min"],
            errors="coerce",
        )
        .dropna()
        .to_numpy(dtype=float)
    )

    salary_max = (
        pd.to_numeric(
            df["normalized_salary_max"],
            errors="coerce",
        )
        .dropna()
        .to_numpy(dtype=float)
    )

    salary_midpoint = (
        pd.to_numeric(
            df["normalized_salary_midpoint"],
            errors="coerce",
        )
        .dropna()
        .to_numpy(dtype=float)
    )

    return {
        "normalized_salary_min": salary_min,
        "normalized_salary_max": salary_max,
        "normalized_salary_midpoint": salary_midpoint,
    }


def calculate_descriptive_statistics(
    values: np.ndarray,
) -> Dict[str, float]:
    """
    Calculate core descriptive statistics for a NumPy array.

    NaN values are removed before calculation.
    """

    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]

    if values.size == 0:
        raise ValueError("Cannot calculate statistics from an empty array.")

    return {
        "count": int(values.size),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "minimum": float(np.min(values)),
        "maximum": float(np.max(values)),
        "standard_deviation": float(np.std(values)),
    }


def calculate_salary_statistics(
    df: pd.DataFrame,
) -> Dict[str, Dict[str, float]]:
    """
    Prepare salary arrays and calculate descriptive statistics
    for each salary measure.
    """

    arrays = prepare_salary_arrays(df)

    return {
        column: calculate_descriptive_statistics(values)
        for column, values in arrays.items()
    }


def calculate_percentiles(
    values: np.ndarray,
) -> Dict[str, float]:
    """
    Calculate the 25th, 50th, and 75th percentiles.

    P25 = first quartile (Q1)
    P50 = second quartile (Q2 / median)
    P75 = third quartile (Q3)
    """

    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]

    if values.size == 0:
        raise ValueError("Cannot calculate percentiles from an empty array.")

    p25, p50, p75 = np.percentile(
        values,
        [25, 50, 75],
    )

    return {
        "p25": float(p25),
        "p50": float(p50),
        "p75": float(p75),
    }


def calculate_iqr(
    values: np.ndarray,
) -> Dict[str, float]:
    """
    Calculate quartiles and the interquartile range.

    IQR = Q3 - Q1
    """

    percentiles = calculate_percentiles(values)

    q1 = percentiles["p25"]
    q3 = percentiles["p75"]

    return {
        "q1": q1,
        "q3": q3,
        "iqr": float(q3 - q1),
    }


def calculate_std_thresholds(
    values: np.ndarray,
) -> Dict[str, float]:
    """
    Calculate standard-deviation-based thresholds.

    Provides thresholds at one and two standard deviations
    from the mean.
    """

    stats = calculate_descriptive_statistics(values)

    mean = stats["mean"]
    std = stats["standard_deviation"]

    return {
        "mean": mean,
        "standard_deviation": std,
        "lower_1_std": float(mean - std),
        "upper_1_std": float(mean + std),
        "lower_2_std": float(mean - (2 * std)),
        "upper_2_std": float(mean + (2 * std)),
    }


def calculate_distribution_statistics(
    values: np.ndarray,
) -> Dict[str, float]:
    """
    Calculate the complete distribution profile for a
    salary NumPy array.

    Includes:
    - count
    - mean
    - median
    - minimum
    - maximum
    - standard deviation
    - P25 / Q1
    - P50 / Q2
    - P75 / Q3
    - IQR
    - ±1 standard deviation thresholds
    - ±2 standard deviation thresholds
    """

    descriptive = calculate_descriptive_statistics(values)
    percentiles = calculate_percentiles(values)
    iqr = calculate_iqr(values)
    std_thresholds = calculate_std_thresholds(values)

    return {
        **descriptive,
        **percentiles,
        **iqr,
        "lower_1_std": std_thresholds["lower_1_std"],
        "upper_1_std": std_thresholds["upper_1_std"],
        "lower_2_std": std_thresholds["lower_2_std"],
        "upper_2_std": std_thresholds["upper_2_std"],
    }


def prepare_numpy_array(
    df: pd.DataFrame,
    column: str,
) -> np.ndarray:
    """
    Prepare a clean NumPy array from a DataFrame column.

    Missing values are removed before conversion.
    """
    return df[column].dropna().to_numpy(dtype=float)


def calculate_outlier_bounds(
    values: np.ndarray,
) -> Dict[str, float]:
    """
    Calculate the lower and upper bounds for IQR-based
    outlier detection.

    Values outside these bounds are considered outliers.
    """
    quartiles = calculate_iqr(values)

    q1 = quartiles["q1"]
    q3 = quartiles["q3"]
    iqr = quartiles["iqr"]

    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower_bound": q1 - (1.5 * iqr),
        "upper_bound": q3 + (1.5 * iqr),
    }


def detect_outliers(
    values: np.ndarray,
) -> Dict[str, Any]:
    """
    Detect lower and upper outliers using the IQR method.

    Outliers are identified but NOT removed.
    """
    if len(values) == 0:
        raise ValueError("Cannot detect outliers in an empty array.")

    bounds = calculate_outlier_bounds(values)

    lower_bound = bounds["lower_bound"]
    upper_bound = bounds["upper_bound"]

    lower_outliers = values[values < lower_bound]
    upper_outliers = values[values > upper_bound]

    all_outliers = values[(values < lower_bound) | (values > upper_bound)]

    return {
        **bounds,
        "lower_outliers": lower_outliers,
        "upper_outliers": upper_outliers,
        "outliers": all_outliers,
        "lower_outlier_count": int(len(lower_outliers)),
        "upper_outlier_count": int(len(upper_outliers)),
        "outlier_count": int(len(all_outliers)),
    }


def calculate_salary_ranges(
    df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Analyze the relationship between normalized minimum,
    maximum, and midpoint salaries.

    Only jobs with valid minimum and maximum salary values
    are included in the advertised-range calculations.
    """
    required_columns = [
        "normalized_salary_min",
        "normalized_salary_max",
        "normalized_salary_midpoint",
    ]

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required salary columns: {missing_columns}")

    salary_min = prepare_numpy_array(
        df,
        "normalized_salary_min",
    )

    salary_max = prepare_numpy_array(
        df,
        "normalized_salary_max",
    )

    midpoint = prepare_numpy_array(
        df,
        "normalized_salary_midpoint",
    )

    # A salary range only exists when both min and max are present.
    valid_ranges = df[
        [
            "normalized_salary_min",
            "normalized_salary_max",
        ]
    ].dropna()

    range_values = (
        valid_ranges["normalized_salary_max"] - valid_ranges["normalized_salary_min"]
    ).to_numpy(dtype=float)

    result = {
        "jobs_with_min_salary": int(len(salary_min)),
        "jobs_with_max_salary": int(len(salary_max)),
        "jobs_with_midpoint_salary": int(len(midpoint)),
        "jobs_with_complete_range": int(len(range_values)),
    }

    if len(range_values) > 0:
        result.update(
            {
                "minimum_range": float(np.min(range_values)),
                "maximum_range": float(np.max(range_values)),
                "mean_range": float(np.mean(range_values)),
                "median_range": float(np.median(range_values)),
            }
        )
    else:
        result.update(
            {
                "minimum_range": None,
                "maximum_range": None,
                "mean_range": None,
                "median_range": None,
            }
        )

    return result


def safe_statistics(values):
    """
    Calculate statistics safely for an arbitrary numeric array.

    Handles:
    - empty arrays
    - NaN values
    - non-finite values
    """

    values = np.asarray(values, dtype=float)

    # Remove NaN and infinite values
    values = values[np.isfinite(values)]

    if values.size == 0:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "minimum": None,
            "maximum": None,
            "standard_deviation": None,
        }

    return {
        "count": int(values.size),
        "mean": float(np.mean(values)),
        "median": float(np.median(values)),
        "minimum": float(np.min(values)),
        "maximum": float(np.max(values)),
        "standard_deviation": float(np.std(values)),
    }


def build_salary_analytics(values):
    """
    Produce a structured analytics dictionary for a salary array.

    This combines the major statistical outputs developed in Phase 2.3:
    - descriptive statistics
    - percentiles
    - quartiles / IQR
    - standard-deviation thresholds
    - outlier detection
    - salary-range information where applicable
    """

    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]

    if values.size == 0:
        return {
            "statistics": safe_statistics(values),
            "percentiles": {},
            "quartiles": {},
            "standard_deviation_thresholds": {},
            "outliers": {},
        }

    q1 = float(np.percentile(values, 25))
    median = float(np.percentile(values, 50))
    q3 = float(np.percentile(values, 75))
    iqr = q3 - q1

    mean = float(np.mean(values))
    std = float(np.std(values))

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    lower_outliers = values[values < lower_bound]
    upper_outliers = values[values > upper_bound]

    return {
        "statistics": {
            "count": int(values.size),
            "mean": mean,
            "median": median,
            "minimum": float(np.min(values)),
            "maximum": float(np.max(values)),
            "standard_deviation": std,
        },
        "percentiles": {
            "p25": q1,
            "p50": median,
            "p75": q3,
        },
        "quartiles": {
            "q1": q1,
            "q3": q3,
            "iqr": float(iqr),
        },
        "standard_deviation_thresholds": {
            "lower_1_std": mean - std,
            "upper_1_std": mean + std,
            "lower_2_std": mean - (2 * std),
            "upper_2_std": mean + (2 * std),
        },
        "outliers": {
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "lower_outliers": lower_outliers.tolist(),
            "upper_outliers": upper_outliers.tolist(),
            "all_outliers": np.concatenate([lower_outliers, upper_outliers]).tolist(),
            "count": int(lower_outliers.size + upper_outliers.size),
        },
    }
