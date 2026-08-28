import numpy as np
import pandas as pd

from data_pipeline.processing.statistics import (
    prepare_salary_arrays,
    calculate_descriptive_statistics,
    calculate_salary_statistics,
    calculate_percentiles,
    calculate_iqr,
    calculate_std_thresholds,
    calculate_distribution_statistics,
    calculate_outlier_bounds,
    detect_outliers,
    calculate_salary_ranges,
    safe_statistics,
    build_salary_analytics
)
from data_pipeline.storage.bronze_loader import load_bronze_json
from data_pipeline.processing.transform import transform_dataframe
from data_pipeline.utils.helper import get_latest_bronze_file

def get_clean_dataframe():
    """
    Load the latest Bronze dataset and run the Phase 2.2
    cleaning/transformation pipeline.
    """

    bronze_file = get_latest_bronze_file()
    df = load_bronze_json(bronze_file)
    return transform_dataframe(df)


def test_prepare_salary_arrays():

    df = get_clean_dataframe()

    arrays = prepare_salary_arrays(df)

    print("\n" + "=" * 60)
    print("NUMPY ARRAY PREPARATION")
    print("=" * 60)

    for name, values in arrays.items():
        print(f"\n{name}:")
        print(f"Type: {type(values)}")
        print(f"Shape: {values.shape}")
        print(f"Dtype: {values.dtype}")
        print(f"First values: {values[:10]}")

        assert isinstance(values, np.ndarray)
        assert values.dtype == np.float64
        assert not np.isnan(values).any()


def test_descriptive_statistics():

    values = np.array(
        [32000, 41000, 52000, 57000, 60000],
        dtype=float,
    )

    stats = calculate_descriptive_statistics(values)

    print("\n" + "=" * 60)
    print("CORE DESCRIPTIVE STATISTICS")
    print("=" * 60)

    for key, value in stats.items():
        print(f"{key}: {value}")

    assert stats["count"] == 5
    assert stats["mean"] == 48400.0
    assert stats["median"] == 52000.0
    assert stats["minimum"] == 32000.0
    assert stats["maximum"] == 60000.0

    expected_std = np.std(values)

    assert np.isclose(
        stats["standard_deviation"],
        expected_std,
    )


def test_salary_statistics():

    df = get_clean_dataframe()

    statistics = calculate_salary_statistics(df)

    print("\n" + "=" * 60)
    print("SALARY STATISTICS")
    print("=" * 60)

    for salary_type, stats in statistics.items():

        print(f"\n{salary_type}")

        for key, value in stats.items():
            print(f"  {key}: {value}")

        assert stats["count"] > 0
        assert stats["minimum"] >= 0
        assert stats["maximum"] >= stats["minimum"]


def test_percentiles():

    values = np.array(
        [32000, 41000, 52000, 57000, 60000],
        dtype=float,
    )

    percentiles = calculate_percentiles(values)

    print("\n" + "=" * 60)
    print("PERCENTILES")
    print("=" * 60)

    for key, value in percentiles.items():
        print(f"{key}: {value}")

    assert percentiles["p25"] == 41000.0
    assert percentiles["p50"] == 52000.0
    assert percentiles["p75"] == 57000.0


def test_iqr():

    values = np.array(
        [32000, 41000, 52000, 57000, 60000],
        dtype=float,
    )

    result = calculate_iqr(values)

    print("\n" + "=" * 60)
    print("INTERQUARTILE RANGE")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")

    assert result["q1"] == 41000.0
    assert result["q3"] == 57000.0
    assert result["iqr"] == 16000.0


def test_std_thresholds():

    values = np.array(
        [32000, 41000, 52000, 57000, 60000],
        dtype=float,
    )

    result = calculate_std_thresholds(values)

    print("\n" + "=" * 60)
    print("STANDARD DEVIATION THRESHOLDS")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")

    expected_std = np.std(values)

    assert result["mean"] == 48400.0
    assert np.isclose(
        result["standard_deviation"],
        expected_std,
    )

    assert np.isclose(
        result["lower_1_std"],
        48400.0 - expected_std,
    )

    assert np.isclose(
        result["upper_1_std"],
        48400.0 + expected_std,
    )

    assert np.isclose(
        result["lower_2_std"],
        48400.0 - (2 * expected_std),
    )

    assert np.isclose(
        result["upper_2_std"],
        48400.0 + (2 * expected_std),
    )


def test_distribution_statistics():

    df = get_clean_dataframe()

    arrays = prepare_salary_arrays(df)

    values = arrays["normalized_salary_midpoint"]

    result = calculate_distribution_statistics(values)

    print("\n" + "=" * 60)
    print("COMPLETE SALARY DISTRIBUTION")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")

    assert result["count"] == len(values)

    assert result["minimum"] >= 0
    assert result["maximum"] >= result["minimum"]

    assert result["p25"] <= result["p50"]
    assert result["p50"] <= result["p75"]

    assert result["q1"] == result["p25"]
    assert result["q3"] == result["p75"]

    assert result["iqr"] == result["q3"] - result["q1"]

    assert result["lower_1_std"] < result["upper_1_std"]
    assert result["lower_2_std"] < result["upper_2_std"]

##

def test_outlier_bounds():
    values = np.array([
        50000,
        51000,
        52000,
        53000,
        54000,
        55000,
        56000,
        57000,
        100000,
    ], dtype=float)

    result = calculate_outlier_bounds(values)

    print("\n" + "=" * 60)
    print("OUTLIER BOUNDS")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")

    assert result["iqr"] > 0
    assert result["lower_bound"] < result["q1"]
    assert result["upper_bound"] > result["q3"]


