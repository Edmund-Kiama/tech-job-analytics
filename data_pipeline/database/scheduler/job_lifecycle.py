from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from data_pipeline.database.models import Listing


def mark_stale_listings(
    session: Session,
    stale_after_days: int,
    now: datetime,
) -> int:
    """
    mMark active listings as inactive if they haven't been seen
    within the stale threshold window.
    """
    now = now or datetime.utcnow()

    stale_threshold = now - timedelta(days=stale_after_days)

    stale_listings = (
        session.execute(
            select(Listing).where(
                Listing.is_active.is_(True),
                Listing.last_seen_at < stale_threshold,
            )
        )
        .scalars()
        .all()
    )

    inactivated = 0
    for listing in stale_listings:
        listing.is_active = False
        listing.inactive_at = now
        inactivated += 1

    return inactivated
