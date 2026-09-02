import pytest

from data_pipeline.database.connection import SessionLocal, engine
from data_pipeline.database.models import (
    Base,
    IngestionRun,
    Listing,
    ListingHistory,
    SalaryInsight,
)
from data_pipeline.services.pipeline import run_pipeline


@pytest.fixture(autouse=True)
def clean_test_database():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        session.query(ListingHistory).delete()
        session.query(IngestionRun).delete()
        session.query(SalaryInsight).delete()
        session.query(Listing).delete()

        session.commit()

    yield


def make_job(
    job_id,
    title="Backend Developer",
    salary_min=40000,
    salary_max=60000,
):
    return {
        "id": job_id,
        "title": title,
        "description": "Test job description",
        "created": "2026-08-29T10:00:00Z",
        "redirect_url": f"https://example.com/jobs/{job_id}",
        "salary_min": salary_min,
        "salary_max": salary_max,
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
        "adref": f"test-{job_id}",
        "__CLASS__": "Adzuna::API::Response::Job",
    }


def test_ingestion_run_is_created(monkeypatch):
    fake_jobs = [
        make_job("job-1"),
        make_job("job-2"),
    ]

    class FakeClient:
        def iter_jobs(self, max_pages=3):
            return iter(fake_jobs)

    monkeypatch.setattr(
        "data_pipeline.services.pipeline.AdzunaClient",
        FakeClient,
    )

    result = run_pipeline(
        max_pages=1,
        analysis_version="2.3-test",
    )

    assert result["ingestion_run_id"] is not None

    with SessionLocal() as session:
        run = session.query(IngestionRun).first()

        assert run is not None
        assert run.status == "success"

        assert run.rows_fetched == 2

        assert run.jobs_inserted == 2
        assert run.jobs_updated == 0
        assert run.jobs_inactivated == 0

        assert run.completed_at is not None
        assert run.salary_insight_id is not None


def test_second_ingestion_updates_existing_jobs(monkeypatch):
    fake_jobs = [
        make_job("job-1"),
        make_job("job-2"),
    ]

    class FakeClient:
        def iter_jobs(self, max_pages=3):
            return iter(fake_jobs)

    monkeypatch.setattr(
        "data_pipeline.services.pipeline.AdzunaClient",
        FakeClient,
    )

    # First ingestion
    first_result = run_pipeline(
        max_pages=1,
        analysis_version="2.3-test",
    )

    # Second ingestion
    second_result = run_pipeline(
        max_pages=1,
        analysis_version="2.3-test",
    )

    assert first_result["jobs_inserted"] == 2
    assert first_result["jobs_updated"] == 0

    assert second_result["jobs_inserted"] == 0
    assert second_result["jobs_updated"] == 2

    with SessionLocal() as session:
        assert session.query(Listing).count() == 2

        assert session.query(IngestionRun).count() == 2

        assert session.query(ListingHistory).count() == 4


def test_missing_job_becomes_inactive(monkeypatch):
    first_jobs = [
        make_job("job-1"),
        make_job("job-2"),
        make_job("job-3"),
    ]

    second_jobs = [
        make_job("job-1"),
        make_job("job-2"),
    ]

    class FakeClient:
        calls = 0

        def iter_jobs(self, max_pages=3):
            # Mutate class attribute so state persists across new FakeClient() instantiations
            FakeClient.calls += 1

            if FakeClient.calls == 1:
                return iter(first_jobs)

            return iter(second_jobs)

    monkeypatch.setattr(
        "data_pipeline.services.pipeline.AdzunaClient",
        FakeClient,
    )

    first_result = run_pipeline(
        max_pages=1,
        analysis_version="2.3-test",
    )

    second_result = run_pipeline(
        max_pages=1,
        analysis_version="2.3-test",
    )

    assert first_result["jobs_inserted"] == 3

    assert second_result["jobs_inserted"] == 0
    assert second_result["jobs_updated"] == 2
    assert second_result["jobs_inactivated"] == 1

    with SessionLocal() as session:
        job_1 = session.get(Listing, "job-1")
        job_2 = session.get(Listing, "job-2")
        job_3 = session.get(Listing, "job-3")

        assert job_1.is_active is True
        assert job_2.is_active is True

        assert job_3.is_active is False
        assert job_3.inactive_at is not None


def test_salary_changes_are_preserved_in_history(monkeypatch):
    first_jobs = [
        make_job(
            "job-1",
            salary_min=50000,
            salary_max=60000,
        )
    ]

    second_jobs = [
        make_job(
            "job-1",
            salary_min=70000,
            salary_max=80000,
        )
    ]

    class FakeClient:
        calls = 0

        def iter_jobs(self, max_pages=3):
            # Mutate class attribute so state persists across new FakeClient() instantiations
            FakeClient.calls += 1

            if FakeClient.calls == 1:
                return iter(first_jobs)

            return iter(second_jobs)

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
        history = (
            session.query(ListingHistory)
            .filter(ListingHistory.listing_id == "job-1")
            .order_by(ListingHistory.observed_at)
            .all()
        )

        assert len(history) == 2

        assert history[0].salary_min == 50000
        assert history[0].salary_max == 60000

        assert history[1].salary_min == 70000
        assert history[1].salary_max == 80000


def test_failed_ingestion_is_recorded(monkeypatch):
    class FakeClient:
        def iter_jobs(self, max_pages=3):
            raise RuntimeError("Adzuna API unavailable")

    monkeypatch.setattr(
        "data_pipeline.services.pipeline.AdzunaClient",
        FakeClient,
    )

    with pytest.raises(RuntimeError, match="Adzuna API unavailable"):
        run_pipeline(
            max_pages=1,
            analysis_version="2.3-test",
        )

    with SessionLocal() as session:
        run = (
            session.query(IngestionRun).order_by(IngestionRun.started_at.desc()).first()
        )

        assert run is not None
        assert run.status == "failed"

        assert run.completed_at is not None

        assert run.error_message == ("Adzuna API unavailable")
