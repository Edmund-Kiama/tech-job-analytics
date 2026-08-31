from datetime import datetime, timedelta

from data_pipeline.database.connection import SessionLocal
from data_pipeline.database.models import Listing
from data_pipeline.database.scheduler.job_lifecycle import (
    mark_stale_listings,
)


def make_job(job_id, title="Python Developer"):
    return {
        "id": job_id,
        "title": title,
        "description": "Test job",
        "created": "2026-08-30T10:00:00Z",
        "redirect_url": f"https://example.com/{job_id}",
        "salary_min": 50000,
        "salary_max": 70000,
        "salary_is_predicted": False,
        "contract_time": "full_time",
        "contract_type": None,
        "company_name": "Test Company",
        "category_label": "IT Jobs",
        "category_tag": "it-jobs",
        "location_name": "London",
        "country": "UK",
        "region": "England",
        "city": "London",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "salary_currency": "GBP",
        "salary_period": "annual",
        "normalized_salary_min": 50000,
        "normalized_salary_max": 70000,
        "normalized_salary_midpoint": 60000,
    }


def test_new_job_tracking():
    seen_at = datetime(2026, 8, 3, 10, 0, 0)

    with SessionLocal() as session:
        job = Listing(
            **make_job("tracking-new"),
            last_seen_at=seen_at,
            first_seen_at=seen_at,
            is_active=True,
            inactive_at=None,
        )

        session.add(job)
        session.commit()

        saved = session.get(
            Listing,
            "tracking-new",
        )

        assert saved is not None
        assert saved.first_seen_at == seen_at
        assert saved.last_seen_at == seen_at
        assert saved.is_active is True
        assert saved.inactive_at is None

        session.delete(saved)
        session.commit()


def test_stale_job_becomes_inactive():
    now = datetime(2026, 8, 3, 10, 0, 0)

    old_seen = now - timedelta(days=10)

    with SessionLocal() as session:
        job = Listing(
            **make_job("tracking-stale"),
            first_seen_at=old_seen,
            last_seen_at=old_seen,
            is_active=True,
            inactive_at=None,
        )

        session.add(job)
        session.commit()

        count = mark_stale_listings(
            session,
            stale_after_days=7,
            now=now,
        )

        session.commit()

        assert count == 1

        saved = session.get(
            Listing,
            "tracking-stale",
        )

        assert saved.is_active is False
        assert saved.inactive_at == now

        session.delete(saved)
        session.commit()
