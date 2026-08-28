from data_pipeline.clients.adzuna import AdzunaClient
from data_pipeline.storage.raw import save_raw_payload
from data_pipeline.utils.console import CommentPrinter

client = AdzunaClient()

data = client.search_jobs(page=1)

file_path = save_raw_payload(data)

CommentPrinter(f"Raw payload saved: {file_path}")
