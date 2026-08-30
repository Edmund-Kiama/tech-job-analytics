import json

import pandas as pd

from data_pipeline.processing.transform import transform_dataframe
from data_pipeline.storage.bronze_loader import load_bronze_json


def test_full_pandas_transformation(tmp_path):

    fake_jobs = [
        {
            "id": "clean-1",
            "title": "Python Developer",
            "description": "Python backend developer",
            "created": "2026-08-29T10:00:00Z",
            "salary_min": 40000,
            "salary_max": 60000,
            "salary_is_predicted": "0",
            "company": {"display_name": "Company A"},
            "category": {"label": "IT Jobs", "tag": "it-jobs"},
            "location": {
                "display_name": "London",
                "area": ["UK", "England", "London"],
            },
        },
        {
            "id": "clean-2",
            "title": "Data Engineer",
            "description": "Data engineering role",
            "created": "2026-08-29T11:00:00Z",
            "salary_min": 50000,
            "salary_max": 70000,
            "salary_is_predicted": "0",
            "company": {"display_name": "Company B"},
            "category": {"label": "IT Jobs", "tag": "it-jobs"},
            "location": {
                "display_name": "Manchester",
                "area": ["UK", "England", "Manchester"],
            },
        },
        {
            "id": "clean-3",
            "title": "Software Engineer",
            "description": "Software engineering role",
            "created": "2026-08-29T12:00:00Z",
            "salary_min": 60000,
            "salary_max": 80000,
            "salary_is_predicted": "0",
            "company": {"display_name": "Company C"},
            "category": {"label": "IT Jobs", "tag": "it-jobs"},
            "location": {
                "display_name": "Birmingham",
                "area": ["UK", "England", "Birmingham"],
            },
        },
    ]

    bronze_file = tmp_path / "adzuna_test.json"

    bronze_file.write_text(
        json.dumps(
            {
                "results": fake_jobs,
                "count": len(fake_jobs),
            }
        ),
        encoding="utf-8",
    )

    df = load_bronze_json(bronze_file)

    print("\nBefore transformation:")
    print(df.shape)

    df = transform_dataframe(df)

    print("\nAfter transformation:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nDtypes:")
    print(df.dtypes)

    print("\nNormalized location:")
    print(
        df[
            [
                "location_name",
                "country",
                "region",
                "city",
            ]
        ]
        .head()
        .to_string(index=False)
    )

    print("\nSalary data:")
    print(
        df[
            [
                "salary_min",
                "salary_max",
                "salary_is_predicted",
                "salary_currency",
                "salary_period",
                "normalized_salary_min",
                "normalized_salary_max",
                "normalized_salary_midpoint",
            ]
        ].to_string(index=False)
    )

    print("\nSalary summary:")
    print(
        df[
            [
                "normalized_salary_min",
                "normalized_salary_max",
                "normalized_salary_midpoint",
            ]
        ].describe()
    )

    # --------------------------------------------------
    # Basic dataset validation
    # --------------------------------------------------

    assert len(df) > 0

    # --------------------------------------------------
    # Location validation
    # --------------------------------------------------

    assert "company_name" in df.columns
    assert "category_label" in df.columns
    assert "category_tag" in df.columns

    assert "location_name" in df.columns
    assert "country" in df.columns
    assert "region" in df.columns
    assert "city" in df.columns

    # --------------------------------------------------
    # Salary validation
    # --------------------------------------------------

    assert "salary_currency" in df.columns
    assert "salary_period" in df.columns
    assert "normalized_salary_min" in df.columns
    assert "normalized_salary_max" in df.columns
    assert "normalized_salary_midpoint" in df.columns

    assert (df["salary_currency"] == "GBP").all()
    assert (df["salary_period"] == "annual").all()

    # Zero minimum salaries must become missing.
    assert not (df["salary_min"] == 0).any()

    # At least some salaries should have valid maximum values.
    assert df["normalized_salary_max"].notna().any()

    # Median must never be below the available minimum.
    valid_min = df["normalized_salary_min"].notna()
    assert (
        df.loc[valid_min, "normalized_salary_midpoint"]
        >= df.loc[valid_min, "normalized_salary_min"]
    ).all()

    # Median must never exceed the available maximum.
    valid_max = df["normalized_salary_max"].notna()
    assert (
        df.loc[valid_max, "normalized_salary_midpoint"]
        <= df.loc[valid_max, "normalized_salary_max"]
    ).all()

    # --------------------------------------------------
    # dtype validation
    # --------------------------------------------------

    assert str(df["id"].dtype) == "string"
    assert str(df["title"].dtype) == "string"
    assert str(df["description"].dtype) == "string"
    assert str(df["salary_currency"].dtype) == "string"
    assert str(df["salary_period"].dtype) == "string"
    assert str(df["salary_is_predicted"].dtype) == "boolean"

    assert pd.api.types.is_datetime64tz_dtype(df["created"])

    assert pd.api.types.is_numeric_dtype(df["normalized_salary_min"])

    assert pd.api.types.is_numeric_dtype(df["normalized_salary_max"])

    assert pd.api.types.is_numeric_dtype(df["normalized_salary_midpoint"])
