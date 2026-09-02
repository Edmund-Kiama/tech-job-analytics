from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from data_pipeline.clients.adzuna import AdzunaClient
from data_pipeline.config import settings
from data_pipeline.database.connection import SessionLocal
from data_pipeline.database.models import IngestionRun, Listing, ListingHistory
from data_pipeline.database.scheduler.job_lifecycle import (
    mark_stale_listings,
)
from data_pipeline.processing.statistics import (
    build_salary_insight_record,
    calculate_salary_statistics,
)
from data_pipeline.processing.transform import transform_dataframe
from data_pipeline.services.salary_insights import save_salary_insights
from data_pipeline.storage.bronze_loader import load_bronze_json
from data_pipeline.storage.raw import save_raw_payload


def run_pipeline(
    max_pages: Optional[int] = None,
    analysis_version: Optional[str] = None,
) -> dict:
    """
    Run the complete data pipeline with ingestion tracking.

    Flow:
        Adzuna API
            ↓
        Bronze JSON
            ↓
        Pandas
            ↓
        SQLite listings
            ↓
        ListingHistory
            ↓
        NumPy statistics
            ↓
        SalaryInsight
            ↓
        IngestionRun completion
    """
    effective_max_pages = (
        max_pages
        if max_pages is not None
        else int(getattr(settings, "ADZUNA_MAX_PAGES", 3))
    )
    effective_analysis_version = (
        analysis_version
        if analysis_version is not None
        else getattr(settings, "ANALYSIS_VERSION", "2.3")
    )

    started_at = datetime.now(timezone.utc)

    # 1. Create ingestion run
    with SessionLocal() as session:
        ingestion_run = create_ingestion_run(
            session=session,
            started_at=started_at,
            analysis_version=effective_analysis_version,
        )
        ingestion_run_id = ingestion_run.id
        session.commit()

    try:
        # 2. Extract from Adzuna
        client = AdzunaClient()
        jobs = []

        max_jobs_setting = getattr(settings, "ADZUNA_MAX_JOBS", None)
        max_jobs = int(max_jobs_setting) if max_jobs_setting is not None else None

        # Call iter_jobs using only valid keyword arguments
        if hasattr(client, "iter_jobs"):
            job_iterable = client.iter_jobs(max_pages=effective_max_pages)
        elif hasattr(client, "iter_pages"):
            pages = client.iter_pages(max_pages=effective_max_pages)
            job_iterable = (job for page in pages for job in page.get("results", []))
        else:
            job_iterable = []

        for job in job_iterable:
            jobs.append(job)
            if max_jobs and len(jobs) >= max_jobs:
                break

        if not jobs:
            raise ValueError("Adzuna API returned no jobs.")

        rows_fetched = len(jobs)
        payload = {
            "results": jobs,
            "count": rows_fetched,
        }

        # 3. Store immutable Bronze snapshot
        bronze_path = save_raw_payload(payload)

        # 4. Load Bronze
        df = load_bronze_json(bronze_path)
        rows_before_cleaning = len(df)

        # 5. Clean / transform
        cleaned_df = transform_dataframe(df)
        rows_after_cleaning = len(cleaned_df)

        seen_at = datetime.now(timezone.utc)

        # 6. Persist listings + history
        with SessionLocal() as session:
            stale_days = int(getattr(settings, "ADZUNA_STALE_AFTER_DAYS", 14))

            sync_result = _save_cleaned_listings(
                session=session,
                dataframe=cleaned_df,
                ingestion_run_id=ingestion_run_id,
                seen_at=seen_at,
                stale_after_days=stale_days,
            )

            # 7. Calculate salary statistics
            salary_stats = calculate_salary_statistics(cleaned_df)
            flat_stats = _prepare_insight_stats(cleaned_df, salary_stats)
            salary_insight_record = build_salary_insight_record(flat_stats)

            # 8. Save salary analytics snapshot
            salary_insight = save_salary_insights(
                session=session,
                insights=salary_insight_record,
                analysis_version=effective_analysis_version,
            )

            # 9. Complete ingestion run
            ingestion_run = session.execute(
                select(IngestionRun).where(IngestionRun.id == ingestion_run_id)
            ).scalar_one()

            ingestion_run.completed_at = datetime.now(timezone.utc)
            ingestion_run.status = "success"
            ingestion_run.rows_fetched = rows_fetched
            ingestion_run.rows_before_cleaning = rows_before_cleaning
            ingestion_run.rows_after_cleaning = rows_after_cleaning
            ingestion_run.jobs_inserted = sync_result["inserted"]
            ingestion_run.jobs_updated = sync_result["updated"]
            ingestion_run.jobs_inactivated = sync_result["inactivated"]
            ingestion_run.salary_insight_id = salary_insight.id
            ingestion_run.bronze_path = str(bronze_path)

            session.commit()

            return {
                "ingestion_run_id": ingestion_run.id,
                "status": ingestion_run.status,
                "bronze_path": Path(bronze_path),
                "rows_fetched": rows_fetched,
                "rows_before_cleaning": rows_before_cleaning,
                "rows_after_cleaning": rows_after_cleaning,
                "listing_count": rows_after_cleaning,
                "jobs_inserted": sync_result["inserted"],
                "jobs_updated": sync_result["updated"],
                "jobs_inactivated": sync_result["inactivated"],
                "salary_insight_id": salary_insight.id,
                "analysis_version": effective_analysis_version,
            }

    except Exception as exc:
        # Record failed ingestion run
        with SessionLocal() as session:
            ingestion_run = session.execute(
                select(IngestionRun).where(IngestionRun.id == ingestion_run_id)
            ).scalar_one_or_none()

            if ingestion_run is not None:
                ingestion_run.completed_at = datetime.now(timezone.utc)
                ingestion_run.status = "failed"
                ingestion_run.error_message = str(exc)
                session.commit()

        raise


