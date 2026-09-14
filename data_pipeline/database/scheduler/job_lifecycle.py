from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from sqlalchemy import and_, or_, select
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


def delete_expired_listings(
    session: Session,
    now: datetime,
    inactive_after_days: int = 7,
    active_after_days: int = 21,
) -> int:
    """
    Delete listings that have exceeded their retention window.

    Rules:
    1. Delete inactive listings that have been inactive for more
       than `inactive_after_days`.
    2. Delete active listings that have not been seen for more
       than `active_after_days`.

    Returns:
        Number of listings deleted.
    """
    now = now or datetime.utcnow()

    inactive_threshold = now - timedelta(days=inactive_after_days)
    active_threshold = now - timedelta(days=active_after_days)

    listings_to_delete = (
        session.execute(
            select(Listing).where(
                or_(
                    # Inactive for more than 7 days
                    and_(
                        Listing.is_active.is_(False),
                        Listing.inactive_at < inactive_threshold,
                    ),
                    # Safety-net: active but not seen for more than 21 days
                    and_(
                        Listing.is_active.is_(True),
                        Listing.last_seen_at < active_threshold,
                    ),
                )
            )
        )
        .scalars()
        .all()
    )

    deleted = 0

    for listing in listings_to_delete:
        session.delete(listing)
        deleted += 1

    return deleted
