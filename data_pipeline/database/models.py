from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    redirect_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    adref: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_is_predicted: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    contract_time: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    contract_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    company_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    category_label: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category_tag: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    location_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    country: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    salary_currency: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    salary_period: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    normalized_salary_min: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    normalized_salary_max: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    normalized_salary_midpoint: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    inactive_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    application_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="NEW",
    )
    saved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    applied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    follow_up_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    user_priority: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    application_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )


class SalaryInsight(Base):
    __tablename__ = "salary_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    job_count: Mapped[int] = mapped_column(Integer, nullable=False)
    salary_count: Mapped[int] = mapped_column(Integer, nullable=False)

    mean_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    minimum_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    maximum_salary: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    standard_deviation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    p25: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    p50: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    p75: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    q1: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    q3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    iqr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    lower_1_std: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    upper_1_std: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lower_2_std: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    upper_2_std: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    outlier_count: Mapped[int] = mapped_column(Integer, nullable=False)
    lower_outlier_count: Mapped[int] = mapped_column(Integer, nullable=False)
    upper_outlier_count: Mapped[int] = mapped_column(Integer, nullable=False)

    jobs_with_min_salary: Mapped[int] = mapped_column(Integer, nullable=False)
    jobs_with_max_salary: Mapped[int] = mapped_column(Integer, nullable=False)
    jobs_with_midpoint_salary: Mapped[int] = mapped_column(Integer, nullable=False)
    jobs_with_complete_range: Mapped[int] = mapped_column(Integer, nullable=False)

    minimum_range: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    maximum_range: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mean_range: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    median_range: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    analysis_version: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="2.3",
    )


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    rows_fetched: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    rows_before_cleaning: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    rows_after_cleaning: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_inserted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_updated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    jobs_inactivated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    salary_insight_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    bronze_path: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    analysis_version: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )


class ListingHistory(Base):
    __tablename__ = "listing_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    listing_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("listings.id"),
        nullable=False,
    )

    ingestion_run_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ingestion_runs.id"),
        nullable=False,
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String, nullable=False)

    salary_min: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    salary_max: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    salary_is_predicted: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )

    normalized_salary_min: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    normalized_salary_max: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    normalized_salary_midpoint: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    contract_time: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    contract_type: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    company_name: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    category_label: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    category_tag: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    location_name: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )


Index(
    "ix_listing_history_listing_id_observed_at",
    ListingHistory.listing_id,
    ListingHistory.observed_at,
)

Index(
    "ix_listing_history_ingestion_run_id",
    ListingHistory.ingestion_run_id,
)

Index(
    "ix_ingestion_runs_started_at",
    IngestionRun.started_at,
)
