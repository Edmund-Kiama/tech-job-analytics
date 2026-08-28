from typing import List

import pandas as pd


TEXT_COLUMNS = [
    "title",
    "description",
    "adref",
    "redirect_url",
]


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values according to field semantics.

    Only records missing required identity fields are removed.
    Optional fields remain missing.
    """
    df = df.copy()

    df = df.dropna(subset=["id", "title"])

    return df


def sanitize_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize whitespace and convert empty strings to missing values.
    """
    df = df.copy()

    for column in TEXT_COLUMNS:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
                .replace("", pd.NA)
            )

    return df


def flatten_nested_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract useful values from Adzuna's nested company,
    category, and location objects.
    """
    df = df.copy()

    df["company_name"] = df["company"].apply(
        lambda value: (
            value.get("display_name")
            if isinstance(value, dict)
            else pd.NA
        )
    )

    df["category_label"] = df["category"].apply(
        lambda value: (
            value.get("label")
            if isinstance(value, dict)
            else pd.NA
        )
    )

    df["category_tag"] = df["category"].apply(
        lambda value: (
            value.get("tag")
            if isinstance(value, dict)
            else pd.NA
        )
    )

    df["location_name"] = df["location"].apply(
        lambda value: (
            value.get("display_name")
            if isinstance(value, dict)
            else pd.NA
        )
    )

    return df


def normalize_location(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize Adzuna's location.area hierarchy.

    Example:

        ['UK', 'South West England', 'Dorset',
         'Poole', 'Parkstone']

    becomes:

        country = UK
        region  = South West England
        city    = Poole
    """
    df = df.copy()

    def extract_area(value) -> List[str]:
        if not isinstance(value, dict):
            return []

        area = value.get("area")

        if not isinstance(area, list):
            return []

        return [
            str(item).strip()
            for item in area
            if item is not None and str(item).strip()
        ]

    areas = df["location"].apply(extract_area)

    df["country"] = areas.apply(
        lambda area: area[0] if len(area) >= 1 else pd.NA
    )

    df["region"] = areas.apply(
        lambda area: area[1] if len(area) >= 2 else pd.NA
    )

    df["city"] = areas.apply(
        lambda area: (
            area[-2]
            if len(area) >= 4
            else area[-1]
            if len(area) >= 3
            else pd.NA
        )
    )

    return df


def normalize_salary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize Adzuna salary data for the GB pipeline.

    Rules:
    - salary values are numeric
    - zero salary values are treated as missing
    - currency is GBP
    - salary period is annual
    - original API salary fields are preserved
    - normalized median uses the available salary bound
    """
    df = df.copy()

    df["salary_min"] = pd.to_numeric(
        df["salary_min"],
        errors="coerce",
    )

    df["salary_max"] = pd.to_numeric(
        df["salary_max"],
        errors="coerce",
    )

    # Adzuna uses 0 where a meaningful minimum salary
    # has not been supplied.
    df.loc[df["salary_min"] == 0, "salary_min"] = pd.NA
    df.loc[df["salary_max"] == 0, "salary_max"] = pd.NA

    # This pipeline currently targets the GB endpoint.
    df["salary_currency"] = pd.Series(
        "GBP",
        index=df.index,
        dtype="string",
    )

    df["salary_period"] = pd.Series(
        "annual",
        index=df.index,
        dtype="string",
    )

    df["normalized_salary_min"] = df["salary_min"]
    df["normalized_salary_max"] = df["salary_max"]

    # Both bounds available:
    # midpoint = (minimum + maximum) / 2
    both_available = (
        df["salary_min"].notna()
        & df["salary_max"].notna()
    )

    df.loc[
        both_available,
        "normalized_salary_midpoint",
    ] = (
        df.loc[both_available, "salary_min"]
        + df.loc[both_available, "salary_max"]
    ) / 2

    # Only minimum available.
    only_min = (
        df["salary_min"].notna()
        & df["salary_max"].isna()
    )

    df.loc[
        only_min,
        "normalized_salary_midpoint",
    ] = df.loc[only_min, "salary_min"]

    # Only maximum available.
    only_max = (
        df["salary_min"].isna()
        & df["salary_max"].notna()
    )

    df.loc[
        only_max,
        "normalized_salary_midpoint",
    ] = df.loc[only_max, "salary_max"]

    return df


def enforce_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enforce explicit Pandas data types.
    """
    df = df.copy()

    string_columns = [
        "id",
        "title",
        "description",
        "created",
        "redirect_url",
        "contract_time",
        "contract_type",
        "company_name",
        "category_label",
        "category_tag",
        "location_name",
        "country",
        "region",
        "city",
        "adref",
        "__CLASS__",
        "salary_currency",
        "salary_period",
    ]

    for column in string_columns:
        if column in df.columns:
            df[column] = df[column].astype("string")

    numeric_columns = [
        "salary_min",
        "salary_max",
        "normalized_salary_min",
        "normalized_salary_max",
        "normalized_salary_midpoint",
        "latitude",
        "longitude",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    if "salary_is_predicted" in df.columns:
        df["salary_is_predicted"] = (
            df["salary_is_predicted"]
            .map({
                0: False,
                1: True,
                "0": False,
                "1": True,
                True: True,
                False: False,
            })
            .astype("boolean")
        )

    if "created" in df.columns:
        df["created"] = pd.to_datetime(
            df["created"],
            errors="coerce",
            utc=True,
        )

    return df