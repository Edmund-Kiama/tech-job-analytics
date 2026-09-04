from typing import List, Optional

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from backend.api.schemas import (
    ApplicationJobResponse,
    ApplicationResponse,
    ApplicationStatus,
)
from backend.services.applications import (
    get_applications as get_applications_service,
)
from backend.services.applications import (
    get_job_application as get_job_application_service,
)
from backend.services.applications import (
    update_job_application as update_job_application_service,
)
from data_pipeline.database.connection import engine
from data_pipeline.schemas.application import ApplicationUpdate

router = APIRouter()


@router.get("/applications", response_model=List[ApplicationJobResponse])
async def get_applications(
    status: Optional[ApplicationStatus] = Query(None),
    priority: Optional[int] = Query(None, ge=1, le=3),
):
    with Session(engine) as session:
        return get_applications_service(
            session=session,
            status=status.value if status is not None else None,
            priority=priority,
        )


@router.get("/jobs/{job_id}/application", response_model=ApplicationResponse)
async def get_job_application(job_id: str):
    with Session(engine) as session:
        return get_job_application_service(session, job_id)


@router.patch("/jobs/{job_id}/application", response_model=ApplicationResponse)
async def update_job_application(job_id: str, payload: ApplicationUpdate):
    with Session(engine) as session:
        return update_job_application_service(
            session=session,
            job_id=job_id,
            application_status=payload.application_status,
            user_priority=payload.user_priority,
            follow_up_at=payload.follow_up_at,
            application_notes=payload.application_notes,
        )