def _save_cleaned_listings(
    session: Session,
    dataframe: pd.DataFrame,
    ingestion_run_id: int,
    seen_at: datetime,
    stale_after_days: Optional[int] = None,
) -> dict:
    """
    Synchronize cleaned jobs into SQLite.

    Returns:
        inserted: number of new listings
        updated: number of existing listings
        inactivated: number of listings marked inactive/stale
    """
    # Deduplicate incoming dataframe by ID before processing
    if not dataframe.empty and "id" in dataframe.columns:
        dataframe = dataframe.drop_duplicates(subset=["id"], keep="last")

    records = dataframe.to_dict(orient="records")
    incoming_ids = {record["id"] for record in records} if records else set()

    inserted = 0
    updated = 0

    if incoming_ids:
        # Bulk-fetch existing listings to prevent N+1 queries
        existing_listings = {
            listing.id: listing
            for listing in session.execute(
                select(Listing).where(Listing.id.in_(incoming_ids))
            )
            .scalars()
            .all()
        }
    else:
        existing_listings = {}

    for record in records:
        record.pop("company", None)
        record.pop("category", None)
        record.pop("location", None)
        record.pop("__CLASS__", None)

        clean_record = {}
        for key, val in record.items():
            if pd.isna(val):
                clean_record[key] = None
            elif isinstance(val, pd.Timestamp):
                clean_record[key] = val.to_pydatetime()
            else:
                clean_record[key] = val

        job_id = clean_record["id"]
        existing = existing_listings.get(job_id)

        if existing is None:
            listing = Listing(
                **clean_record,
                first_seen_at=seen_at,
                last_seen_at=seen_at,
                is_active=True,
                inactive_at=None,
            )
            session.add(listing)
            existing_listings[job_id] = (
                listing  # Store in map to prevent duplicate inserts
            )
            inserted += 1
        else:
            for field, value in clean_record.items():
                setattr(existing, field, value)

            existing.last_seen_at = seen_at
            existing.is_active = True
            existing.inactive_at = None
            updated += 1

        listing_snapshot = ListingHistory(
            listing_id=job_id,
            ingestion_run_id=ingestion_run_id,
            observed_at=seen_at,
            title=clean_record.get("title"),
            salary_min=clean_record.get("salary_min"),
            salary_max=clean_record.get("salary_max"),
            salary_is_predicted=clean_record.get("salary_is_predicted"),
            normalized_salary_min=clean_record.get("normalized_salary_min"),
            normalized_salary_max=clean_record.get("normalized_salary_max"),
            normalized_salary_midpoint=clean_record.get("normalized_salary_midpoint"),
            contract_time=clean_record.get("contract_time"),
            contract_type=clean_record.get("contract_type"),
            company_name=clean_record.get("company_name"),
            category_label=clean_record.get("category_label"),
            category_tag=clean_record.get("category_tag"),
            location_name=clean_record.get("location_name"),
            is_active=True,
        )
        session.add(listing_snapshot)

    # Inactivate listings missing from this run
    active_listings = (
        session.execute(select(Listing).where(Listing.is_active.is_(True)))
        .scalars()
        .all()
    )

    inactivated = 0
    for listing in active_listings:
        if listing.id not in incoming_ids:
            listing.is_active = False
            listing.inactive_at = seen_at
            inactivated += 1

    # Time-decay check for any additional stale listings
    if stale_after_days is not None:
        extra_inactivated = mark_stale_listings(
            session=session,
            stale_after_days=stale_after_days,
            now=seen_at,
        )
        if isinstance(extra_inactivated, int):
            inactivated += extra_inactivated

    session.flush()

    return {
        "inserted": inserted,
        "updated": updated,
        "inactivated": inactivated,
    }


