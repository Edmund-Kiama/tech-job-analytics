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


settings = Settings()
