from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from backend.api.schemas import JobListResponse, JobResponse, JobSort
from backend.services.jobs import get_job as get_job_service
from backend.services.jobs import get_jobs as get_jobs_service
from data_pipeline.database.connection import engine

router = APIRouter()


@router.get("/jobs", response_model=JobListResponse)
async def get_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    contract_type: Optional[str] = Query(None),
    contract_time: Optional[str] = Query(None),
    min_salary: Optional[float] = Query(None, ge=0),
    max_salary: Optional[float] = Query(None, ge=0),
    salary_is_predicted: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    sort: JobSort = Query(JobSort.created_desc),
):
    with Session(engine) as session:
        return get_jobs_service(
            session=session,
            page=page,
            page_size=page_size,
            search=search,
            category=category,
            location=location,
            contract_type=contract_type,
            contract_time=contract_time,
            min_salary=min_salary,
            max_salary=max_salary,
            salary_is_predicted=salary_is_predicted,
            is_active=is_active,
            sort=sort,
        )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    with Session(engine) as session:
        job = get_job_service(session, job_id)

        if job is None:
            raise HTTPException(
                status_code=404,
                detail=f"Job with ID '{job_id}' not found.",
            )

        return job
