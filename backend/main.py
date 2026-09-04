from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routers.analytics import router as analytics_router
from backend.api.routers.applications import router as applications_router
from backend.api.routers.jobs import router as jobs_router
from backend.api.routers.system import router as system_router
from data_pipeline.config import settings
from data_pipeline.database.scheduler.main_scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="UK Job Analytics API",
    description="API for accessing UK job listings and analytics data.",
    version="0.2.0",
    lifespan=lifespan,
)
allowed_origins = settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"]


def _error_code(status_code: int, detail) -> str:
    detail_text = str(detail)
    if status_code == 404 and "Job with ID" in detail_text:
        return "JOB_NOT_FOUND"
    if status_code == 404 and "Category" in detail_text:
        return "CATEGORY_NOT_FOUND"
    if status_code == 404 and "salary analytics" in detail_text:
        return "NO_ANALYTICS"
    if status_code == 404:
        return "NOT_FOUND"
    if status_code == 422:
        return "INVALID_QUERY"
    if status_code == 503:
        return "DATABASE_UNAVAILABLE"
    return "API_ERROR"


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": _error_code(exc.status_code, exc.detail),
                "message": detail,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = "; ".join(error["msg"] for error in exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "INVALID_QUERY",
                "message": messages,
            }
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(analytics_router)
app.include_router(system_router)
