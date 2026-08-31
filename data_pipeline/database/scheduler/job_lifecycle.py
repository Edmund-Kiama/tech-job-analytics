from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from data_pipeline.database.models import Listing


def mark_stale_listings(
    session: Session,
    stale_after_days: int,
    now: Optional[datetime] = None,
) -> int:
    """
    mMark active listings inactive when they have not been seen
    within the configured freshness window.

    Historical listings remain in the database.
    """

    if stale_after_days < 0:
        raise ValueError("stale_after_days must be >= 0")

    # SQLite DateTime columns are being used as naive UTC timestamps
    # throughout this project.
    now = now or datetime.utcnow()

    cutoff = now - timedelta(days=stale_after_days)

    statement = (
        update(Listing)
        .where(
            Listing.is_active.is_(True),
            Listing.last_seen_at.is_not(None),
            Listing.last_seen_at < cutoff,
        )
        .values(
            is_active=False,
            inactive_at=now,
        )
    )

    result = session.execute(statement)

    return result.rowcount