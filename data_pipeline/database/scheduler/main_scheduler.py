import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from data_pipeline.config import settings
from data_pipeline.services.pipeline import run_pipeline

logger = logging.getLogger(__name__)


def execute_daily_ingestion():
    logger.info("APScheduler triggering daily ingestion job...")
    try:
        summary = run_pipeline(
            max_pages=int(settings.ADZUNA_MAX_PAGES),
            analysis_version=settings.ADZUNA_ANALYSIS_VERSION,
        )
        logger.info(f"Job complete: {summary}")
    except Exception as exc:
        logger.error(f"Job failed during execution: {exc}", exc_info=True)


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="UTC")

    # Schedule to run every day at 02:00 AM UTC
    scheduler.add_job(
        func=execute_daily_ingestion,
        trigger=CronTrigger(hour=2, minute=0),
        id="adzuna_daily_etl",
        name="Adzuna Daily Ingestion and Analytics",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping executions if a run hangs
    )

    scheduler.start()
    logger.info("Pipeline scheduler initialized.")
    return scheduler
