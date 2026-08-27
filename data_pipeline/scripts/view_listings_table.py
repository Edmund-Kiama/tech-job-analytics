from data_pipeline.database import SessionLocal, Listing
from data_pipeline.utils.console import CommentPrinter


with SessionLocal() as session:
    listings = session.query(Listing).all()

    CommentPrinter(f"Total listings: {len(listings)}")

    for listing in listings[:5]:
        CommentPrinter(f"Listing ID: {listing.id}, Title: {listing.title}, Company: {listing.company_name}")