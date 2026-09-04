from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from backend.api.schemas import IngestionRunListResponse
from backend.services.system import health, ingestion_runs, ingestion_status
from data_pipeline.database.connection import engine

router = APIRouter()


@router.get("/health")
async def health_check():
    try:
        with Session(engine) as session:
            return health(session)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {error}",
        )


@router.get("/ingestion/status")
async def get_ingestion_status():
    with Session(engine) as session:
        return ingestion_status(session)


@router.get("/ingestion/runs", response_model=IngestionRunListResponse)
async def get_ingestion_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    with Session(engine) as session:
        return ingestion_runs(session, page, page_size)
