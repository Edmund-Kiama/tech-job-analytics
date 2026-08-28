from datetime import datetime, timezone

from sqlalchemy import inspect

from data_pipeline.database.connection import engine
from data_pipeline.database.models import Base, Listing, SalaryInsight


def test_listing_model_exists():
    assert Listing.__tablename__ == "listings"


def test_salary_insight_model_exists():
    assert SalaryInsight.__tablename__ == "salary_insights"


def test_salary_insight_table_schema():
    Base.metadata.create_all(engine)

    inspector = inspect(engine)

    assert "salary_insights" in inspector.get_table_names()

    columns = {
        column["name"]: column for column in inspector.get_columns("salary_insights")
    }

    expected_columns = {
        "id",
        "created_at",
        "job_count",
        "salary_count",
        "mean_salary",
        "median_salary",
        "minimum_salary",
        "maximum_salary",
        "standard_deviation",
        "p25",
        "p50",
        "p75",
        "q1",
        "q3",
        "iqr",
        "lower_1_std",
        "upper_1_std",
        "lower_2_std",
        "upper_2_std",
        "outlier_count",
        "lower_outlier_count",
        "upper_outlier_count",
        "jobs_with_min_salary",
        "jobs_with_max_salary",
        "jobs_with_midpoint_salary",
        "jobs_with_complete_range",
        "minimum_range",
        "maximum_range",
        "mean_range",
        "median_range",
    }

    assert set(columns.keys()) == expected_columns


def test_salary_insight_primary_key():
    primary_key = inspect(engine).get_pk_constraint("salary_insights")

    assert primary_key["constrained_columns"] == ["id"]


def test_salary_insight_model_can_be_instantiated():
    insight = SalaryInsight(
        created_at=datetime.now(timezone.utc),
        job_count=30,
        salary_count=30,
        mean_salary=57640.0,
        median_salary=60000.0,
        minimum_salary=32000.0,
        maximum_salary=66000.0,
        standard_deviation=6493.97,
        p25=57000.0,
        p50=60000.0,
        p75=60000.0,
        q1=57000.0,
        q3=60000.0,
        iqr=3000.0,
        lower_1_std=51146.02,
        upper_1_std=64133.98,
        lower_2_std=44652.05,
        upper_2_std=70627.95,
        outlier_count=1,
        lower_outlier_count=0,
        upper_outlier_count=1,
        jobs_with_min_salary=1,
        jobs_with_max_salary=30,
        jobs_with_midpoint_salary=30,
        jobs_with_complete_range=1,
        minimum_range=23600.0,
        maximum_range=23600.0,
        mean_range=23600.0,
        median_range=23600.0,
    )

    assert insight.job_count == 30
    assert insight.salary_count == 30
    assert insight.median_salary == 60000.0
    assert insight.iqr == 3000.0
    assert insight.outlier_count == 1
