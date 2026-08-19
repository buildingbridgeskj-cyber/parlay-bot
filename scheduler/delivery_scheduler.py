from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeliveryScheduler:
    """Manages daily parlay delivery at 9:00 a.m. EST"""
    
    def __init__(self, delivery_hour=9, delivery_minute=0, timezone="US/Eastern"):
        self.scheduler = BackgroundScheduler()
        self.delivery_hour = delivery_hour
        self.delivery_minute = delivery_minute
        self.timezone = timezone
        self.is_running = False
    
    def start(self, job_func):
        """Start the scheduler with the delivery job"""
        try:
            # Schedule job to run daily at 9:00 AM EST
            self.scheduler.add_job(
                job_func,
                CronTrigger(
                    hour=self.delivery_hour,
                    minute=self.delivery_minute,
                    timezone=self.timezone
                ),
                id='parlay_delivery',
                name='Daily Parlay Delivery',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"Scheduler started. Delivery set for {self.delivery_hour}:{self.delivery_minute:02d} {self.timezone}")
            return True
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            return False
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("Scheduler stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
            return False
    
    def get_status(self):
        """Get scheduler status"""
        return {
            'is_running': self.is_running,
            'delivery_time': f"{self.delivery_hour}:{self.delivery_minute:02d}",
            'timezone': self.timezone,
            'next_delivery': str(self.scheduler.get_job('parlay_delivery').next_run_time) if self.is_running else 'Not scheduled'
        }