def test_detect_outliers():
    values = np.array([
        50000,
        51000,
        52000,
        53000,
        54000,
        55000,
        56000,
        57000,
        100000,
    ], dtype=float)

    result = detect_outliers(values)

    print("\n" + "=" * 60)
    print("OUTLIER DETECTION")
    print("=" * 60)

    print(f"Lower bound: {result['lower_bound']}")
    print(f"Upper bound: {result['upper_bound']}")
    print(f"Lower outliers: {result['lower_outliers']}")
    print(f"Upper outliers: {result['upper_outliers']}")
    print(f"All outliers: {result['outliers']}")
    print(f"Outlier count: {result['outlier_count']}")

    assert result["upper_outlier_count"] == 1
    assert result["lower_outlier_count"] == 0
    assert result["outlier_count"] == 1
    assert result["upper_outliers"][0] == 100000


def test_salary_range_analysis():
    df = pd.DataFrame({
        "normalized_salary_min": [
            30000,
            40000,
            np.nan,
            50000,
        ],
        "normalized_salary_max": [
            50000,
            60000,
            55000,
            70000,
        ],
        "normalized_salary_midpoint": [
            40000,
            50000,
            55000,
            60000,
        ],
    })

    result = calculate_salary_ranges(df)

    print("\n" + "=" * 60)
    print("SALARY RANGE ANALYSIS")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")

    assert result["jobs_with_min_salary"] == 3
    assert result["jobs_with_max_salary"] == 4
    assert result["jobs_with_midpoint_salary"] == 4

    # Only rows with BOTH min and max are valid salary ranges.
    assert result["jobs_with_complete_range"] == 3

    assert result["minimum_range"] == 20000.0
    assert result["maximum_range"] == 20000.0
    assert result["mean_range"] == 20000.0
    assert result["median_range"] == 20000.0


def test_safe_statistics_with_valid_values():
    values = np.array([32000, 41000, 52000, 57000, 60000], dtype=float)

    result = safe_statistics(values)

    assert result["count"] == 5
    assert result["mean"] == np.mean(values)
    assert result["median"] == np.median(values)
    assert result["minimum"] == np.min(values)
    assert result["maximum"] == np.max(values)
    print("PASSED: test_safe_statistics_with_valid_values")


def test_safe_statistics_with_nan_and_infinite_values():
    values = np.array(
        [32000, 41000, np.nan, np.inf, 52000],
        dtype=float,
    )

    result = safe_statistics(values)

    assert result["count"] == 3
    assert result["minimum"] == 32000
    assert result["maximum"] == 52000
    print("PASSED: test_safe_statistics_with_nan_and_infinite_values")


def test_safe_statistics_with_empty_array():
    values = np.array([], dtype=float)

    result = safe_statistics(values)

    assert result["count"] == 0
    assert result["mean"] is None
    assert result["median"] is None
    assert result["minimum"] is None
    assert result["maximum"] is None
    assert result["standard_deviation"] is None
    print("PASSED: test_safe_statistics_with_empty_array")


def test_build_salary_analytics_structure():
    values = np.array(
        [32000, 41000, 52000, 57000, 60000],
        dtype=float,
    )

    result = build_salary_analytics(values)

    assert "statistics" in result
    assert "percentiles" in result
    assert "quartiles" in result
    assert "standard_deviation_thresholds" in result
    assert "outliers" in result
    print("PASSED: test_build_salary_analytics_structure")


def test_build_salary_analytics_values():
    values = np.array(
        [32000, 41000, 52000, 57000, 60000],
        dtype=float,
    )

    result = build_salary_analytics(values)

    assert result["statistics"]["count"] == 5
    assert result["statistics"]["median"] == 52000

    assert result["percentiles"]["p25"] == 41000
    assert result["percentiles"]["p50"] == 52000
    assert result["percentiles"]["p75"] == 57000

    assert result["quartiles"]["q1"] == 41000
    assert result["quartiles"]["q3"] == 57000
    assert result["quartiles"]["iqr"] == 16000
    print("PASSED: test_build_salary_analytics_values")


def test_build_salary_analytics_handles_nan():
    values = np.array(
        [32000, 41000, np.nan, 52000, np.inf],
        dtype=float,
    )

    result = build_salary_analytics(values)

    assert result["statistics"]["count"] == 3
    assert result["statistics"]["minimum"] == 32000
    assert result["statistics"]["maximum"] == 52000
    print("PASSED: test_build_salary_analytics_handles_nan")


def test_build_salary_analytics_empty_array():
    values = np.array([], dtype=float)

    result = build_salary_analytics(values)

    assert result["statistics"]["count"] == 0
    assert result["percentiles"] == {}
    assert result["quartiles"] == {}
    assert result["standard_deviation_thresholds"] == {}
    assert result["outliers"] == {}
    print("PASSED: test_build_salary_analytics_empty_array")


if __name__ == "__main__":
    test_prepare_salary_arrays()
    test_descriptive_statistics()
    test_salary_statistics()
    test_percentiles()
    test_iqr()
    test_std_thresholds()
    test_distribution_statistics()
    test_outlier_bounds()
    test_detect_outliers()
    test_salary_range_analysis()
    test_safe_statistics_with_valid_values()
    test_safe_statistics_with_nan_and_infinite_values()
    test_safe_statistics_with_empty_array()
    test_build_salary_analytics_structure()
    test_build_salary_analytics_values()
    test_build_salary_analytics_handles_nan()
    test_build_salary_analytics_empty_array()

    print("\n" + "=" * 60)
    print("ALL 2.3-A + 2.3-B STATISTICS TESTS PASSED")
    print("=" * 60)