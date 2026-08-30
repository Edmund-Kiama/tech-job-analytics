from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from data_pipeline.clients.adzuna import AdzunaClient
from data_pipeline.database.connection import SessionLocal
from data_pipeline.database.models import Listing
from data_pipeline.processing.statistics import (
    build_salary_insight_record,
    calculate_salary_statistics,
)
from data_pipeline.processing.transform import transform_dataframe
from data_pipeline.storage.bronze_loader import load_bronze_json
from data_pipeline.storage.raw import save_raw_payload
from data_pipeline.utils.console import CommentPrinter


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

    jobs = []

    for job in client.iter_jobs(max_pages=max_pages):
        jobs.append(job)

    if not jobs:
        raise ValueError("Adzuna API returned no jobs.")

    payload = {
        "results": jobs,
        "count": len(jobs),
    }

    CommentPrinter(f"JOBS BEFORE BRONZE: {len(jobs)}")
    CommentPrinter(f"PAYLOAD RESULTS: {len(payload['results'])}")

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

    CommentPrinter(f"JOBS BEFORE BRONZE: {len(jobs)}")
    CommentPrinter(f"PAYLOAD RESULTS: {len(payload['results'])}")

    return {
        "bronze_path": Path(bronze_path),
        "rows_before_cleaning": rows_before_cleaning,
        "rows_after_cleaning": rows_after_cleaning,
        "listing_count": listing_count,
        "salary_insight_id": salary_insight_id,
        "analysis_version": analysis_version,
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
    dataframe: pd.DataFrame,
) -> int:
    """
    Persist cleaned DataFrame rows into the listings table.

    Listings are synchronized by their Adzuna ID:
    - new IDs are inserted
    - existing IDs are updated
    - running the pipeline repeatedly is therefore idempotent
    """

    table = Listing.__table__

    # Only allow columns that actually exist in the listings table.
    valid_columns = {column.name for column in table.columns}

    records = dataframe.to_dict(orient="records")

    for record in records:
        if isinstance(record.get("created"), pd.Timestamp):
            record["created"] = record["created"].to_pydatetime()

    processed = 0

    for raw_record in records:
        # Remove raw nested API objects.
        raw_record.pop("company", None)
        raw_record.pop("category", None)
        raw_record.pop("location", None)
        raw_record.pop("__CLASS__", None)

        # Keep only columns represented by Listing.
        record = {
            key: value for key, value in raw_record.items() if key in valid_columns
        }

        if not record.get("id"):
            continue

        stmt = insert(table).values(**record)

        # Do not update the primary key on conflict.
        update_values = {key: value for key, value in record.items() if key != "id"}

        if update_values:
            stmt = stmt.on_conflict_do_update(
                index_elements=[table.c.id],
                set_=update_values,
            )
        else:
            stmt = stmt.on_conflict_do_nothing(
                index_elements=[table.c.id],
            )

        session.execute(stmt)

        processed += 1

    return processed


if __name__ == "__main__":
    result = run_pipeline(max_pages=3)

    # print("=" * 60)
    # print("PIPELINE COMPLETE")
    # print("=" * 60)

    # for key, value in result.items():
    #     print(f"{key}: {value}")
