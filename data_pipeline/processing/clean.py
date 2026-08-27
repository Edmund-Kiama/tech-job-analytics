import pandas as pd


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Required fields
    df = df.dropna(subset=["id", "title"])

    return df


def sanitize_text(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    text_columns = [
        "title",
        "description",
        "adref",
        "redirect_url",
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    return df