from datetime import datetime
from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody


class JobSort(str, Enum):
    created_asc = "created_asc"
    created_desc = "created_desc"
    salary_asc = "salary_asc"
    salary_desc = "salary_desc"
    title_asc = "title_asc"
    title_desc = "title_desc"
    company_asc = "company_asc"
    company_desc = "company_desc"


class ApplicationStatus(str, Enum):
    NEW = "NEW"
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"


class Pagination(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)


ResponseItem = TypeVar("ResponseItem")


class PaginatedResponse(BaseModel, Generic[ResponseItem]):
    items: List[ResponseItem]
    pagination: Pagination


class JobResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    created: Optional[str] = None
    redirect_url: Optional[str] = None
    adref: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_is_predicted: Optional[bool] = None
    contract_time: Optional[str] = None
    contract_type: Optional[str] = None
    company_name: Optional[str] = None
    category_label: Optional[str] = None
    category_tag: Optional[str] = None
    location_name: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    normalized_salary_min: Optional[float] = None
    normalized_salary_max: Optional[float] = None
    normalized_salary_midpoint: Optional[float] = None
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    inactive_at: Optional[datetime] = None
    application_status: Optional[str] = None
    saved_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    follow_up_at: Optional[datetime] = None
    user_priority: Optional[int] = None
    application_notes: Optional[str] = None


class JobListResponse(BaseModel):
    items: List[JobResponse]
    pagination: Pagination


class ApplicationJobResponse(BaseModel):
    id: str
    title: str
    company_name: Optional[str] = None
    location_name: Optional[str] = None
    normalized_salary_min: Optional[float] = None
    normalized_salary_max: Optional[float] = None
    normalized_salary_midpoint: Optional[float] = None
    redirect_url: Optional[str] = None
    application_status: str
    saved_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    follow_up_at: Optional[datetime] = None
    user_priority: Optional[int] = None
    application_notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    job_id: str
    application_status: str
    saved_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    follow_up_at: Optional[datetime] = None
    user_priority: Optional[int] = None
    application_notes: Optional[str] = None


class FlexibleResponse(BaseModel):
    """Contract marker for legacy analytics payloads during migration."""

    data: Any = None

    class Config:
        extra = "allow"


class IngestionRunResponse(BaseModel):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    rows_fetched: int
    rows_before_cleaning: int
    rows_after_cleaning: int
    jobs_inserted: int
    jobs_updated: int
    jobs_inactivated: int
    salary_insight_id: Optional[int] = None
    bronze_path: Optional[str] = None
    analysis_version: Optional[str] = None
    error_message: Optional[str] = None


class IngestionRunListResponse(BaseModel):
    pagination: Pagination
    runs: List[IngestionRunResponse]
