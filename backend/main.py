from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from data_pipeline.database.connection import engine
from data_pipeline.database.models import (
    IngestionRun,
    Listing,
    SalaryInsight,
)
from data_pipeline.database.scheduler.main_scheduler import start_scheduler
from data_pipeline.schemas.application import (
    ApplicationUpdate,
)
from data_pipeline.services.application_tracker import (
    APPLICATION_STATUSES,
    get_application,
    update_application,
)
from data_pipeline.services.job_prioritization import (
    PrioritizationProfile,
    score_listing,
)


def build_prioritization_profile(
    target_titles: Optional[str],
    preferred_categories: Optional[str],
    preferred_locations: Optional[str],
    preferred_contract_types: Optional[str],
):
    def split_values(value):
        if not value:
            return []

        return [item.strip() for item in value.split(",") if item.strip()]

    return PrioritizationProfile(
        target_titles=split_values(target_titles),
        preferred_categories=split_values(preferred_categories),
        preferred_locations=split_values(preferred_locations),
        preferred_contract_types=split_values(preferred_contract_types),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="Tech Job Analytics API",
    description="API for accessing tech job listings and analytics data.",
    version="0.2.0",
    lifespan=lifespan,
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
                    "application_status": listing.application_status,
                    "saved_at": listing.saved_at,
                    "applied_at": listing.applied_at,
                    "follow_up_at": listing.follow_up_at,
                    "user_priority": listing.user_priority,
                    "application_notes": listing.application_notes,
                }
                for listing in listings
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    with Session(engine) as session:
        listing = session.query(Listing).filter(Listing.id == job_id).first()

        if listing is None:
            raise HTTPException(
                status_code=404,
                detail=f"Job with ID '{job_id}' not found.",
            )

        return {
            "id": listing.id,
            "title": listing.title,
            "description": listing.description,
            "created": listing.created,
            "redirect_url": listing.redirect_url,
            "adref": listing.adref,
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
            "application_status": listing.application_status,
            "saved_at": listing.saved_at,
            "applied_at": listing.applied_at,
            "follow_up_at": listing.follow_up_at,
            "user_priority": listing.user_priority,
            "application_notes": listing.application_notes,
        }


@app.get("/analytics/prioritization/{job_id}")
async def get_job_prioritization(
    job_id: str,
    target_titles: Optional[str] = Query(
        None,
        description=("Comma-separated target job titles."),
    ),
    preferred_categories: Optional[str] = Query(
        None,
        description=("Comma-separated preferred categories."),
    ),
    preferred_locations: Optional[str] = Query(
        None,
        description=("Comma-separated preferred locations."),
    ),
    preferred_contract_types: Optional[str] = Query(
        None,
        description=("Comma-separated preferred contract types."),
    ),
):
    with Session(engine) as session:
        listing = session.query(Listing).filter(Listing.id == job_id).first()

        if listing is None:
            raise HTTPException(
                status_code=404,
                detail=f"Job with ID '{job_id}' not found.",
            )

        reference_salaries = [
            value[0]
            for value in (
                session.query(Listing.normalized_salary_midpoint)
                .filter(
                    Listing.is_active.is_(True),
                    Listing.normalized_salary_midpoint.isnot(None),
                )
                .all()
            )
        ]

        profile = build_prioritization_profile(
            target_titles,
            preferred_categories,
            preferred_locations,
            preferred_contract_types,
        )

        prioritization = score_listing(
            listing=listing,
            reference_salaries=reference_salaries,
            profile=profile,
        )

        return {
            "job": {
                "id": listing.id,
                "title": listing.title,
                "company_name": listing.company_name,
                "category_label": listing.category_label,
                "location_name": listing.location_name,
                "salary": listing.normalized_salary_midpoint,
                "salary_min": listing.normalized_salary_min,
                "salary_max": listing.normalized_salary_max,
                "contract_type": listing.contract_type,
                "created": listing.created,
                "redirect_url": listing.redirect_url,
            },
            **prioritization,
        }


