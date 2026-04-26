"""Subscription scheduling tasks."""
from datetime import datetime
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.subscription import subscription_service

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def process_subscriptions_task():
    """Background task to process recurring subscriptions."""
    db = SessionLocal()
    try:
        logger.info("Starting subscription processing task...")
        results = subscription_service.process_recurring_orders(db)
        logger.info(f"Subscription processing completed: {results}")
    except Exception as e:
        logger.error(f"Error in subscription processing task: {str(e)}")
    finally:
        db.close()


def start_subscription_scheduler():
    """Start the APScheduler scheduler."""
    if not scheduler.running:
        # Run every day at 2 AM
        scheduler.add_job(
            process_subscriptions_task,
            'cron',
            hour=2,
            minute=0,
            id='process_subscriptions',
            name='Process Recurring Subscriptions',
            max_instances=1
        )
        scheduler.start()
        logger.info("Subscription scheduler started")


def stop_subscription_scheduler():
    """Stop the APScheduler scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Subscription scheduler stopped")