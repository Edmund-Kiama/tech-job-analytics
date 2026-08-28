import pandas as pd

from data_pipeline.processing.transform import transform_dataframe
from data_pipeline.storage.bronze_loader import load_bronze_json
from data_pipeline.utils.helper import get_latest_bronze_file


def test_full_pandas_transformation():
    bronze_file = get_latest_bronze_file()

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
