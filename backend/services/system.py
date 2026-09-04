from sqlalchemy.orm import Session

from data_pipeline.database.models import IngestionRun, Listing


def health(session: Session) -> dict:
    listings_count = session.query(Listing).count()
    latest_ingestion = (
        session.query(Listing.last_seen_at)
        .order_by(Listing.last_seen_at.desc())
        .first()
    )
    return {
        "status": "ok",
        "database": "ok",
        "listings": listings_count,
        "latest_ingestion": latest_ingestion[0] if latest_ingestion else None,
    }


def ingestion_status(session: Session) -> dict:
    latest_run = (
        session.query(IngestionRun).order_by(IngestionRun.started_at.desc()).first()
    )
    active_jobs = session.query(Listing).filter(Listing.is_active.is_(True)).count()
    inactive_jobs = session.query(Listing).filter(Listing.is_active.is_(False)).count()
    total_jobs = session.query(Listing).count()

    jobs = {"total": total_jobs, "active": active_jobs, "inactive": inactive_jobs}
    if latest_run is None:
        return {"status": "never_run", "last_run": None, "jobs": jobs}

    return {
        "status": latest_run.status,
        "last_run": latest_run.started_at,
        "completed_at": latest_run.completed_at,
        "ingestion_run_id": latest_run.id,
        "rows_fetched": latest_run.rows_fetched,
        "rows_before_cleaning": latest_run.rows_before_cleaning,
        "rows_after_cleaning": latest_run.rows_after_cleaning,
        "jobs_inserted": latest_run.jobs_inserted,
        "jobs_updated": latest_run.jobs_updated,
        "jobs_inactivated": latest_run.jobs_inactivated,
        "salary_insight_id": latest_run.salary_insight_id,
        "analysis_version": latest_run.analysis_version,
        "bronze_path": latest_run.bronze_path,
        "error_message": latest_run.error_message,
        "jobs": jobs,
    }


def ingestion_runs(session: Session, page: int, page_size: int) -> dict:
    total = session.query(IngestionRun).count()
    runs = (
        session.query(IngestionRun)
        .order_by(IngestionRun.started_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return {
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
        "runs": [
            {
                "id": run.id,
                "started_at": run.started_at,
                "completed_at": run.completed_at,
                "status": run.status,
                "rows_fetched": run.rows_fetched,
                "rows_before_cleaning": run.rows_before_cleaning,
                "rows_after_cleaning": run.rows_after_cleaning,
                "jobs_inserted": run.jobs_inserted,
                "jobs_updated": run.jobs_updated,
                "jobs_inactivated": run.jobs_inactivated,
                "salary_insight_id": run.salary_insight_id,
                "bronze_path": run.bronze_path,
                "analysis_version": run.analysis_version,
                "error_message": run.error_message,
            }
            for run in runs
        ],
    }
