from typing import Optional
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, create_engine
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

    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


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