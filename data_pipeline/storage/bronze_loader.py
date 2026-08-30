import json
from pathlib import Path
from typing import Union

import pandas as pd

# def load_bronze_json(file_path: Union[str, Path]) -> pd.DataFrame:
#     file_path = Path(file_path)

#     with file_path.open("r", encoding="utf-8") as file:
#         payload = json.load(file)

#     jobs = []

#     for page in payload["pages"]:
#         jobs.extend(page.get("results", []))

#     return pd.DataFrame(jobs)


def load_bronze_json(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load an Adzuna Bronze JSON file into a Pandas DataFrame.

    Supports both:
    1. Paginated Bronze payloads:
       {
           "pages": [
               {"results": [...]},
               ...
           ]
       }

    2. A single Adzuna response:
       {
           "results": [...]
       }

    3. A raw list of job records:
       [
           {...},
           {...}
       ]
    """

    file_path = Path(file_path)

    with file_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if isinstance(payload, dict):
        if "pages" in payload:
            jobs = []

            for page in payload["pages"]:
                jobs.extend(page.get("results", []))

        elif "results" in payload:
            jobs = payload["results"]

        else:
            raise ValueError(
                "Unsupported Bronze JSON structure: expected 'pages' or 'results'."
            )

    elif isinstance(payload, list):
        jobs = payload

    else:
        raise ValueError(
            "Unsupported Bronze JSON structure: expected a dictionary or list."
        )

    return pd.DataFrame(jobs)
