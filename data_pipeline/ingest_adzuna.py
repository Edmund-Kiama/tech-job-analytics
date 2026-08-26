from sqlalchemy.dialects.sqlite import insert

from data_pipeline.adzuna_client import AdzunaClient
from data_pipeline.database import Listing, SessionLocal
from data_pipeline.transform import transform_adzuna_job
from data_pipeline.helper import CommentPrinter


def ingest_jobs(max_pages: int = 3):
    client = AdzunaClient()

    processed = 0

    with SessionLocal() as session:
        for item in client.iter_jobs(max_pages=max_pages):
            listing_data = transform_adzuna_job(item)

            stmt = insert(Listing).values(**listing_data)

            stmt = stmt.on_conflict_do_update(
                index_elements=[Listing.id],
                set_=listing_data,
            )

            session.execute(stmt)

            processed += 1

        session.commit()

    CommentPrinter(f"Successfully synchronized {processed} jobs.")


if __name__ == "__main__":
    ingest_jobs(max_pages=3)