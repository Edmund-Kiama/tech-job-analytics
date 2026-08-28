import json
from pathlib import Path
from typing import Union

import pandas as pd


def load_bronze_json(file_path: Union[str, Path]) -> pd.DataFrame:
    file_path = Path(file_path)

    with file_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    jobs = []

    for page in payload["pages"]:
        jobs.extend(page.get("results", []))

    return pd.DataFrame(jobs)
