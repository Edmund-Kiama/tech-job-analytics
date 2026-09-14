from sqlalchemy import inspect, text

from data_pipeline.database.connection import engine


def migrate():

    inspector = inspect(engine)

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("ingestion_runs")
    }

    # Define column DDL compatible with SQLite ALTER TABLE rules
    new_columns = {
        "job_deleted": "BOOLEAN NOT NULL DEFAULT 0",
    }

    with engine.begin() as connection:

        # Add missing columns
        for column_name, definition in new_columns.items():

            if column_name not in existing_columns:

                connection.execute(
                    text(
                        f"ALTER TABLE ingestion_runs "
                        f"ADD COLUMN {column_name} {definition}"
                    )
                )

    print("ingestion_runs job_deleted migration complete.")


if __name__ == "__main__":
    migrate()