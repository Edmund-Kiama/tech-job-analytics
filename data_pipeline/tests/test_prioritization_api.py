from sqlalchemy import text


def _seed_test_job(client):
    """Seed 'test-job' into the listings database table if not present."""
    session = None

    # Attempt to locate the database session from application modules
    for mod_name in [
        "data_pipeline.db",
        "data_pipeline.database",
        "data_pipeline.db.session",
        "data_pipeline.db.database",
        "data_pipeline.models",
    ]:
        try:
            mod = __import__(mod_name, fromlist=["SessionLocal", "engine", "get_db"])
            if hasattr(mod, "get_db"):
                gen = mod.get_db()
                if hasattr(gen, "__next__"):
                    session = next(gen)
                    break
            elif hasattr(mod, "SessionLocal"):
                session = mod.SessionLocal()
                break
            elif hasattr(mod, "engine"):
                from sqlalchemy.orm import sessionmaker

                session = sessionmaker(bind=mod.engine)()
                break
        except Exception:
            continue

    # Fallback to inspecting route dependencies on the FastAPI app instance
    if session is None and hasattr(client, "app"):
        for route in getattr(client.app, "routes", []):
            dependant = getattr(route, "dependant", None)
            if dependant:
                for dep in dependant.dependencies:
                    try:
                        res = dep.call()
                        if hasattr(res, "__next__"):
                            session = next(res)
                            break
                        elif hasattr(res, "execute"):
                            session = res
                            break
                    except Exception:
                        continue
                if session:
                    break

    # Insert test record into the listings table
    if session is not None:
        try:
            session.execute(
                text(
                    """
                    INSERT OR REPLACE INTO listings (
                        id, title, category_label, location_name, contract_type, is_active
                    ) VALUES (
                        'test-job', 'Data Scientist', 'IT jobs', 'Birmingham', 'permanent', 1
                    )
                    """
                )
            )
            if hasattr(session, "commit"):
                session.commit()
        except Exception:
            if hasattr(session, "rollback"):
                session.rollback()


def test_prioritization_endpoint_returns_score(client):
    _seed_test_job(client)

    response = client.get(
        "/analytics/prioritization/test-job"
        "?target_titles=Data%20Scientist"
        "&preferred_categories=IT%20jobs"
        "&preferred_locations=Birmingham"
        "&preferred_contract_types=permanent"
    )

    assert response.status_code == 200

    data = response.json()

    assert "job" in data
    assert "priority_score" in data
    assert "priority" in data
    assert "factors" in data
    assert "explanation" in data


def test_prioritization_endpoint_returns_404_for_missing_job(
    client,
):
    response = client.get("/analytics/prioritization/non-existent-job")

    assert response.status_code == 404


def test_ranked_prioritization_returns_jobs(client):
    response = client.get(
        "/analytics/prioritization"
        "?target_titles=Data%20Scientist"
        "&preferred_categories=IT%20jobs"
        "&preferred_locations=Birmingham"
        "&preferred_contract_types=permanent"
    )

    assert response.status_code == 200

    data = response.json()

    assert "jobs" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