@app.get("/analytics/prioritization")
async def get_prioritized_jobs(
    target_titles: Optional[str] = Query(None),
    preferred_categories: Optional[str] = Query(None),
    preferred_locations: Optional[str] = Query(None),
    preferred_contract_types: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    with Session(engine) as session:
        jobs = session.query(Listing).filter(Listing.is_active.is_(True)).all()

        if not jobs:
            return {
                "page": page,
                "page_size": page_size,
                "total": 0,
                "jobs": [],
            }

        reference_salaries = [
            job.normalized_salary_midpoint
            for job in jobs
            if job.normalized_salary_midpoint is not None
        ]

        profile = build_prioritization_profile(
            target_titles,
            preferred_categories,
            preferred_locations,
            preferred_contract_types,
        )

        scored_jobs = []

        for job in jobs:
            prioritization = score_listing(
                listing=job,
                reference_salaries=reference_salaries,
                profile=profile,
            )

            scored_jobs.append(
                {
                    "id": job.id,
                    "title": job.title,
                    "company_name": job.company_name,
                    "category_label": job.category_label,
                    "location_name": job.location_name,
                    "salary": job.normalized_salary_midpoint,
                    "salary_min": job.normalized_salary_min,
                    "salary_max": job.normalized_salary_max,
                    "contract_type": job.contract_type,
                    "created": job.created,
                    "redirect_url": job.redirect_url,
                    **prioritization,
                }
            )

        scored_jobs.sort(
            key=lambda job: (
                job["priority_score"],
                job["salary"] or 0,
            ),
            reverse=True,
        )

        total = len(scored_jobs)

        start = (page - 1) * page_size
        end = start + page_size

        paginated_jobs = scored_jobs[start:end]

        for index, job in enumerate(
            paginated_jobs,
            start=start + 1,
        ):
            job["rank"] = index

        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "jobs": paginated_jobs,
        }


@app.get("/jobs/{job_id}/application")
async def get_job_application(job_id: str):
    with Session(engine) as session:
        listing = get_application(job_id, session)

        return {
            "job_id": listing.id,
            "application_status": listing.application_status,
            "saved_at": listing.saved_at,
            "applied_at": listing.applied_at,
            "follow_up_at": listing.follow_up_at,
            "user_priority": listing.user_priority,
            "application_notes": listing.application_notes,
        }


@app.patch("/jobs/{job_id}/application")
async def update_job_application(
    job_id: str,
    payload: ApplicationUpdate,
):
    with Session(engine) as session:
        listing = get_application(job_id, session)

        listing = update_application(
            session=session,
            listing=listing,
            application_status=payload.application_status,
            user_priority=payload.user_priority,
            follow_up_at=payload.follow_up_at,
            application_notes=payload.application_notes,
        )

        return {
            "job_id": listing.id,
            "application_status": listing.application_status,
            "saved_at": listing.saved_at,
            "applied_at": listing.applied_at,
            "follow_up_at": listing.follow_up_at,
            "user_priority": listing.user_priority,
            "application_notes": listing.application_notes,
        }


