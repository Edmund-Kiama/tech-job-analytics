import pandas as pd
import pytest

from data_pipeline.processing.salary_insights import generate_salary_insights


def create_test_dataframe():
    """
    Small deterministic dataset used to verify that the
    salary-insight generator correctly combines the existing
    statistical calculations.
    """

    return pd.DataFrame(
        {
            "id": ["1", "2", "3", "4", "5"],
            "normalized_salary_min": [
                40000.0,
                45000.0,
                50000.0,
                55000.0,
                60000.0,
            ],
            "normalized_salary_max": [
                50000.0,
                55000.0,
                60000.0,
                65000.0,
                70000.0,
            ],
            "normalized_salary_midpoint": [
                45000.0,
                50000.0,
                55000.0,
                60000.0,
                65000.0,
            ],
        }
    )


def test_generate_salary_insights():
    df = create_test_dataframe()

    insights = generate_salary_insights(df)

    print("\n")
    print("=" * 60)
    print("GENERATED SALARY INSIGHTS")
    print("=" * 60)

    for key, value in insights.items():
        print(f"{key}: {value}")

    assert isinstance(insights, dict)

    # Dataset-level values
    assert insights["job_count"] == 5
    assert insights["salary_count"] == 5

    # Core statistics
    assert insights["mean_salary"] == 55000.0
    assert insights["median_salary"] == 55000.0
    assert insights["minimum_salary"] == 45000.0
    assert insights["maximum_salary"] == 65000.0

    # Percentiles
    assert insights["p25"] == 50000.0
    assert insights["p50"] == 55000.0
    assert insights["p75"] == 60000.0

    # IQR
    assert insights["q1"] == 50000.0
    assert insights["q3"] == 60000.0
    assert insights["iqr"] == 10000.0

    # Salary ranges
    assert insights["jobs_with_min_salary"] == 5
    assert insights["jobs_with_max_salary"] == 5
    assert insights["jobs_with_midpoint_salary"] == 5
    assert insights["jobs_with_complete_range"] == 5

    assert insights["minimum_range"] == 10000.0
    assert insights["maximum_range"] == 10000.0
    assert insights["mean_range"] == 10000.0
    assert insights["median_range"] == 10000.0


def test_generate_salary_insights_rejects_missing_salary_data():
    df = pd.DataFrame(
        {
            "normalized_salary_midpoint": [
                None,
                None,
                None,
            ]
        }
    )

    with pytest.raises(ValueError, match="No valid salary data"):
        generate_salary_insights(df)


def test_generate_salary_insights_preserves_job_count():
    df = pd.DataFrame(
        {
            "normalized_salary_midpoint": [
                40000.0,
                None,
                60000.0,
            ],
            "normalized_salary_min": [
                35000.0,
                None,
                55000.0,
            ],
            "normalized_salary_max": [
                45000.0,
                None,
                65000.0,
            ],
        }
    )

    insights = generate_salary_insights(df)

    # There are 3 jobs, but only 2 have usable midpoint salaries.
    assert insights["job_count"] == 3
    assert insights["salary_count"] == 2
