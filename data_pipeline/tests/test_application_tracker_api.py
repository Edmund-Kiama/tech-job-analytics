from datetime import datetime, timedelta, timezone

from data_pipeline.database.connection import engine
from data_pipeline.database.models import Base, Listing


def seed_application_job():
    Base.metadata.create_all(bind=engine)

    now = datetime.now(timezone.utc)

    with engine.begin() as connection:
        connection.exec_driver_sql(
            """
            INSERT OR REPLACE INTO listings (
                id,
                title,
                description,
                created,
                redirect_url,
                salary_min,
                salary_max,
                salary_is_predicted,
                contract_time,
                contract_type,
                company_name,
                category_label,
                category_tag,
                location_name,
                country,
                region,
                city,
                latitude,
                longitude,
                salary_currency,
                salary_period,
                normalized_salary_min,
                normalized_salary_max,
                normalized_salary_midpoint,
                first_seen_at,
                last_seen_at,
                is_active,
                application_status,
                saved_at,
                applied_at,
                follow_up_at,
                user_priority,
                application_notes
            )
            VALUES (
                'application-test-job',
                'Data Scientist',
                'Test job',
                '2026-08-01',
                'https://example.com/apply',
                50000,
                70000,
                0,
                'full_time',
                'permanent',
                'Test Company',
                'IT jobs',
                'it',
                'Birmingham',
                'gb',
                'West Midlands',
                'Birmingham',
                NULL,
                NULL,
                'GBP',
                'year',
                50000,
                70000,
                60000,
                ?,
                ?,
                1,
                'NEW',
                NULL,
                NULL,
                NULL,
                NULL,
                NULL
            )
            """,
            (now, now),
        )


def test_application_defaults_to_new(client):
    seed_application_job()

    response = client.get("/jobs/application-test-job/application")

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == "application-test-job"
    assert data["application_status"] == "NEW"
    assert data["saved_at"] is None
    assert data["applied_at"] is None
    assert data["follow_up_at"] is None
    assert data["user_priority"] is None
    assert data["application_notes"] is None


def test_save_job_sets_saved_timestamp(client):
    seed_application_job()

    response = client.patch(
        "/jobs/application-test-job/application",
        json={
            "application_status": "SAVED",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["application_status"] == "SAVED"
    assert data["saved_at"] is not None
    assert data["applied_at"] is None


def test_apply_job_sets_applied_timestamp(client):
    seed_application_job()

    response = client.patch(
        "/jobs/application-test-job/application",
        json={
            "application_status": "APPLIED",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["application_status"] == "APPLIED"
    assert data["applied_at"] is not None


def test_applied_timestamp_is_not_erased(client):
    seed_application_job()

    response = client.patch(
        "/jobs/application-test-job/application",
        json={
            "application_status": "APPLIED",
        },
    )

    assert response.status_code == 200

    first_applied_at = response.json()["applied_at"]

    response = client.patch(
        "/jobs/application-test-job/application",
        json={
            "application_status": "INTERVIEW",
        },
    )

    assert response.status_code == 200

    assert response.json()["applied_at"] == first_applied_at


def test_application_priority_notes_and_follow_up(client):
    seed_application_job()

    follow_up = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

    response = client.patch(
        "/jobs/application-test-job/application",
        json={
            "application_status": "SAVED",
            "user_priority": 3,
            "follow_up_at": follow_up,
            "application_notes": "Strong match. Prepare CV.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["application_status"] == "SAVED"
    assert data["user_priority"] == 3
    assert data["follow_up_at"] is not None
    assert data["application_notes"] == "Strong match. Prepare CV."


def test_invalid_application_status_returns_422(client):
    seed_application_job()

    response = client.patch(
        "/jobs/application-test-job/application",
        json={
            "application_status": "INVALID",
        },
    )

    assert response.status_code == 422


def test_invalid_priority_returns_422(client):
    seed_application_job()

    response = client.patch(
        "/jobs/application-test-job/application",
        json={
            "user_priority": 4,
        },
    )

    assert response.status_code == 422


def test_applications_endpoint_returns_tracked_jobs(client):
    seed_application_job()

    client.patch(
        "/jobs/application-test-job/application",
        json={
            "application_status": "APPLIED",
            "user_priority": 3,
        },
    )

    response = client.get("/applications")

    assert response.status_code == 200

    data = response.json()

    matching = [item for item in data if item["id"] == "application-test-job"]

    assert len(matching) == 1

    job = matching[0]

    assert job["application_status"] == "APPLIED"
    assert job["user_priority"] == 3


def test_applications_status_filter(client):
    seed_application_job()

    client.patch(
        "/jobs/application-test-job/application",
        json={
            "application_status": "INTERVIEW",
        },
    )

    response = client.get("/applications?status=INTERVIEW")

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1

    assert all(item["application_status"] == "INTERVIEW" for item in data)


def test_applications_priority_filter(client):
    seed_application_job()

    client.patch(
        "/jobs/application-test-job/application",
        json={
            "application_status": "SAVED",
            "user_priority": 3,
        },
    )

    response = client.get("/applications?priority=3")

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1

    assert all(item["user_priority"] == 3 for item in data)


def test_application_job_not_found(client):
    response = client.get("/jobs/does-not-exist/application")

    assert response.status_code == 404
