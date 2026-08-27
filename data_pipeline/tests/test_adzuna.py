from data_pipeline.clients.adzuna import AdzunaClient
from data_pipeline.utils.console import CommentPrinter


client = AdzunaClient()

# data = client.search_jobs()

# CommentPrinter(f"Response received\nNumber of jobs: {len(data.get('results', []))}")

# if data.get("results"):
#     first_job = data["results"][0]

# CommentPrinter(f"First job:\nID: {first_job.get('id')}\nTitle: {first_job.get('title')}")

count = 0

for job in client.iter_jobs(max_pages=3):
    count += 1
    CommentPrinter(
        f"""
        Job {count}
        ID: {job.get('id')}
        Title: {job.get('title')}
        """
    )

print()
CommentPrinter(f"Total jobs: {count}")