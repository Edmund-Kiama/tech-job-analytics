from pathlib import Path

from data_pipeline.pandas_loader import load_bronze_json


bronze_dir = Path("data/bronze")

bronze_files = sorted(bronze_dir.glob("adzuna_*.json"))

if not bronze_files:
    raise FileNotFoundError("No Bronze JSON files found.")

latest_file = bronze_files[-1]

df = load_bronze_json(latest_file)

print("=" * 50)
print("Bronze file:")
print(latest_file)

print("=" * 50)
print("DataFrame shape:")
print(df.shape)

print("=" * 50)
print("Columns:")
print(df.columns.tolist())

print("=" * 50)
print("First 5 jobs:")
print(df.head())