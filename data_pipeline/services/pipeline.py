from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from data_pipeline.clients.adzuna import AdzunaClient
from data_pipeline.config import settings
from data_pipeline.database.connection import SessionLocal
from data_pipeline.database.models import Listing
from data_pipeline.database.scheduler.job_lifecycle import (
    mark_stale_listings,
)
from data_pipeline.processing.statistics import (
    build_salary_insight_record,
    calculate_salary_statistics,
)
from data_pipeline.processing.transform import transform_dataframe
from data_pipeline.storage.bronze_loader import load_bronze_json
from data_pipeline.storage.raw import save_raw_payload


def run_pipeline(
    max_pages: int = 3,
    analysis_version: str = "2.3",
) -> dict:
    """
    Run the complete Phase 2 data pipeline.

    Flow:
        Adzuna API
        -> Bronze JSON
        -> Pandas DataFrame
        -> Cleaning
        -> SQLite listings
        -> NumPy statistics
        -> SQLite salary_insights

    Returns a summary of the pipeline execution.
    """

    # ---------------------------------------------------------
    # 1. Extract from Adzuna
    # ---------------------------------------------------------

    client = AdzunaClient()

    pages = list(
        client.iter_pages(
            max_pages=max_pages,
            max_jobs=int(settings.ADZUNA_MAX_JOBS),
        )
    )

    seen_at = datetime.utcnow()

    payload = {
        "fetched_at": seen_at.isoformat(),
        "page_count": len(pages),
        "job_count": sum(len(page.get("results", [])) for page in pages),
        "pages": pages,
    }

    # ---------------------------------------------------------
    # 2. Store immutable Bronze snapshot
    # ---------------------------------------------------------

    bronze_path = save_raw_payload(payload)

    # ---------------------------------------------------------
    # 3. Load Bronze JSON into Pandas
    # ---------------------------------------------------------

    df = load_bronze_json(bronze_path)

    rows_before_cleaning = len(df)

    # ---------------------------------------------------------
    # 4. Clean / transform
    # ---------------------------------------------------------

    cleaned_df = transform_dataframe(df)

    rows_after_cleaning = len(cleaned_df)

    # ---------------------------------------------------------
    # 5. Persist cleaned listings
    # ---------------------------------------------------------

    with SessionLocal() as session:
        listing_count = _save_cleaned_listings(
            session=session,
            dataframe=cleaned_df,
            seen_at=seen_at,
        )
        inactive_count = mark_stale_listings(
            session,
            stale_after_days=int(settings.ADZUNA_STALE_AFTER_DAYS),
            now=seen_at,
        )

        # -----------------------------------------------------
        # 6. Calculate NumPy salary statistics
        # -----------------------------------------------------

        salary_stats = calculate_salary_statistics(cleaned_df)
        flat_stats = _prepare_insight_stats(cleaned_df, salary_stats)

        # -----------------------------------------------------
        # 7. Convert statistics into database-ready values
        # -----------------------------------------------------

        salary_insight_record = build_salary_insight_record(flat_stats)

        # -----------------------------------------------------
        # 8. Persist analytical snapshot
        # -----------------------------------------------------

        from data_pipeline.services.salary_insights import (
            save_salary_insights,
        )

        salary_insight = save_salary_insights(
            session=session,
            insights=salary_insight_record,
            analysis_version=analysis_version,
        )

        session.commit()

        salary_insight_id = salary_insight.id

    # ---------------------------------------------------------
    # 9. Return execution summary
    # ---------------------------------------------------------

    return {
        "bronze_path": Path(bronze_path),
        "rows_before_cleaning": rows_before_cleaning,
        "rows_after_cleaning": rows_after_cleaning,
        "listing_count": listing_count,
        "salary_insight_id": salary_insight_id,
        "analysis_version": analysis_version,
        "inactive_count": inactive_count,
        "jobs_ingested": len(cleaned_df),
        "jobs_seen": len(df),
        "jobs_fetched": payload["job_count"],
    }


def _prepare_insight_stats(df: pd.DataFrame, salary_stats: dict) -> dict:
    """
    Format column statistics and DataFrame analytics into the flat dictionary
    structure expected by build_salary_insight_record.
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


def _save_cleaned_listings(
    session: Session,
    dataframe,
    seen_at: datetime,
) -> int:
    """
    Synchronize cleaned jobs into SQLite.

    Existing jobs are updated.
    New jobs are inserted.
    Adzuna job ID remains the deduplication key.

    Every observed job gets:
        last_seen_at = current ingestion time
        is_active = True
        inactive_at = None

    first_seen_at is only assigned when the job is first inserted.
    """

    records = dataframe.to_dict(orient="records")

    processed = 0

    for record in records:
        record.pop("company", None)
        record.pop("category", None)
        record.pop("location", None)
        record.pop("__CLASS__", None)

        job_id = record["id"]

        existing = session.execute(
            select(Listing).where(Listing.id == job_id)
        ).scalar_one_or_none()

        if existing is None:
            listing = Listing(
                **record,
                first_seen_at=seen_at,
                last_seen_at=seen_at,
                is_active=True,
                inactive_at=None,
            )

            session.add(listing)

        else:
            for field, value in record.items():
                setattr(existing, field, value)

            existing.last_seen_at = seen_at
            existing.is_active = True
            existing.inactive_at = None

        processed += 1

    session.flush()

    return processed


if __name__ == "__main__":
    result = run_pipeline(max_pages=3)

    # print("=" * 60)
    # print("PIPELINE COMPLETE")
    # print("=" * 60)

    # for key, value in result.items():
    #     print(f"{key}: {value}")
