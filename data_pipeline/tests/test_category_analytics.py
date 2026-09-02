import pytest
from fastapi.testclient import TestClient

from backend.main import app
from data_pipeline.database.connection import SessionLocal, engine
from data_pipeline.database.models import Base, Listing


@pytest.fixture(autouse=True)
def clean_test_database():
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        session.query(Listing).delete()
        session.commit()

    yield

    with SessionLocal() as session:
        session.query(Listing).delete()
        session.commit()


@pytest.fixture
def client():
    return TestClient(app)


def make_listing(
    job_id,
    category,
    salary,
    active=True,
):
    return Listing(
        id=job_id,
        title=f"Job {job_id}",
        description="Test job",
        created="2026-08-29T10:00:00Z",
        company_name="Test Company",
        category_label=category,
        category_tag=category.lower().replace(" ", "-"),
        location_name="London",
        country="UK",
        region="England",
        city="London",
        salary_min=salary,
        salary_max=salary,
        salary_is_predicted=False,
        salary_currency="GBP",
        salary_period="annual",
        normalized_salary_min=salary,
        normalized_salary_max=salary,
        normalized_salary_midpoint=salary,
        is_active=active,
    )


def test_get_categories(client):
    with SessionLocal() as session:
        session.add_all(
            [
                make_listing("1", "IT Jobs", 50000),
                make_listing("2", "IT Jobs", 60000),
                make_listing("3", "Engineering Jobs", 55000),
            ]
        )
        session.commit()

    response = client.get("/analytics/categories")

    assert response.status_code == 200

    data = response.json()

    assert data["categories"] == [
        "Engineering Jobs",
        "IT Jobs",
    ]


def test_get_category_analytics(client):
    with SessionLocal() as session:
        session.add_all(
            [
                make_listing("1", "IT Jobs", 50000),
                make_listing("2", "IT Jobs", 60000),
                make_listing("3", "IT Jobs", 70000),
            ]
        )
        session.commit()

    response = client.get("/analytics/categories/IT%20Jobs")

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "IT Jobs"
    assert data["job_count"] == 3

    assert data["salary"]["mean"] == 60000
    assert data["salary"]["median"] == 60000
    assert data["salary"]["minimum"] == 50000
    assert data["salary"]["maximum"] == 70000

    assert len(data["top_jobs"]) == 3

    assert data["top_jobs"][0]["salary"] == 70000
    assert data["top_jobs"][1]["salary"] == 60000
    assert data["top_jobs"][2]["salary"] == 50000


def test_category_excludes_inactive_jobs(client):
    with SessionLocal() as session:
        session.add_all(
            [
                make_listing("1", "IT Jobs", 50000, active=True),
                make_listing("2", "IT Jobs", 90000, active=False),
            ]
        )
        session.commit()

    response = client.get("/analytics/categories/IT%20Jobs")

    assert response.status_code == 200

    data = response.json()

    assert data["job_count"] == 1
    assert data["salary"]["maximum"] == 50000


def test_unknown_category_returns_404(client):
    response = client.get("/analytics/categories/Does%20Not%20Exist")

    assert response.status_code == 404
