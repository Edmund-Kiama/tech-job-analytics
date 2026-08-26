from data_pipeline.adzuna_client import AdzunaClient
from data_pipeline.helper import CommentPrinter


client = AdzunaClient()

# data = client.search_jobs()

# CommentPrinter(f"Response received\nNumber of jobs: {len(data.get('results', []))}")

# if data.get("results"):
#     first_job = data["results"][0]

# CommentPrinter(f"First job:\nID: {first_job.get('id')}\nTitle: {first_job.get('title')}")

count = 0

for job in client.iter_jobs(max_pages=3):
    count += 1
    CommentPrinter(f"Job {count}:\nID: {job.get('id')}\nTitle: {job.get('title')}")

print()
CommentPrinter(f"Total jobs: {count}")