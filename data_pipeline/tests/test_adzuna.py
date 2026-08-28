from data_pipeline.clients.adzuna import AdzunaClient
from data_pipeline.utils.console import CommentPrinter


client = AdzunaClient()

count = 0

for job in client.iter_jobs(max_pages=3):
    count += 1
    print(
        f"""
        Job {count}
        salary_min: {job.get('salary_min')}
        salary_max: {job.get('salary_max')}
        salary_is_predicted: {job.get('salary_is_predicted')}
        contract_time: {job.get('contract_time')}
        contract_type: {job.get('contract_type')}

        """
    )

print()
CommentPrinter(f"Total jobs: {count}")