@app.get("/applications")
async def get_applications(
    status: Optional[str] = None,
    priority: Optional[int] = None,
):
    with Session(engine) as session:
        query = session.query(Listing)

        if status is not None:
            status = status.upper()

            if status not in APPLICATION_STATUSES:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Invalid application status '{status}'. "
                        f"Allowed statuses: "
                        f"{', '.join(sorted(APPLICATION_STATUSES))}."
                    ),
                )

            query = query.filter(Listing.application_status == status)
        else:
            # NEW jobs are ordinary untracked jobs.
            # The applications endpoint shows jobs
            # that have entered the tracker.
            query = query.filter(Listing.application_status != "NEW")

        if priority is not None:
            if priority not in {1, 2, 3}:
                raise HTTPException(
                    status_code=422,
                    detail="priority must be 1, 2, or 3.",
                )

            query = query.filter(Listing.user_priority == priority)

        listings = query.order_by(
            desc(Listing.user_priority),
            desc(Listing.applied_at),
            desc(Listing.saved_at),
        ).all()

        return [
            {
                "id": listing.id,
                "title": listing.title,
                "company_name": listing.company_name,
                "location_name": listing.location_name,
                "normalized_salary_min": (listing.normalized_salary_min),
                "normalized_salary_max": (listing.normalized_salary_max),
                "normalized_salary_midpoint": (listing.normalized_salary_midpoint),
                "redirect_url": listing.redirect_url,
                "application_status": (listing.application_status),
                "saved_at": listing.saved_at,
                "applied_at": listing.applied_at,
                "follow_up_at": listing.follow_up_at,
                "user_priority": listing.user_priority,
                "application_notes": (listing.application_notes),
            }
            for listing in listings
        ]


@app.get("/analytics/metadata")
async def get_analytics_metadata():
    with Session(engine) as session:
        categories = (
            session.query(Listing.category_label)
            .filter(Listing.category_label.isnot(None))
            .distinct()
            .order_by(Listing.category_label)
            .all()
        )

        locations = (
            session.query(Listing.location_name)
            .filter(Listing.location_name.isnot(None))
            .distinct()
            .order_by(Listing.location_name)
            .all()
        )

        contract_time = (
            session.query(Listing.contract_time)
            .filter(Listing.contract_time.isnot(None))
            .distinct()
            .order_by(Listing.contract_time)
            .all()
        )

        contract_type = (
            session.query(Listing.contract_type)
            .filter(Listing.contract_type.isnot(None))
            .distinct()
            .order_by(Listing.contract_type)
            .all()
        )

        salary_prediction = (
            session.query(Listing.salary_is_predicted)
            .filter(Listing.salary_is_predicted.isnot(None))
            .distinct()
            .order_by(Listing.salary_is_predicted)
            .all()
        )

        return {
            "categories": [row[0] for row in categories],
            "locations": [row[0] for row in locations],
            "contract_time": [row[0] for row in contract_time],
            "contract_type": [row[0] for row in contract_type],
            "salary_prediction": [row[0] for row in salary_prediction],
        }


@app.get("/analytics/trends")
async def get_analytics_trends():
    with Session(engine) as session:
        listings = session.query(Listing).all()

        if not listings:
            return {"daily": []}

        daily = {}

        for listing in listings:
            if listing.first_seen_at is not None:
                date = listing.first_seen_at.date().isoformat()

                if date not in daily:
                    daily[date] = {
                        "date": date,
                        "jobs_added": 0,
                        "jobs_inactivated": 0,
                        "active_jobs": 0,
                    }

                daily[date]["jobs_added"] += 1

            if listing.inactive_at is not None:
                date = listing.inactive_at.date().isoformat()

                if date not in daily:
                    daily[date] = {
                        "date": date,
                        "jobs_added": 0,
                        "jobs_inactivated": 0,
                        "active_jobs": 0,
                    }

                daily[date]["jobs_inactivated"] += 1

        running_active = 0

        for date in sorted(daily):
            running_active += (
                daily[date]["jobs_added"] - daily[date]["jobs_inactivated"]
            )

            daily[date]["active_jobs"] = running_active

        return {"daily": [daily[date] for date in sorted(daily)]}


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


