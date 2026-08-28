from typing import Dict, Any

import pandas as pd

from data_pipeline.processing.statistics import (
    calculate_descriptive_statistics,
    calculate_percentiles,
    calculate_iqr,
    calculate_std_thresholds,
    detect_outliers,
    calculate_salary_ranges,
)


def generate_salary_insights(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a complete salary-insights payload from a cleaned
    Pandas DataFrame.

    The calculations are delegated to the statistical functions
    already implemented and tested in statistics.py.
    """

    salary = df["normalized_salary_midpoint"].dropna().to_numpy()

    if len(salary) == 0:
        raise ValueError("No valid salary data available for analysis.")

    # ---------------------------------------------------------
    # Core descriptive statistics
    # ---------------------------------------------------------
    descriptive = calculate_descriptive_statistics(salary)

    # ---------------------------------------------------------
    # Percentiles
    # ---------------------------------------------------------
    percentiles = calculate_percentiles(salary)

    # ---------------------------------------------------------
    # Interquartile range
    # ---------------------------------------------------------
    iqr = calculate_iqr(salary)

    # ---------------------------------------------------------
    # Standard deviation thresholds
    # ---------------------------------------------------------
    std_thresholds = calculate_std_thresholds(salary)

    # ---------------------------------------------------------
    # Outlier analysis
    # ---------------------------------------------------------
    outliers = detect_outliers(salary)

    # ---------------------------------------------------------
    # Salary range analysis
    # ---------------------------------------------------------
    range_analysis = calculate_salary_ranges(df)

    # ---------------------------------------------------------
    # Combine everything into one database-ready payload
    # ---------------------------------------------------------
    return {
        "job_count": len(df),
        "salary_count": len(salary),

        "mean_salary": descriptive["mean"],
        "median_salary": descriptive["median"],
        "minimum_salary": descriptive["minimum"],
        "maximum_salary": descriptive["maximum"],
        "standard_deviation": descriptive["standard_deviation"],

        "p25": percentiles["p25"],
        "p50": percentiles["p50"],
        "p75": percentiles["p75"],

        "q1": iqr["q1"],
        "q3": iqr["q3"],
        "iqr": iqr["iqr"],

        "lower_1_std": std_thresholds["lower_1_std"],
        "upper_1_std": std_thresholds["upper_1_std"],
        "lower_2_std": std_thresholds["lower_2_std"],
        "upper_2_std": std_thresholds["upper_2_std"],

        "outlier_count": outliers["outlier_count"],
        "lower_outlier_count": outliers["lower_outlier_count"],
        "upper_outlier_count": outliers["upper_outlier_count"],

        "jobs_with_min_salary": range_analysis["jobs_with_min_salary"],
        "jobs_with_max_salary": range_analysis["jobs_with_max_salary"],
        "jobs_with_midpoint_salary": range_analysis["jobs_with_midpoint_salary"],
        "jobs_with_complete_range": range_analysis["jobs_with_complete_range"],

        "minimum_range": range_analysis["minimum_range"],
        "maximum_range": range_analysis["maximum_range"],
        "mean_range": range_analysis["mean_range"],
        "median_range": range_analysis["median_range"],
    }
