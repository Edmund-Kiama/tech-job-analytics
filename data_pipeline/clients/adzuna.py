from typing import Optional

import requests
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from data_pipeline.config import settings


def is_retryable_exception(exception):
    if not isinstance(exception, requests.HTTPError):
        return False

    response = exception.response

    if response is None:
        return False

    return response.status_code == 429 or 500 <= response.status_code <= 599


class AdzunaClient:
    def __init__(self):
        self.base_url = settings.ADZUNA_BASE_URL
        self.app_id = settings.ADZUNA_APP_ID
        self.app_key = settings.ADZUNA_APP_KEY
        self.country = settings.ADZUNA_COUNTRY

        self.results_per_page = min(
            int(settings.ADZUNA_RESULTS_PER_PAGE),
            50,
        )

        self.max_jobs = int(settings.ADZUNA_MAX_JOBS)
        self.max_pages = int(settings.ADZUNA_MAX_PAGES)

    @retry(
        retry=retry_if_exception(is_retryable_exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(
            multiplier=1,
            min=2,
            max=8,
        ),
    )
    def search_jobs(self, page: int = 1):
        url = f"{self.base_url}/jobs/{self.country}/search/{page}"

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": self.results_per_page,
            "sort_by": settings.ADZUNA_SORT_BY,
            "max_days_old": int(settings.ADZUNA_MAX_DAYS_OLD),
            "content-type": "application/json",
        }

        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def iter_pages(
        self,
        max_pages: Optional[int] = None,
        max_jobs: Optional[int] = None,
    ):
        """
        Yield complete Adzuna API page responses.

        max_jobs limits the total number of jobs returned,
        while max_pages provides an additional API-call safety limit.
        """

        max_pages = max_pages or self.max_pages
        max_jobs = max_jobs or self.max_jobs

        jobs_seen = 0

        for page in range(1, max_pages + 1):
            if jobs_seen >= max_jobs:
                break

            data = self.search_jobs(page)

            results = data.get("results", [])

            if not results:
                break

            remaining = max_jobs - jobs_seen

            if len(results) > remaining:
                results = results[:remaining]

                data = {
                    **data,
                    "results": results,
                }

            jobs_seen += len(results)

            yield data

            if len(results) < self.results_per_page:
                break

    def iter_jobs(
        self,
        max_pages: Optional[int] = None,
        max_jobs: Optional[int] = None,
    ):
        """
        Yield individual jobs across paginated API responses.
        """

        for page in self.iter_pages(
            max_pages=max_pages,
            max_jobs=max_jobs,
        ):
            for job in page.get("results", []):
                yield job
