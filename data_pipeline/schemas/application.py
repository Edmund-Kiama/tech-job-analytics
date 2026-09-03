from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# STATUS MEANINGS:
# NEW        Job has not been acted on
# SAVED      User wants to keep the job
# APPLIED    Application submitted
# INTERVIEW  Interview stage
# OFFER      Offer received
# REJECTED   Application rejected
# ARCHIVED   User no longer wants to track it

# PRIORITY LEVELS::
# 1 = LOW
# 2 = MEDIUM
# 3 = HIGH

APPLICATION_STATUSES = {
    "NEW",
    "SAVED",
    "APPLIED",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
    "ARCHIVED",
}


class ApplicationUpdate(BaseModel):
    application_status: Optional[str] = None
    user_priority: Optional[int] = Field(default=None, ge=1, le=3)
    follow_up_at: Optional[datetime] = None
    application_notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    job_id: str
    application_status: str
    saved_at: Optional[datetime]
    applied_at: Optional[datetime]
    follow_up_at: Optional[datetime]
    user_priority: Optional[int]
    application_notes: Optional[str]
