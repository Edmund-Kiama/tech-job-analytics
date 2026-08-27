from pathlib import Path

from data_pipeline.pandas_loader import load_bronze_json


bronze_dir = Path("data/bronze")
bronze_files = sorted(bronze_dir.glob("adzuna_*.json"))

if not bronze_files:
    raise FileNotFoundError("No Bronze JSON files found.")

latest_file = bronze_files[-1]

df = load_bronze_json(latest_file)


print("=" * 60)
print("DATASET SHAPE")
print("=" * 60)
print(df.shape)


print("\n" + "=" * 60)
print("DATA TYPES")
print("=" * 60)
print(df.dtypes)


print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)
print(df.isna().sum())


print("\n" + "=" * 60)
print("MISSING VALUE PERCENTAGE")
print("=" * 60)
print((df.isna().mean() * 100).round(2))


print("\n" + "=" * 60)
print("UNIQUE VALUES")
print("=" * 60)

for column in df.columns:
    print(f"\n{column}:")

    non_null = df[column].dropna()

    if non_null.empty:
        print("No non-null values")
        continue

    first_value = non_null.iloc[0]

    if isinstance(first_value, dict):
        print("Nested dictionary field")
        print(first_value)
    else:
        print(non_null.unique()[:20])

print("\n" + "=" * 60)
print("SAMPLE NESTED OBJECTS")
print("=" * 60)

for column in ["company", "category", "location"]:
    print(f"\n{column.upper()}:")

    non_null = df[column].dropna()

    if not non_null.empty:
        print(non_null.iloc[0])