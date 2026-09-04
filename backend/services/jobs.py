from typing import Optional

from sqlalchemy.orm import Session

from backend.api.schemas import JobSort
from data_pipeline.database.models import Listing


def listing_to_dict(listing: Listing, include_adref: bool = False) -> dict:
    result = {
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
    if include_adref:
        result["adref"] = listing.adref
    return result


def get_jobs(
    session: Session,
    page: int,
    page_size: int,
    search: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    contract_type: Optional[str] = None,
    contract_time: Optional[str] = None,
    min_salary: Optional[float] = None,
    max_salary: Optional[float] = None,
    salary_is_predicted: Optional[bool] = None,
    is_active: Optional[bool] = None,
    sort: JobSort = JobSort.created_desc,
) -> dict:
    query = session.query(Listing)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            Listing.title.ilike(search_term)
            | Listing.company_name.ilike(search_term)
            | Listing.description.ilike(search_term)
        )
    if category:
        query = query.filter(Listing.category_label.ilike(category.strip()))
    if location:
        location_term = f"%{location.strip()}%"
        query = query.filter(
            Listing.location_name.ilike(location_term)
            | Listing.city.ilike(location_term)
            | Listing.region.ilike(location_term)
            | Listing.country.ilike(location_term)
        )
    if contract_type:
        query = query.filter(Listing.contract_type.ilike(contract_type.strip()))
    if contract_time:
        query = query.filter(Listing.contract_time.ilike(contract_time.strip()))
    if min_salary is not None:
        query = query.filter(Listing.normalized_salary_max >= min_salary)
    if max_salary is not None:
        query = query.filter(Listing.normalized_salary_min <= max_salary)
    if salary_is_predicted is not None:
        query = query.filter(Listing.salary_is_predicted == salary_is_predicted)
    if is_active is not None:
        query = query.filter(Listing.is_active == is_active)

    sort_columns = {
        JobSort.created_asc: Listing.created.asc(),
        JobSort.created_desc: Listing.created.desc(),
        JobSort.salary_asc: Listing.normalized_salary_midpoint.asc(),
        JobSort.salary_desc: Listing.normalized_salary_midpoint.desc(),
        JobSort.title_asc: Listing.title.asc(),
        JobSort.title_desc: Listing.title.desc(),
        JobSort.company_asc: Listing.company_name.asc(),
        JobSort.company_desc: Listing.company_name.desc(),
    }
    query = query.order_by(sort_columns[sort])

    total = query.count()
    listings = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": [listing_to_dict(listing) for listing in listings],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
    }


def get_job(session: Session, job_id: str) -> Optional[dict]:
    listing = session.query(Listing).filter(Listing.id == job_id).first()
    return listing_to_dict(listing, include_adref=True) if listing else None
