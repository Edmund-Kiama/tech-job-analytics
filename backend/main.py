from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from data_pipeline.database.connection import engine
from data_pipeline.database.models import Listing, SalaryInsight

app = FastAPI(
    title="Tech Job Analytics API",
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/jobs")
async def get_jobs():
    with Session(engine) as session:
        listings = session.query(Listing).all()

        return [
            {
                "id": listing.id,
                "title": listing.title,
                "description": listing.description,
                "created": listing.created,
                "redirect_url": listing.redirect_url,
                "salary_min": listing.salary_min,
                "salary_max": listing.salary_max,
                "salary_is_predicted": listing.salary_is_predicted,
                "contract_time": listing.contract_time,
                "contract_type": listing.contract_type,
                "company_name": listing.company_name,
                "category_label": listing.category_label,
                "category_tag": listing.category_tag,
                "location_name": listing.location_name,
                "country": listing.country,
                "region": listing.region,
                "city": listing.city,
                "latitude": listing.latitude,
                "longitude": listing.longitude,
                "salary_currency": listing.salary_currency,
                "salary_period": listing.salary_period,
                "normalized_salary_min": listing.normalized_salary_min,
                "normalized_salary_max": listing.normalized_salary_max,
                "normalized_salary_midpoint": listing.normalized_salary_midpoint,
            }
            for listing in listings
        ]


@app.get("/analytics/summary")
async def get_analytics_summary():
    with Session(engine) as session:
        insight = (
            session.query(SalaryInsight)
            .order_by(SalaryInsight.created_at.desc())
            .first()
        )

        if insight is None:
            raise HTTPException(
                status_code=404,
                detail="No salary analytics available.",
            )

        return {
            "created_at": insight.created_at,
            "analysis_version": insight.analysis_version,
            "job_count": insight.job_count,
            "salary_count": insight.salary_count,
            "mean_salary": insight.mean_salary,
            "median_salary": insight.median_salary,
            "minimum_salary": insight.minimum_salary,
            "maximum_salary": insight.maximum_salary,
            "standard_deviation": insight.standard_deviation,
        }


@app.get("/analytics/salary")
async def get_salary_analytics():
    with Session(engine) as session:
        insight = (
            session.query(SalaryInsight)
            .order_by(SalaryInsight.created_at.desc())
            .first()
        )

        if insight is None:
            raise HTTPException(
                status_code=404,
                detail="No salary analytics available.",
            )

        return {
            "created_at": insight.created_at,
            "analysis_version": insight.analysis_version,
            "distribution": {
                "minimum": insight.minimum_salary,
                "maximum": insight.maximum_salary,
                "mean": insight.mean_salary,
                "median": insight.median_salary,
                "standard_deviation": insight.standard_deviation,
                "p25": insight.p25,
                "p50": insight.p50,
                "p75": insight.p75,
                "q1": insight.q1,
                "q3": insight.q3,
                "iqr": insight.iqr,
            },
            "standard_deviation_ranges": {
                "lower_1_std": insight.lower_1_std,
                "upper_1_std": insight.upper_1_std,
                "lower_2_std": insight.lower_2_std,
                "upper_2_std": insight.upper_2_std,
            },
            "outliers": {
                "total": insight.outlier_count,
                "lower": insight.lower_outlier_count,
                "upper": insight.upper_outlier_count,
            },
            "salary_coverage": {
                "with_min_salary": insight.jobs_with_min_salary,
                "with_max_salary": insight.jobs_with_max_salary,
                "with_midpoint_salary": insight.jobs_with_midpoint_salary,
                "with_complete_range": insight.jobs_with_complete_range,
            },
            "salary_ranges": {
                "minimum": insight.minimum_range,
                "maximum": insight.maximum_range,
                "mean": insight.mean_range,
                "median": insight.median_range,
            },
        }
