import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
    ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
    ADZUNA_COUNTRY = os.getenv("ADZUNA_COUNTRY", "gb")
    ADZUNA_BASE_URL = os.getenv(
        "ADZUNA_BASE_URL",
        "https://api.adzuna.com/v1/api",
    )
    ADZUNA_RESULTS_PER_PAGE=os.getenv("ADZUNA_RESULTS_PER_PAGE")
    ADZUNA_MAX_JOBS=os.getenv("ADZUNA_MAX_JOBS")
    ADZUNA_MAX_PAGES=os.getenv("ADZUNA_MAX_PAGES")
    ADZUNA_SORT_BY=os.getenv("ADZUNA_SORT_BY")
    ADZUNA_MAX_DAYS_OLD=os.getenv("ADZUNA_MAX_DAYS_OLD")
    ADZUNA_STALE_AFTER_DAYS=os.getenv("ADZUNA_STALE_AFTER_DAYS")



settings = Settings()
