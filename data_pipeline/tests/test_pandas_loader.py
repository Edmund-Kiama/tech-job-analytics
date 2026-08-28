from data_pipeline.storage.bronze_loader import load_bronze_json
from data_pipeline.utils.helper import get_latest_bronze_file

latest_file = get_latest_bronze_file()

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
