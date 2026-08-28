import json
from datetime import datetime, timezone
from pathlib import Path

BRONZE_DIR = Path("data/bronze")


def save_raw_payload(payload: dict) -> Path:
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    file_path = BRONZE_DIR / f"adzuna_{timestamp}.json"

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return file_path
