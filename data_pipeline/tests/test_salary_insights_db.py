from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_pipeline.database.models import Base, SalaryInsight
from data_pipeline.processing.statistics import (
    build_salary_insight_record,
)
from data_pipeline.services.salary_insights import save_salary_insights


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


def sample_statistics():
    return {
        "count": 5,
        "mean": 55000.0,
        "median": 55000.0,
        "minimum": 45000.0,
        "maximum": 65000.0,
        "standard_deviation": 7071.067811865475,
        "p25": 50000.0,
        "p50": 55000.0,
        "p75": 60000.0,
        "q1": 50000.0,
        "q3": 60000.0,
        "iqr": 10000.0,
        "lower_1_std": 47928.932188134524,
        "upper_1_std": 62071.067811865476,
        "lower_2_std": 40857.86437626905,
        "upper_2_std": 69142.13562373095,
        "outlier_count": 0,
        "lower_outlier_count": 0,
        "upper_outlier_count": 0,
        "jobs_with_min_salary": 5,
        "jobs_with_max_salary": 5,
        "jobs_with_midpoint_salary": 5,
        "jobs_with_complete_range": 5,
        "minimum_range": 10000.0,
        "maximum_range": 10000.0,
        "mean_range": 10000.0,
        "median_range": 10000.0,
    }


def test_build_salary_insight_record():
    stats = sample_statistics()

    record = build_salary_insight_record(stats)

    assert isinstance(record, dict)

    assert record["job_count"] == 5
    assert record["salary_count"] == 5

    assert record["mean_salary"] == 55000.0
    assert record["median_salary"] == 55000.0

    assert record["p25"] == 50000.0
    assert record["p75"] == 60000.0

    assert record["iqr"] == 10000.0

    assert record["outlier_count"] == 0

    assert record["jobs_with_complete_range"] == 5


def test_build_salary_insight_record_uses_python_types():
    stats = sample_statistics()

    record = build_salary_insight_record(stats)

    for key, value in record.items():
        assert type(value) in (int, float)


def test_save_salary_insights(session):
    stats = sample_statistics()

    record = build_salary_insight_record(stats)

    insight = save_salary_insights(
        session,
        record,
        analysis_version="2.3",
    )

    session.commit()

    assert isinstance(insight, SalaryInsight)

    assert insight.id is not None

    assert insight.job_count == 5
    assert insight.salary_count == 5

    assert insight.median_salary == 55000.0
    assert insight.mean_salary == 55000.0

    assert insight.analysis_version == "2.3"

    assert isinstance(insight.created_at, datetime)


def test_salary_insight_is_persisted(session):
    stats = sample_statistics()

    record = build_salary_insight_record(stats)

    insight = save_salary_insights(
        session,
        record,
        analysis_version="2.3",
    )

    session.commit()

    stored = session.get(SalaryInsight, insight.id)

    assert stored is not None
    assert stored.id == insight.id
    assert stored.median_salary == 55000.0
    assert stored.analysis_version == "2.3"


def test_multiple_analysis_snapshots_are_preserved(session):
    stats = sample_statistics()

    record = build_salary_insight_record(stats)

    first = save_salary_insights(
        session,
        record,
        analysis_version="2.3",
    )

    second = save_salary_insights(
        session,
        record,
        analysis_version="2.3",
    )

    session.commit()

    assert first.id != second.id

    stored = session.query(SalaryInsight).order_by(SalaryInsight.id).all()

    assert len(stored) == 2

    assert stored[0].created_at is not None
    assert stored[1].created_at is not None

    assert stored[0].analysis_version == "2.3"
    assert stored[1].analysis_version == "2.3"
