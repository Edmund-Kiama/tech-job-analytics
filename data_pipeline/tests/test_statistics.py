import numpy as np

from data_pipeline.processing.statistics import (
    prepare_salary_arrays,
    calculate_descriptive_statistics,
    calculate_salary_statistics,
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


if __name__ == "__main__":
    test_prepare_salary_arrays()
    test_descriptive_statistics()
    test_salary_statistics()

    print("\n" + "=" * 60)
    print("ALL STATISTICS TESTS PASSED")
    print("=" * 60)