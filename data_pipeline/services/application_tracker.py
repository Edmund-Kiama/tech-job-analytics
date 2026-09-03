from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from data_pipeline.database.models import Listing

APPLICATION_STATUSES = {
    "NEW",
    "SAVED",
    "APPLIED",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
    "ARCHIVED",
}


def utc_now():
    return datetime.now(timezone.utc)


def get_application(job_id: str, session: Session):
    listing = session.query(Listing).filter(Listing.id == job_id).first()

    if listing is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job with ID '{job_id}' not found.",
        )

    return listing


def update_application(
    session: Session,
    listing: Listing,
    application_status: Optional[str] = None,
    user_priority: Optional[int] = None,
    follow_up_at=None,
    application_notes: Optional[str] = None,
):
    now = utc_now()

    if application_status is not None:
        application_status = application_status.upper()

        if application_status not in APPLICATION_STATUSES:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Invalid application status '{application_status}'. "
                    f"Allowed statuses: "
                    f"{', '.join(sorted(APPLICATION_STATUSES))}."
                ),
            )

    if user_priority is not None:
        if user_priority not in {1, 2, 3}:
            raise HTTPException(
                status_code=422,
                detail="user_priority must be 1, 2, or 3.",
            )

    previous_status = listing.application_status

    if application_status is not None:
        listing.application_status = application_status

        # NEW -> SAVED
        if application_status == "SAVED" and listing.saved_at is None:
            listing.saved_at = now

        # NEW/SAVED -> APPLIED
        if application_status == "APPLIED" and listing.applied_at is None:
            listing.applied_at = now

    if user_priority is not None:
        listing.user_priority = user_priority

    if follow_up_at is not None:
        listing.follow_up_at = follow_up_at

    if application_notes is not None:
        listing.application_notes = application_notes

    session.add(listing)
    session.commit()
    session.refresh(listing)

    return listing
