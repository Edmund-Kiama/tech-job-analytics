import pandas as pd

from data_pipeline.database.connection import SessionLocal, engine
from data_pipeline.database.models import Base, SalaryInsight
from data_pipeline.processing.salary_insights import generate_salary_insights
from data_pipeline.services.salary_insights import save_salary_insights


def create_test_dataframe():
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


def test_save_salary_insights():
    """
    Verify that generated salary insights can be persisted
    and read back from SQLite.
    """

    # Make sure the test database schema exists.
    Base.metadata.create_all(engine)

    df = create_test_dataframe()

    insights = generate_salary_insights(df)

    with SessionLocal() as session:
        saved = save_salary_insights(session, insights)

        session.commit()

        saved_id = saved.id

    # Open a fresh session to verify the actual database record.
    with SessionLocal() as session:
        result = (
            session.query(SalaryInsight).filter(SalaryInsight.id == saved_id).first()
        )

        assert result is not None

        assert result.job_count == 5
        assert result.salary_count == 5

        assert result.mean_salary == 55000.0
        assert result.median_salary == 55000.0
        assert result.minimum_salary == 45000.0
        assert result.maximum_salary == 65000.0

        assert result.p25 == 50000.0
        assert result.p50 == 55000.0
        assert result.p75 == 60000.0

        assert result.q1 == 50000.0
        assert result.q3 == 60000.0
        assert result.iqr == 10000.0

        assert result.outlier_count == 0
        assert result.lower_outlier_count == 0
        assert result.upper_outlier_count == 0

        assert result.jobs_with_min_salary == 5
        assert result.jobs_with_max_salary == 5
        assert result.jobs_with_midpoint_salary == 5
        assert result.jobs_with_complete_range == 5

        assert result.minimum_range == 10000.0
        assert result.maximum_range == 10000.0
        assert result.mean_range == 10000.0
        assert result.median_range == 10000.0


def test_save_salary_insights_returns_model_instance():
    Base.metadata.create_all(engine)

    df = create_test_dataframe()
    insights = generate_salary_insights(df)

    with SessionLocal() as session:
        saved = save_salary_insights(session, insights)

        assert isinstance(saved, SalaryInsight)
        assert saved.id is not None
        assert saved.created_at is not None

        session.rollback()
