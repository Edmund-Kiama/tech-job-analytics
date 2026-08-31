from pathlib import Path

import pytest

from data_pipeline.database.connection import SessionLocal
from data_pipeline.database.models import Listing, SalaryInsight
from data_pipeline.services.pipeline import run_pipeline


@pytest.fixture(autouse=True)
def mock_bronze_dir(monkeypatch, tmp_path):
    """Automatically redirects BRONZE_DIR to a temporary folder for every test."""
    test_bronze = tmp_path / "test_bronze"
    monkeypatch.setattr("data_pipeline.storage.raw.BRONZE_DIR", test_bronze)
    return test_bronze


@pytest.fixture(autouse=True)
def clean_pipeline_database():
    with SessionLocal() as session:
        session.query(SalaryInsight).delete()
        session.query(Listing).delete()
        session.commit()


def test_complete_pipeline(monkeypatch, tmp_path):
    """
    Verify the complete API -> Bronze -> Pandas -> NumPy -> SQLite flow.
    """

    fake_jobs = [
        {
            "id": "pipeline-1",
            "title": "Python Developer",
            "description": "Python backend developer",
            "created": "2026-08-29T10:00:00Z",
            "redirect_url": "https://example.com/job/1",
            "salary_min": 40000,
            "salary_max": 60000,
            "salary_is_predicted": "0",
            "contract_time": "full_time",
            "contract_type": None,
            "company": {
                "display_name": "Test Company",
            },
            "category": {
                "label": "IT Jobs",
                "tag": "it-jobs",
            },
            "location": {
                "display_name": "London",
                "area": [
                    "UK",
                    "England",
                    "London",
                ],
            },
            "latitude": 51.5074,
            "longitude": -0.1278,
            "adref": "test-1",
            "__CLASS__": "Adzuna::API::Response::Job",
        },
        {
            "id": "pipeline-2",
            "title": "Data Engineer",
            "description": "Data engineering role",
            "created": "2026-08-29T10:00:00Z",
            "redirect_url": "https://example.com/job/2",
            "salary_min": 50000,
            "salary_max": 70000,
            "salary_is_predicted": "0",
            "contract_time": "full_time",
            "contract_type": None,
            "company": {
                "display_name": "Another Company",
            },
            "category": {
                "label": "IT Jobs",
                "tag": "it-jobs",
            },
            "location": {
                "display_name": "Manchester",
                "area": [
                    "UK",
                    "England",
                    "Manchester",
                ],
            },
            "latitude": 53.4808,
            "longitude": -2.2426,
            "adref": "test-2",
            "__CLASS__": "Adzuna::API::Response::Job",
        },
    ]

    class FakeClient:
        def iter_pages(self, max_pages=3, max_jobs=None):
            yield {
                "page": 1,
                "results": fake_jobs,
                "count": len(fake_jobs),
            }

    monkeypatch.setattr(
        "data_pipeline.services.pipeline.AdzunaClient",
        FakeClient,
    )

    result = run_pipeline(
        max_pages=1,
        analysis_version="2.3-test",
    )

    assert result["rows_before_cleaning"] == 2
    assert result["rows_after_cleaning"] == 2
    assert result["listing_count"] == 2

    assert result["salary_insight_id"] is not None
    assert result["analysis_version"] == "2.3-test"

    assert Path(result["bronze_path"]).exists()

    with SessionLocal() as session:
        listings = session.query(Listing).all()

        assert len(listings) == 2

        ids = {listing.id for listing in listings}

        assert ids == {
            "pipeline-1",
            "pipeline-2",
        }

        insights = session.query(SalaryInsight).all()

        assert len(insights) == 1

        insight = insights[0]

        assert insight.job_count == 2
        assert insight.salary_count == 2

        assert insight.median_salary is not None
        assert insight.mean_salary is not None

        assert insight.analysis_version == "2.3-test"
        assert insight.created_at is not None


def test_pipeline_is_idempotent(monkeypatch):
    """
    Running the pipeline twice with the same jobs must not create
    duplicate Listing records.
    """

    fake_jobs = [
        {
            "id": "idempotent-1",
            "title": "Backend Developer",
            "description": "Backend role",
            "created": "2026-08-29T10:00:00Z",
            "redirect_url": "https://example.com/job/1",
            "salary_min": 40000,
            "salary_max": 60000,
            "salary_is_predicted": "0",
            "contract_time": "full_time",
            "contract_type": None,
            "company": {
                "display_name": "Test Company",
            },
            "category": {
                "label": "IT Jobs",
                "tag": "it-jobs",
            },
            "location": {
                "display_name": "London",
                "area": [
                    "UK",
                    "England",
                    "London",
                ],
            },
            "latitude": 51.5074,
            "longitude": -0.1278,
            "adref": "test-idempotent",
            "__CLASS__": "Adzuna::API::Response::Job",
        }
    ]

    class FakeClient:
        def iter_pages(self, max_pages=3, max_jobs=None):
            yield {
                "page": 1,
                "results": fake_jobs,
                "count": len(fake_jobs),
            }

    monkeypatch.setattr(
        "data_pipeline.services.pipeline.AdzunaClient",
        FakeClient,
    )

    run_pipeline(
        max_pages=1,
        analysis_version="2.3-test",
    )

    run_pipeline(
        max_pages=1,
        analysis_version="2.3-test",
    )

    with SessionLocal() as session:
        listings = session.query(Listing).all()

        assert len(listings) == 1

        assert listings[0].id == "idempotent-1"


def test_pipeline_creates_analysis_snapshot_each_run(monkeypatch):
    """
    Listings are idempotent, but salary analytics are snapshots.
    Therefore each pipeline execution should create a new insight.
    """

    fake_jobs = [
        {
            "id": "snapshot-1",
            "title": "Data Scientist",
            "description": "Data science role",
            "created": "2026-08-29T10:00:00Z",
            "redirect_url": "https://example.com/job/1",
            "salary_min": 50000,
            "salary_max": 70000,
            "salary_is_predicted": "0",
            "contract_time": "full_time",
            "contract_type": None,
            "company": {
                "display_name": "Test Company",
            },
            "category": {
                "label": "IT Jobs",
                "tag": "it-jobs",
            },
            "location": {
                "display_name": "London",
                "area": [
                    "UK",
                    "England",
                    "London",
                ],
            },
            "latitude": 51.5074,
            "longitude": -0.1278,
            "adref": "test-snapshot",
            "__CLASS__": "Adzuna::API::Response::Job",
        }
    ]

    class FakeClient:
        def iter_pages(self, max_pages=3, max_jobs=None):
            yield {
                "page": 1,
                "results": fake_jobs,
                "count": len(fake_jobs),
            }

    monkeypatch.setattr(
        "data_pipeline.services.pipeline.AdzunaClient",
        FakeClient,
    )

    run_pipeline(
        max_pages=1,
        analysis_version="2.3-test",
    )

    run_pipeline(
        max_pages=1,
        analysis_version="2.3-test",
    )

    with SessionLocal() as session:
        insights = session.query(SalaryInsight).all()

        assert len(insights) == 2

        assert insights[0].id != insights[1].id

        assert all(insight.analysis_version == "2.3-test" for insight in insights)

        assert all(insight.created_at is not None for insight in insights)