@app.get("/analytics/breakdown")
async def get_analytics_breakdown():
    with Session(engine) as session:
        # ---------------------------------------------------------
        # 1. Job status
        # ---------------------------------------------------------

        active_count = (
            session.query(Listing).filter(Listing.is_active.is_(True)).count()
        )

        inactive_count = (
            session.query(Listing).filter(Listing.is_active.is_(False)).count()
        )

        # ---------------------------------------------------------
        # 2. Top 10 individual jobs by salary
        # ---------------------------------------------------------

        top_salary_listings = (
            session.query(Listing)
            .filter(Listing.normalized_salary_midpoint.isnot(None))
            .order_by(Listing.normalized_salary_midpoint.desc())
            .limit(10)
            .all()
        )

        top_salary_jobs = [
            {
                "rank": rank,
                "id": listing.id,
                "title": listing.title,
                "company_name": listing.company_name,
                "location_name": listing.location_name,
                "salary": listing.normalized_salary_midpoint,
            }
            for rank, listing in enumerate(top_salary_listings, start=1)
        ]

        # ---------------------------------------------------------
        # 3. Top 10 categories by job count
        # ---------------------------------------------------------

        category_rows = (
            session.query(
                Listing.category_label,
                func.count(Listing.id).label("job_count"),
                func.avg(Listing.normalized_salary_midpoint).label("mean_salary"),
            )
            .filter(Listing.category_label.isnot(None))
            .group_by(Listing.category_label)
            .order_by(func.count(Listing.id).desc())
            .limit(10)
            .all()
        )

        top_categories = []

        for rank, row in enumerate(category_rows, start=1):
            category_jobs = (
                session.query(Listing.normalized_salary_midpoint)
                .filter(
                    Listing.category_label == row.category_label,
                    Listing.normalized_salary_midpoint.isnot(None),
                )
                .order_by(Listing.normalized_salary_midpoint)
                .all()
            )

            salaries = [value[0] for value in category_jobs]

            if salaries:
                middle = len(salaries) // 2

                if len(salaries) % 2 == 0:
                    median_salary = (salaries[middle - 1] + salaries[middle]) / 2
                else:
                    median_salary = salaries[middle]
            else:
                median_salary = None

            top_categories.append(
                {
                    "rank": rank,
                    "category": row.category_label,
                    "job_count": row.job_count,
                    "mean_salary": (
                        float(row.mean_salary) if row.mean_salary is not None else None
                    ),
                    "median_salary": (
                        float(median_salary) if median_salary is not None else None
                    ),
                }
            )

        # ---------------------------------------------------------
        # 4. Top 10 locations by job count
        # ---------------------------------------------------------

        location_rows = (
            session.query(
                Listing.location_name,
                func.count(Listing.id).label("job_count"),
                func.avg(Listing.normalized_salary_midpoint).label("mean_salary"),
            )
            .filter(Listing.location_name.isnot(None))
            .group_by(Listing.location_name)
            .order_by(func.count(Listing.id).desc())
            .limit(10)
            .all()
        )

        top_locations = []

        for rank, row in enumerate(location_rows, start=1):
            location_jobs = (
                session.query(Listing.normalized_salary_midpoint)
                .filter(
                    Listing.location_name == row.location_name,
                    Listing.normalized_salary_midpoint.isnot(None),
                )
                .order_by(Listing.normalized_salary_midpoint)
                .all()
            )

            salaries = [value[0] for value in location_jobs]

            if salaries:
                middle = len(salaries) // 2

                if len(salaries) % 2 == 0:
                    median_salary = (salaries[middle - 1] + salaries[middle]) / 2
                else:
                    median_salary = salaries[middle]
            else:
                median_salary = None

            top_locations.append(
                {
                    "rank": rank,
                    "location": row.location_name,
                    "job_count": row.job_count,
                    "mean_salary": (
                        float(row.mean_salary) if row.mean_salary is not None else None
                    ),
                    "median_salary": (
                        float(median_salary) if median_salary is not None else None
                    ),
                }
            )

        # ---------------------------------------------------------
        # 5. Top 10 companies by job count
        # ---------------------------------------------------------

        company_rows = (
            session.query(
                Listing.company_name,
                func.count(Listing.id).label("job_count"),
                func.avg(Listing.normalized_salary_midpoint).label("mean_salary"),
            )
            .filter(Listing.company_name.isnot(None))
            .group_by(Listing.company_name)
            .order_by(func.count(Listing.id).desc())
            .limit(10)
            .all()
        )

        top_companies = []

        for rank, row in enumerate(company_rows, start=1):
            company_jobs = (
                session.query(Listing.normalized_salary_midpoint)
                .filter(
                    Listing.company_name == row.company_name,
                    Listing.normalized_salary_midpoint.isnot(None),
                )
                .order_by(Listing.normalized_salary_midpoint)
                .all()
            )

            salaries = [value[0] for value in company_jobs]

            if salaries:
                middle = len(salaries) // 2

                if len(salaries) % 2 == 0:
                    median_salary = (salaries[middle - 1] + salaries[middle]) / 2
                else:
                    median_salary = salaries[middle]
            else:
                median_salary = None

            top_companies.append(
                {
                    "rank": rank,
                    "company": row.company_name,
                    "job_count": row.job_count,
                    "mean_salary": (
                        float(row.mean_salary) if row.mean_salary is not None else None
                    ),
                    "median_salary": (
                        float(median_salary) if median_salary is not None else None
                    ),
                }
            )

        # ---------------------------------------------------------
        # 6. Contract time
        # ---------------------------------------------------------

        contract_time_rows = (
            session.query(
                Listing.contract_time,
                func.count(Listing.id).label("job_count"),
            )
            .filter(Listing.contract_time.isnot(None))
            .group_by(Listing.contract_time)
            .order_by(func.count(Listing.id).desc())
            .all()
        )

        contract_time = [
            {
                "rank": rank,
                "contract_time": row.contract_time,
                "job_count": row.job_count,
            }
            for rank, row in enumerate(contract_time_rows, start=1)
        ]

        # ---------------------------------------------------------
        # 7. Contract type
        # ---------------------------------------------------------

        contract_type_rows = (
            session.query(
                Listing.contract_type,
                func.count(Listing.id).label("job_count"),
            )
            .filter(Listing.contract_type.isnot(None))
            .group_by(Listing.contract_type)
            .order_by(func.count(Listing.id).desc())
            .all()
        )

        contract_type = [
            {
                "rank": rank,
                "contract_type": row.contract_type,
                "job_count": row.job_count,
            }
            for rank, row in enumerate(contract_type_rows, start=1)
        ]

        # ---------------------------------------------------------
        # 8. Salary prediction
        # ---------------------------------------------------------

        predicted_count = (
            session.query(Listing).filter(Listing.salary_is_predicted.is_(True)).count()
        )

        not_predicted_count = (
            session.query(Listing)
            .filter(Listing.salary_is_predicted.is_(False))
            .count()
        )

        salary_prediction = [
            {
                "rank": 1,
                "salary_predicted": False,
                "job_count": not_predicted_count,
            },
            {
                "rank": 2,
                "salary_predicted": True,
                "job_count": predicted_count,
            },
        ]

        # ---------------------------------------------------------
        # 9. Return complete breakdown
        # ---------------------------------------------------------

        return {
            "job_status": {
                "active": active_count,
                "inactive": inactive_count,
            },
            "top_salary_jobs": top_salary_jobs,
            "top_categories": top_categories,
            "top_locations": top_locations,
            "top_companies": top_companies,
            "contract_time": contract_time,
            "contract_type": contract_type,
            "salary_prediction": salary_prediction,
        }


