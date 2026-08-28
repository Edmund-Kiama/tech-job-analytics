import requests
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from data_pipeline.config import settings


# helper
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

    @retry(
        retry=retry_if_exception(is_retryable_exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
    )
    def search_jobs(self, page: int = 1):
        url = f"{self.base_url}/jobs/{self.country}/search/{page}"

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
        }

        response = requests.get(url, params=params)

        response.raise_for_status()

        return response.json()

    def iter_jobs(self, max_pages: int = 100):
        for page in range(1, max_pages + 1):
            data = self.search_jobs(page)
            results = data.get("results", [])

            if not results:
                break

            for job in results:
                yield job

    def iter_pages(self, max_pages: int = 100):
        for page in range(1, max_pages + 1):
            data = self.search_jobs(page)

            results = data.get("results", [])

            if not results:
                break

            yield data
