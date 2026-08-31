from datetime import datetime, timezone

import numpy as np

# import pandas as pd
from data_pipeline.database.connection import SessionLocal
from data_pipeline.database.models import Listing, SalaryInsight
from data_pipeline.processing.statistics import (
    calculate_salary_statistics,
    # calculate_salary_statistics,
    prepare_salary_arrays,
)
from data_pipeline.processing.transform import transform_dataframe
from data_pipeline.services.pipeline import (
    _prepare_insight_stats,
    _save_cleaned_listings,
    build_salary_insight_record,
)
from data_pipeline.services.salary_insights import save_salary_insights
from data_pipeline.storage.bronze_loader import load_bronze_json
from data_pipeline.utils.helper import get_latest_bronze_file


def test_database_validation():
    """
    Validate that the persisted SQLite data agrees with the
    Pandas/NumPy analytical results from the latest Bronze dataset.
    """

    # ---------------------------------------------------------
    # 1. Bronze -> Pandas
    # ---------------------------------------------------------

    bronze_file = get_latest_bronze_file()
    bronze_df = load_bronze_json(bronze_file)
    cleaned_df = transform_dataframe(bronze_df)

    seen_at = datetime.now(timezone.utc)

    with SessionLocal() as session:
        _save_cleaned_listings(
            session=session,
            dataframe=cleaned_df,
            seen_at=seen_at,
        )

        salary_stats = calculate_salary_statistics(cleaned_df)

        flat_stats = _prepare_insight_stats(
            cleaned_df,
            salary_stats,
        )

        salary_insight_record = build_salary_insight_record(
            flat_stats,
        )

        save_salary_insights(
            session=session,
            insights=salary_insight_record,
            analysis_version="database-validation-test",
        )

        session.commit()

    # ---------------------------------------------------------
    # 2. Pandas -> NumPy -> Statistics
    # ---------------------------------------------------------

    arrays = prepare_salary_arrays(cleaned_df)
    midpoint_values = arrays["normalized_salary_midpoint"]

    # salary_stats = calculate_salary_statistics(cleaned_df)

    # ---------------------------------------------------------
    # 3. Query SQLite
    # ---------------------------------------------------------

    with SessionLocal() as session:
        listings = session.query(Listing).all()
        insights = (
            session.query(SalaryInsight).order_by(SalaryInsight.id.desc()).first()
        )

    # ---------------------------------------------------------
    # 4. Validate job-level data
    # ---------------------------------------------------------

    assert len(listings) == len(cleaned_df)

    db_ids = {listing.id for listing in listings}
    pandas_ids = set(cleaned_df["id"].dropna().astype(str))

    assert db_ids == pandas_ids

    # ---------------------------------------------------------
    # 5. Validate salary counts
    # ---------------------------------------------------------

    db_salary_values = [
        listing.normalized_salary_midpoint
        for listing in listings
        if listing.normalized_salary_midpoint is not None
    ]

    assert len(db_salary_values) == len(midpoint_values)

    # ---------------------------------------------------------
    # 6. Validate SQLite salary values against NumPy values
    # ---------------------------------------------------------

    assert np.allclose(
        sorted(db_salary_values),
        sorted(midpoint_values),
        equal_nan=False,
    )

    # ---------------------------------------------------------
    # 7. Validate analytical snapshot
    # ---------------------------------------------------------

    assert insights is not None

    assert insights.job_count == len(cleaned_df)
    assert insights.salary_count == len(midpoint_values)

    # ---------------------------------------------------------
    # 8. Validate mean
    # ---------------------------------------------------------

    expected_mean = float(np.mean(midpoint_values))

    assert np.isclose(
        insights.mean_salary,
        expected_mean,
    )

    # ---------------------------------------------------------
    # 9. Validate median
    # ---------------------------------------------------------

    expected_median = float(np.median(midpoint_values))

    assert np.isclose(
        insights.median_salary,
        expected_median,
    )

    # ---------------------------------------------------------
    # 10. Validate minimum / maximum
    # ---------------------------------------------------------

    assert np.isclose(
        insights.minimum_salary,
        np.min(midpoint_values),
    )

    assert np.isclose(
        insights.maximum_salary,
        np.max(midpoint_values),
    )

    # ---------------------------------------------------------
    # 11. Validate percentiles
    # ---------------------------------------------------------

    assert np.isclose(
        insights.p25,
        np.percentile(midpoint_values, 25),
    )

    assert np.isclose(
        insights.p50,
        np.percentile(midpoint_values, 50),
    )

    assert np.isclose(
        insights.p75,
        np.percentile(midpoint_values, 75),
    )

    # ---------------------------------------------------------
    # 12. Print validation summary
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("DATABASE VALIDATION")
    print("=" * 60)

    print(f"Bronze file:       {bronze_file}")
    print(f"Pandas jobs:       {len(cleaned_df)}")
    print(f"SQLite listings:   {len(listings)}")
    print(f"NumPy salaries:    {len(midpoint_values)}")
    print(f"SQLite salary rows:{len(db_salary_values)}")

    print("\nSalary comparison:")
    print(f"Pandas/NumPy mean:     {expected_mean}")
    print(f"SQLite mean:           {insights.mean_salary}")

    print(f"Pandas/NumPy median:   {expected_median}")
    print(f"SQLite median:         {insights.median_salary}")

    print(f"Pandas/NumPy minimum:  {np.min(midpoint_values)}")
    print(f"SQLite minimum:        {insights.minimum_salary}")

    print(f"Pandas/NumPy maximum:  {np.max(midpoint_values)}")
    print(f"SQLite maximum:        {insights.maximum_salary}")

    print("\n" + "=" * 60)
    print("DATABASE VALIDATION PASSED")
    print("=" * 60)
