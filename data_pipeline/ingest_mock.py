import json
from sqlalchemy.orm import Session
from database import Listing, engine
from helper import CommentPrinter


def ingest_mock_data(json_file: str):
    with open(json_file, "r") as f:
        data = json.load(f)

    CommentPrinter(f"Ingesting mock data from {json_file}...")

    with Session(engine) as session:
        try:
            for item in data["results"]:
                listing = Listing(
                    id=item.get("id"),
                    title=item.get("title"),
                    description=item.get("description"),
                    created=item.get("created"),
                    redirect_url=item.get("redirect_url"),
                    salary_min=item.get("salary_min"),
                    salary_max=item.get("salary_max"),
                    salary_is_predicted=item.get("salary_is_predicted"),
                    contract_time=item.get("contract_time"),
                    contract_type=item.get("contract_type"),
                    company_name=item.get("company", {}).get("display_name"),
                    category_label=item.get("category", {}).get("label"),
                    category_tag=item.get("category", {}).get("tag"),
                    location_name=item.get("location", {}).get("display_name"),
                    latitude=item.get("latitude"),
                    longitude=item.get("longitude"),
                )

                session.add(listing)

            session.commit()
            CommentPrinter("Mock data ingested successfully.")

        except Exception:
            session.rollback()
            CommentPrinter("Error occurred while ingesting mock data. Rolling back changes.")
            raise


if __name__ == "__main__":
    ingest_mock_data("data/mock_jobs.json")