@app.get("/analytics/categories")
async def get_categories():
    with Session(engine) as session:
        categories = (
            session.query(Listing.category_label)
            .filter(Listing.category_label.isnot(None))
            .distinct()
            .order_by(Listing.category_label.asc())
            .all()
        )

        return {"categories": [category[0] for category in categories]}


@app.get("/analytics/categories/{category}")
async def get_category_analytics(category: str):
    with Session(engine) as session:
        jobs = (
            session.query(Listing)
            .filter(
                Listing.category_label == category,
                Listing.is_active.is_(True),
            )
            .all()
        )

        if not jobs:
            raise HTTPException(
                status_code=404,
                detail=f"Category '{category}' not found.",
            )

        salaries = [
            job.normalized_salary_midpoint
            for job in jobs
            if job.normalized_salary_midpoint is not None
        ]

        salary = {
            "mean": None,
            "median": None,
            "minimum": None,
            "maximum": None,
        }

        if salaries:
            import numpy as np

            salary = {
                "mean": float(np.mean(salaries)),
                "median": float(np.median(salaries)),
                "minimum": float(np.min(salaries)),
                "maximum": float(np.max(salaries)),
            }

        top_jobs = sorted(
            jobs,
            key=lambda job: (
                job.normalized_salary_midpoint
                if job.normalized_salary_midpoint is not None
                else float("-inf")
            ),
            reverse=True,
        )[:10]

        return {
            "category": category,
            "job_count": len(jobs),
            "salary": salary,
            "top_jobs": [
                {
                    "rank": rank,
                    "id": job.id,
                    "title": job.title,
                    "company_name": job.company_name,
                    "location_name": job.location_name,
                    "salary": job.normalized_salary_midpoint,
                    "salary_min": job.normalized_salary_min,
                    "salary_max": job.normalized_salary_max,
                    "salary_is_predicted": job.salary_is_predicted,
                    "created": job.created,
                    "redirect_url": job.redirect_url,
                }
                for rank, job in enumerate(top_jobs, start=1)
            ],
        }


