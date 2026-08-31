from typing import Optional

from fastapi import FastAPI, HTTPException, Query
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
    sort: str = Query("created_desc"),
):
    with Session(engine) as session:
        query = session.query(Listing)

        # ---------------------------------------------------------
        # Search
        # ---------------------------------------------------------

        if search:
            search_term = f"%{search.strip()}%"

            query = query.filter(
                Listing.title.ilike(search_term)
                | Listing.company_name.ilike(search_term)
                | Listing.description.ilike(search_term)
            )

        if category:
            query = query.filter(Listing.category_label.ilike(category.strip()))

        # ---------------------------------------------------------
        # Location
        # ---------------------------------------------------------

        if location:
            location_term = f"%{location.strip()}%"

            query = query.filter(
                Listing.location_name.ilike(location_term)
                | Listing.city.ilike(location_term)
                | Listing.region.ilike(location_term)
                | Listing.country.ilike(location_term)
            )

        # ---------------------------------------------------------
        # Contract type
        # ---------------------------------------------------------

        if contract_type:
            query = query.filter(Listing.contract_type.ilike(contract_type.strip()))

        # ---------------------------------------------------------
        # Contract time
        # ---------------------------------------------------------

        if contract_time:
            query = query.filter(Listing.contract_time.ilike(contract_time.strip()))

        # ---------------------------------------------------------
        # Salary
        # ---------------------------------------------------------

        if min_salary is not None:
            query = query.filter(Listing.normalized_salary_max >= min_salary)
        if max_salary is not None:
            query = query.filter(Listing.normalized_salary_min <= max_salary)

        # ---------------------------------------------------------
        # Predicted salary
        # ---------------------------------------------------------

        if salary_is_predicted is not None:
            query = query.filter(Listing.salary_is_predicted == salary_is_predicted)

        # ---------------------------------------------------------
        # Active / historical
        # ---------------------------------------------------------

        if is_active is not None:
            query = query.filter(Listing.is_active == is_active)

        # ---------------------------------------------------------
        # Sorting
        # ---------------------------------------------------------

        if sort == "created_asc":
            query = query.order_by(Listing.created.asc())

        elif sort == "salary_asc":
            query = query.order_by(Listing.normalized_salary_midpoint.asc())

        elif sort == "salary_desc":
            query = query.order_by(Listing.normalized_salary_midpoint.desc())

        elif sort == "title_asc":
            query = query.order_by(Listing.title.asc())

        elif sort == "title_desc":
            query = query.order_by(Listing.title.desc())

        elif sort == "company_asc":
            query = query.order_by(Listing.company_name.asc())

        elif sort == "company_desc":
            query = query.order_by(Listing.company_name.desc())

        else:
            # Default
            query = query.order_by(Listing.created.desc())

        # ---------------------------------------------------------
        # Pagination
        # ---------------------------------------------------------

        total = query.count()

        offset = (page - 1) * page_size

        listings = query.offset(offset).limit(page_size).all()

        total_pages = (total + page_size - 1) // page_size

        return {
            "items": [
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
                    "first_seen_at": listing.first_seen_at,
                    "last_seen_at": listing.last_seen_at,
                    "is_active": listing.is_active,
                    "inactive_at": listing.inactive_at,
                }
                for listing in listings
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }


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
