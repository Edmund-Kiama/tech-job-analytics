from typing import Dict

import numpy as np
import pandas as pd


def prepare_salary_arrays(df: pd.DataFrame) -> Dict[str, np.ndarray]:
    """
    Extract valid salary observations from a cleaned DataFrame
    and convert them into NumPy arrays.
    """

    salary_min = pd.to_numeric(
        df["normalized_salary_min"],
        errors="coerce",
    ).dropna().to_numpy(dtype=float)

    salary_max = pd.to_numeric(
        df["normalized_salary_max"],
        errors="coerce",
    ).dropna().to_numpy(dtype=float)

    salary_midpoint = pd.to_numeric(
        df["normalized_salary_midpoint"],
        errors="coerce",
    ).dropna().to_numpy(dtype=float)

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
        raise ValueError(
            "Cannot calculate statistics from an empty array."
        )

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