from sqlalchemy import inspect, text

from data_pipeline.database.connection import engine


def migrate():
    inspector = inspect(engine)
    existing_columns = {column["name"] for column in inspector.get_columns("listings")}

    # Define column DDL compatible with SQLite ALTER TABLE rules
    new_columns = {
        "first_seen_at": "DATETIME",
        "last_seen_at": "DATETIME",
        "is_active": "BOOLEAN NOT NULL DEFAULT 1",  # '1' is a literal constant, so this works
        "inactive_at": "DATETIME",
    }

    with engine.begin() as connection:
        # 1. Add missing columns
        for column_name, definition in new_columns.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE listings ADD COLUMN {column_name} {definition}")
                )

        # 2. Backfill timestamps for existing rows
        if "first_seen_at" not in existing_columns:
            connection.execute(
                text(
                    "UPDATE listings SET first_seen_at = CURRENT_TIMESTAMP WHERE first_seen_at IS NULL"
                )
            )
        if "last_seen_at" not in existing_columns:
            connection.execute(
                text(
                    "UPDATE listings SET last_seen_at = CURRENT_TIMESTAMP WHERE last_seen_at IS NULL"
                )
            )

    print("2.5-B Listing tracking migration complete.")


if __name__ == "__main__":
    migrate()
