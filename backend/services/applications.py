from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from data_pipeline.database.models import Listing
from data_pipeline.services.application_tracker import (
    get_application,
    update_application,
)


def application_to_dict(listing: Listing) -> dict:
    return {
        "job_id": listing.id,
        "application_status": listing.application_status,
        "saved_at": listing.saved_at,
        "applied_at": listing.applied_at,
        "follow_up_at": listing.follow_up_at,
        "user_priority": listing.user_priority,
        "application_notes": listing.application_notes,
    }


def get_job_application(session: Session, job_id: str) -> dict:
    return application_to_dict(get_application(job_id, session))


def update_job_application(
    session: Session,
    job_id: str,
    application_status: Optional[str] = None,
    user_priority: Optional[int] = None,
    follow_up_at=None,
    application_notes: Optional[str] = None,
) -> dict:
    listing = get_application(job_id, session)
    listing = update_application(
        session=session,
        listing=listing,
        application_status=application_status,
        user_priority=user_priority,
        follow_up_at=follow_up_at,
        application_notes=application_notes,
    )
    return application_to_dict(listing)


def get_applications(
    session: Session,
    status: Optional[str] = None,
    priority: Optional[int] = None,
) -> list:
    query = session.query(Listing)
    if status is not None:
        query = query.filter(Listing.application_status == status)
    else:
        query = query.filter(Listing.application_status != "NEW")
    if priority is not None:
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
            "normalized_salary_min": listing.normalized_salary_min,
            "normalized_salary_max": listing.normalized_salary_max,
            "normalized_salary_midpoint": listing.normalized_salary_midpoint,
            "redirect_url": listing.redirect_url,
            "application_status": listing.application_status,
            "saved_at": listing.saved_at,
            "applied_at": listing.applied_at,
            "follow_up_at": listing.follow_up_at,
            "user_priority": listing.user_priority,
            "application_notes": listing.application_notes,
        }
        for listing in listings
    ]