@app.get("/analytics/salary/distribution")
async def get_salary_distribution(
    category: Optional[str] = Query(
        None,
        description="Optional category to analyze.",
    ),
):
    with Session(engine) as session:
        query = session.query(Listing).filter(
            Listing.is_active.is_(True),
            Listing.normalized_salary_midpoint.isnot(None),
        )

        if category is not None:
            query = query.filter(Listing.category_label == category)

        listings = query.all()

        if not listings:
            if category is not None:
                raise HTTPException(
                    status_code=404,
                    detail=f"No active salary records found for category '{category}'.",
                )

            raise HTTPException(
                status_code=404,
                detail="No active salary records available.",
            )

        salaries = np.array(
            [float(listing.normalized_salary_midpoint) for listing in listings],
            dtype=float,
        )

        minimum = float(np.min(salaries))
        maximum = float(np.max(salaries))
        mean = float(np.mean(salaries))
        median = float(np.median(salaries))

        q1 = float(np.percentile(salaries, 25))
        q3 = float(np.percentile(salaries, 75))
        iqr = q3 - q1

        standard_deviation = float(np.std(salaries))

        lower_outlier_boundary = q1 - (1.5 * iqr)
        upper_outlier_boundary = q3 + (1.5 * iqr)

        lower_outliers = salaries[salaries < lower_outlier_boundary]
        upper_outliers = salaries[salaries > upper_outlier_boundary]

        outliers = np.concatenate([lower_outliers, upper_outliers])

        # Choose a sensible number of bins based on dataset size.
        # For small subsets, avoid producing dozens of nearly empty bins.
        bin_count = min(
            12,
            max(5, int(np.sqrt(len(salaries)))),
        )

        if minimum == maximum:
            edges = np.array(
                [
                    minimum - 0.5,
                    maximum + 0.5,
                ]
            )
        else:
            edges = np.linspace(
                minimum,
                maximum,
                bin_count + 1,
            )

        counts, edges = np.histogram(
            salaries,
            bins=edges,
        )

        bins = []

        for index, count in enumerate(counts):
            bins.append(
                {
                    "min": float(edges[index]),
                    "max": float(edges[index + 1]),
                    "count": int(count),
                    "label": (
                        f"£{edges[index] / 1000:.0f}k–£{edges[index + 1] / 1000:.0f}k"
                    ),
                }
            )

        return {
            "scope": {
                "type": "category" if category else "all",
                "category": category,
            },
            "job_count": len(listings),
            "salary_count": len(salaries),
            "bins": bins,
            "statistics": {
                "minimum": minimum,
                "q1": q1,
                "median": median,
                "mean": mean,
                "q3": q3,
                "maximum": maximum,
                "iqr": iqr,
                "standard_deviation": standard_deviation,
            },
            "outliers": {
                "total": int(len(outliers)),
                "lower": int(len(lower_outliers)),
                "upper": int(len(upper_outliers)),
                "lower_boundary": float(lower_outlier_boundary),
                "upper_boundary": float(upper_outlier_boundary),
            },
        }


