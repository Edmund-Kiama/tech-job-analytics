from pathlib import Path



def get_latest_bronze_file() -> Path:
    bronze_dir = Path("data/bronze")
    files = sorted(bronze_dir.glob("adzuna_*.json"))

    if not files:
        raise FileNotFoundError("No Bronze JSON files found in data/bronze.")

    return files[-1]