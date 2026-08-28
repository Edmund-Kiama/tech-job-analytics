from datetime import datetime, timezone

from sqlalchemy.orm import Session

from data_pipeline.database.models import SalaryInsight


def save_salary_insights(
    session: Session,
    insights: dict,
) -> SalaryInsight:
    """
    Persist one salary-insights snapshot to the database.

    The caller is responsible for committing the transaction.
    """

    salary_insight = SalaryInsight(
        created_at=datetime.now(timezone.utc),
        **insights,
    )

    session.add(salary_insight)
    session.flush()

    return salary_insight