@app.get("/health")
async def health_check():
    with Session(engine) as session:
        try:
            listings_count = session.query(Listing).count()

            latest_ingestion = (
                session.query(Listing.last_seen_at)
                .order_by(Listing.last_seen_at.desc())
                .first()
            )

            return {
                "status": "ok",
                "database": "ok",
                "listings": listings_count,
                "latest_ingestion": (latest_ingestion[0] if latest_ingestion else None),
            }

        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail=f"Database unavailable: {error}",
            )


@app.get("/ingestion/status")
async def get_ingestion_status():
    with Session(engine) as session:
        latest_run = (
            session.query(IngestionRun).order_by(IngestionRun.started_at.desc()).first()
        )

        active_jobs = session.query(Listing).filter(Listing.is_active.is_(True)).count()

        inactive_jobs = (
            session.query(Listing).filter(Listing.is_active.is_(False)).count()
        )

        total_jobs = session.query(Listing).count()

        if latest_run is None:
            return {
                "status": "never_run",
                "last_run": None,
                "jobs": {
                    "total": total_jobs,
                    "active": active_jobs,
                    "inactive": inactive_jobs,
                },
            }

        return {
            "status": latest_run.status,
            "last_run": latest_run.started_at,
            "completed_at": latest_run.completed_at,
            "ingestion_run_id": latest_run.id,
            "rows_fetched": latest_run.rows_fetched,
            "rows_before_cleaning": (latest_run.rows_before_cleaning),
            "rows_after_cleaning": (latest_run.rows_after_cleaning),
            "jobs_inserted": latest_run.jobs_inserted,
            "jobs_updated": latest_run.jobs_updated,
            "jobs_inactivated": latest_run.jobs_inactivated,
            "salary_insight_id": latest_run.salary_insight_id,
            "analysis_version": latest_run.analysis_version,
            "bronze_path": latest_run.bronze_path,
            "error_message": latest_run.error_message,
            "jobs": {
                "total": total_jobs,
                "active": active_jobs,
                "inactive": inactive_jobs,
            },
        }


@app.get("/ingestion/runs")
async def get_ingestion_runs(
    page: int = 1,
    page_size: int = 20,
):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="page must be greater than or equal to 1.",
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="page_size must be between 1 and 100.",
        )

    with Session(engine) as session:
        total = session.query(IngestionRun).count()

        runs = (
            session.query(IngestionRun)
            .order_by(IngestionRun.started_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ((total + page_size - 1) // page_size if total > 0 else 0),
            "runs": [
                {
                    "id": run.id,
                    "started_at": run.started_at,
                    "completed_at": run.completed_at,
                    "status": run.status,
                    "rows_fetched": run.rows_fetched,
                    "rows_before_cleaning": (run.rows_before_cleaning),
                    "rows_after_cleaning": (run.rows_after_cleaning),
                    "jobs_inserted": run.jobs_inserted,
                    "jobs_updated": run.jobs_updated,
                    "jobs_inactivated": run.jobs_inactivated,
                    "salary_insight_id": (run.salary_insight_id),
                    "bronze_path": run.bronze_path,
                    "analysis_version": run.analysis_version,
                    "error_message": run.error_message,
                }
                for run in runs
            ],
        }
