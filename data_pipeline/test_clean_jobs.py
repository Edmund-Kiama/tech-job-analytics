from pathlib import Path

from data_pipeline.pandas_loader import load_bronze_json
from data_pipeline.clean_jobs import handle_missing_values, sanitize_text

bronze_dir = Path("data/bronze")
bronze_files = sorted(bronze_dir.glob("adzuna_*.json"))

if not bronze_files:
    raise FileNotFoundError("No Bronze JSON files found.")

latest_file = bronze_files[-1]

df = load_bronze_json(latest_file)

print("Before cleaning:")
print(f"Rows: {len(df)}")

df = handle_missing_values(df)
df = sanitize_text(df)

print("\nText columns:")
print(df[[
    "title",
    "description",
    "adref",
    "redirect_url",
]].head())

print("\nAfter cleaning:")
print(f"Rows: {len(df)}")

print("\nMissing values:")
print(df.isna().sum())

print("\n" + "=" * 60)
print("SAMPLE DESCRIPTION")
print("=" * 60)

print(df["description"].iloc[0])

print("\n" + "=" * 60)
print("SALARY DATA")
print("=" * 60)

print(
    df[
        [
            "salary_min",
            "salary_max",
            "salary_is_predicted",
            "contract_time",
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 60)
print("SALARY SUMMARY")
print("=" * 60)

print(df["salary_min"].describe())
print(df["salary_max"].describe())