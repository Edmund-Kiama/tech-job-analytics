import json

from data_pipeline.storage.bronze_loader import load_bronze_json


def test_load_bronze_json(tmp_path):
    payload = {
        "results": [
            {
                "id": "test-1",
                "title": "Python Developer",
                "description": "Python backend developer",
            },
            {
                "id": "test-2",
                "title": "Data Engineer",
                "description": "Data engineering role",
            },
        ],
        "count": 2,
    }

    bronze_file = tmp_path / "adzuna_test.json"

    bronze_file.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    df = load_bronze_json(bronze_file)

    assert len(df) == 2
    assert "id" in df.columns
    assert "title" in df.columns
    assert "description" in df.columns

    print("=" * 50)
    print("Bronze file:")
    print(bronze_file)
    print("=" * 50)
    print("DataFrame shape:")
    print(df.shape)
    print("=" * 50)
    print("Columns:")
    print(df.columns.tolist())
    print("=" * 50)
    print("First 5 jobs:")
    print(df.head())
