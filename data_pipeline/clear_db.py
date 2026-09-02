import sys

from sqlalchemy import text

from data_pipeline.database.connection import SessionLocal

TABLES = [
    "salary_insights",
    "listing_history",
    "listings",
    "ingestion_runs",
]


def clear_database():
    session = SessionLocal()
    try:
        print("Clearing database tables...")
        for table in TABLES:
            result = session.execute(text(f"DELETE FROM {table}"))
            print(f"  - Cleared table '{table}' ({result.rowcount} rows removed)")
        session.commit()
        print("Done! All specified tables cleared successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error clearing database: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    clear_database()
