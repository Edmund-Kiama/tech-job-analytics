from fastapi import APIRouter

from backend.api.schemas import FlexibleResponse
from backend.services import analytics

router = APIRouter(prefix="/analytics")
for path, handler in [
    ("/prioritization/{job_id}", analytics.get_job_prioritization),
    ("/prioritization", analytics.get_prioritized_jobs),
    ("/metadata", analytics.get_analytics_metadata),
    ("/trends", analytics.get_analytics_trends),
    ("/summary", analytics.get_analytics_summary),
    ("/salary", analytics.get_salary_analytics),
    ("/breakdown", analytics.get_analytics_breakdown),
    ("/categories", analytics.get_categories),
    ("/categories/{category}", analytics.get_category_analytics),
    ("/salary/distribution", analytics.get_salary_distribution),
]:
    router.add_api_route(
        path,
        handler,
        methods=["GET"],
        response_model=FlexibleResponse,
    )
