from data_pipeline.adzuna_client import AdzunaClient
from data_pipeline.raw_storage import save_raw_payload
from data_pipeline.helper import CommentPrinter


client = AdzunaClient()

data = client.search_jobs(page=1)

file_path = save_raw_payload(data)

CommentPrinter(f"Raw payload saved: {file_path}")