def _prepare_insight_stats(df: pd.DataFrame, salary_stats: dict) -> dict:
    """
    Format column statistics and DataFrame analytics into a flat dictionary.
    """
    midpoint_stats = salary_stats.get("normalized_salary_midpoint", {})
    if not midpoint_stats and isinstance(salary_stats, dict):
        midpoint_stats = salary_stats

    midpoints = (
        df["normalized_salary_midpoint"].dropna().to_numpy(dtype=float)
        if "normalized_salary_midpoint" in df.columns
        else np.array([], dtype=float)
    )
    midpoints = midpoints[np.isfinite(midpoints)]

    if midpoints.size > 0:
        count = int(midpoints.size)
        mean = float(np.mean(midpoints))
        median = float(np.median(midpoints))
        minimum = float(np.min(midpoints))
        maximum = float(np.max(midpoints))
        std = float(np.std(midpoints))

        q1 = float(np.percentile(midpoints, 25))
        q3 = float(np.percentile(midpoints, 75))
        iqr = float(q3 - q1)

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        lower_outliers = midpoints[midpoints < lower_bound]
        upper_outliers = midpoints[midpoints > upper_bound]

        lower_1_std = float(mean - std)
        upper_1_std = float(mean + std)
        lower_2_std = float(mean - 2 * std)
        upper_2_std = float(mean + 2 * std)
        outlier_count = int(lower_outliers.size + upper_outliers.size)
        lower_outlier_count = int(lower_outliers.size)
        upper_outlier_count = int(upper_outliers.size)
    else:
        count = int(midpoint_stats.get("count", 0))
        mean = float(midpoint_stats.get("mean", 0.0))
        median = float(midpoint_stats.get("median", 0.0))
        minimum = float(midpoint_stats.get("minimum", 0.0))
        maximum = float(midpoint_stats.get("maximum", 0.0))
        std = float(midpoint_stats.get("standard_deviation", 0.0))
        q1 = q3 = iqr = 0.0
        lower_1_std = upper_1_std = lower_2_std = upper_2_std = 0.0
        outlier_count = lower_outlier_count = upper_outlier_count = 0

    has_min = (
        df["normalized_salary_min"].notna()
        if "normalized_salary_min" in df.columns
        else pd.Series(False, index=df.index)
    )
    has_max = (
        df["normalized_salary_max"].notna()
        if "normalized_salary_max" in df.columns
        else pd.Series(False, index=df.index)
    )
    has_mid = (
        df["normalized_salary_midpoint"].notna()
        if "normalized_salary_midpoint" in df.columns
        else pd.Series(False, index=df.index)
    )
    has_both = has_min & has_max

    jobs_with_min = int(has_min.sum())
    jobs_with_max = int(has_max.sum())
    jobs_with_midpoint = int(has_mid.sum())
    jobs_with_complete = int(has_both.sum())

    if has_both.any():
        ranges = (
            (
                df.loc[has_both, "normalized_salary_max"]
                - df.loc[has_both, "normalized_salary_min"]
            )
            .dropna()
            .to_numpy(dtype=float)
        )
        ranges = ranges[np.isfinite(ranges)]
    else:
        ranges = np.array([], dtype=float)

    if ranges.size > 0:
        min_range = float(np.min(ranges))
        max_range = float(np.max(ranges))
        mean_range = float(np.mean(ranges))
        median_range = float(np.median(ranges))
    else:
        min_range = max_range = mean_range = median_range = 0.0

    return {
        "count": count,
        "mean": mean,
        "median": median,
        "minimum": minimum,
        "maximum": maximum,
        "standard_deviation": std,
        "p25": q1,
        "p50": median,
        "p75": q3,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower_1_std": lower_1_std,
        "upper_1_std": upper_1_std,
        "lower_2_std": lower_2_std,
        "upper_2_std": upper_2_std,
        "outlier_count": outlier_count,
        "lower_outlier_count": lower_outlier_count,
        "upper_outlier_count": upper_outlier_count,
        "jobs_with_min_salary": jobs_with_min,
        "jobs_with_max_salary": jobs_with_max,
        "jobs_with_midpoint_salary": jobs_with_midpoint,
        "jobs_with_complete_range": jobs_with_complete,
        "minimum_range": min_range,
        "maximum_range": max_range,
        "mean_range": mean_range,
        "median_range": median_range,
    }


def create_ingestion_run(
    session: Session,
    started_at: datetime,
    analysis_version: Optional[str],
) -> IngestionRun:
    """
    Create a new ingestion run record initialized in the RUNNING state.
    """
    run = IngestionRun(
        started_at=started_at,
        status="running",
        rows_fetched=0,
        rows_before_cleaning=0,
        rows_after_cleaning=0,
        jobs_inserted=0,
        jobs_updated=0,
        jobs_inactivated=0,
        analysis_version=analysis_version,
    )
    session.add(run)
    session.flush()
    return run


if __name__ == "__main__":
    result = run_pipeline(
        max_pages=int(getattr(settings, "ADZUNA_MAX_PAGES", 3)),
        analysis_version=getattr(settings, "ADZUNA_ANALYSIS_VERSION", "2.3"),
    )
