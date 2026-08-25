from fastapi import FastAPI
from sqlalchemy.orm import Session

from data_pipeline.database import Listing, engine

app = FastAPI(
    title="Tech Job Analytics API",
    version="0.1.0"
)

@app.get("/jobs")
async def get_jobs():
    with Session(engine) as session:
        listings = session.query(Listing).all()

        return [
            {
                "id": listing.id,
                "title": listing.title,
                "description": listing.description,
                "created": listing.created,
                "redirect_url": listing.redirect_url,
                "salary_min": listing.salary_min,
                "salary_max": listing.salary_max,
                "salary_is_predicted": listing.salary_is_predicted,
                "contract_time": listing.contract_time,
                "contract_type": listing.contract_type,
                "company_name": listing.company_name,
                "category_label": listing.category_label,
                "category_tag": listing.category_tag,
                "location_name": listing.location_name,
                "latitude": listing.latitude,
                "longitude": listing.longitude 
            } 
            for listing in listings
        ]