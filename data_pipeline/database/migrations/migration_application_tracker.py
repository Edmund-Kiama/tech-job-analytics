from sqlalchemy import inspect, text

from data_pipeline.database.connection import engine


def migrate():
    inspector = inspect(engine)
    existing_columns = {column["name"] for column in inspector.get_columns("listings")}

    # Define column DDL compatible with SQLite ALTER TABLE rules
    new_columns = {
        "application_status": "VARCHAR NOT NULL DEFAULT 'NEW'",
        "saved_at": "DATETIME",
        "applied_at": "DATETIME",
        "follow_up_at": "DATETIME",
        "user_priority": "INTEGER",
        "application_notes": "TEXT",
    }

    with engine.begin() as connection:
        # 1. Add missing columns
        for column_name, definition in new_columns.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(f"ALTER TABLE listings ADD COLUMN {column_name} {definition}")
                )

        # 2. Backfill existing rows to ensure application_status is set to 'NEW'
        if "application_status" not in existing_columns:
            connection.execute(
                text(
                    "UPDATE listings SET application_status = 'NEW' WHERE application_status IS NULL"
                )
            )

    print("3. Application tracking migration complete.")


if __name__ == "__main__":
    migrate()