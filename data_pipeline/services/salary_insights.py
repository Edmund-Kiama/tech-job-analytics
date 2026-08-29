from datetime import datetime, timezone

from sqlalchemy.orm import Session

from data_pipeline.database.models import SalaryInsight


def save_salary_insights(
    session: Session,
    insights: dict,
    analysis_version: str = "2.3",
) -> SalaryInsight:
    """
    Persist one salary-insights snapshot to the database.

    The caller is responsible for committing the transaction.
    """

    salary_insight = SalaryInsight(
        **insights,
        created_at=datetime.now(timezone.utc),
        analysis_version=analysis_version,
    )

    session.add(salary_insight)
    session.flush()

    return salary_insight
