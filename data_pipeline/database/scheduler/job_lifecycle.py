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
    mMark listings inactive when they have not been seen
    within the configured freshness window.

    Historical records remain in SQLite.
    """

    now = now or datetime.utcnow()

    cutoff = now - timedelta(days=stale_after_days)

    statement = (
        update(Listing)
        .where(
            Listing.is_active.is_(True),
            Listing.last_seen_at < cutoff,
        )
        .values(
            is_active=False,
            inactive_at=now,
        )
    )

    result = session.execute(statement)

    return result.rowcount
