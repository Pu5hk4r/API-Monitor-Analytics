"""
Background scheduler for periodic monitor checks
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from app.core.config import settings
from app.core.firebase import FirestoreService
from app.services.monitor_checker import monitor_checker
from app.services.gemini_service import gemini_service
from app.services.cache_service import cache_service
from app.database.sqlite_db import (
    HealthCheckRepository, 
    DailyMetricsRepository
)

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None
firestore_service = FirestoreService()


class AlertManager:
    """Manages alert triggering and cooldowns"""
    
    def __init__(self):
        self.failure_counts = {}  # monitor_id -> consecutive failures
        self.last_alert_time = {}  # monitor_id -> last alert timestamp
    
    def should_alert(self, monitor_id: str, is_up: bool, alert_config: Dict) -> bool:
        """Determine if an alert should be triggered"""
        if not alert_config.get('alert_on_failure', True):
            return False
        
        if is_up:
            # Reset failure count on success
            self.failure_counts[monitor_id] = 0
            return False
        
        # Increment failure count
        self.failure_counts[monitor_id] = self.failure_counts.get(monitor_id, 0) + 1
        
        # Check if threshold reached
        threshold = settings.MAX_CONSECUTIVE_FAILURES
        if self.failure_counts[monitor_id] < threshold:
            return False
        
        # Check cooldown
        last_alert = self.last_alert_time.get(monitor_id)
        if last_alert:
            cooldown = timedelta(minutes=settings.ALERT_COOLDOWN_MINUTES)
            if datetime.utcnow() - last_alert < cooldown:
                return False
        
        return True
    
    def record_alert(self, monitor_id: str):
        """Record that an alert was sent"""
        self.last_alert_time[monitor_id] = datetime.utcnow()
    
    def get_failure_count(self, monitor_id: str) -> int:
        """Get consecutive failure count"""
        return self.failure_counts.get(monitor_id, 0)


alert_manager = AlertManager()


async def check_all_monitors():
    """Background job to check all active monitors"""
    try:
        logger.info("Starting monitor check cycle...")
        
        # Get all active monitors from Firestore
        monitors = await firestore_service.get_all_monitors()
        active_monitors = [m for m in monitors if m.get('is_active', True)]
        
        logger.info(f"Checking {len(active_monitors)} active monitors")
        
        # Check monitors concurrently (with limit)
        semaphore = asyncio.Semaphore(settings.MAX_WORKERS)
        
        async def check_with_semaphore(monitor):
            async with semaphore:
                return await check_single_monitor(monitor)
        
        tasks = [check_with_semaphore(monitor) for monitor in active_monitors]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('is_up'))
        failed = sum(1 for r in results if isinstance(r, dict) and not r.get('is_up'))
        errors = sum(1 for r in results if isinstance(r, Exception))
        
        logger.info(f"Monitor check completed: {successful} up, {failed} down, {errors} errors")
        
        # Cleanup old data
        HealthCheckRepository.cleanup_old_data()
        
        # Cleanup expired cache
        cache_service.cleanup_expired()
        
    except Exception as e:
        logger.error(f"Error in monitor check cycle: {str(e)}", exc_info=True)


async def check_single_monitor(monitor: Dict) -> Dict:
    """Check a single monitor and handle alerts"""
    try:
        monitor_id = monitor['id']
        
        # Perform health check
        result = await monitor_checker.check_and_record(monitor)
        
        # Update cache with current status
        cache_key = f"monitor_status:{monitor_id}"
        cache_service.set(cache_key, {
            'current_status': 'up' if result['is_up'] else 'down',
            'last_check_time': result['timestamp']
        }, ttl=settings.CACHE_TTL_SECONDS)
        
        # Check if alert should be triggered
        if alert_manager.should_alert(monitor_id, result['is_up'], monitor):
            await trigger_alert(monitor, result)
            alert_manager.record_alert(monitor_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking monitor {monitor.get('id')}: {str(e)}")
        raise


async def trigger_alert(monitor: Dict, check_result: Dict):
    """Trigger an alert for a failed monitor"""
    try:
        monitor_id = monitor['id']
        failure_count = alert_manager.get_failure_count(monitor_id)
        
        # Get AI analysis for the error
        ai_analysis = None
        try:
            error_details = {
                'status_code': check_result.get('status_code'),
                'error_message': check_result.get('error_message'),
                'response_time_ms': check_result.get('response_time_ms'),
                'consecutive_failures': failure_count
            }
            ai_analysis = await gemini_service.analyze_error(monitor, error_details)
        except Exception as e:
            logger.error(f"Failed to get AI analysis: {str(e)}")
        
        # Create alert in Firestore
        alert_data = {
            'monitor_id': monitor_id,
            'monitor_name': monitor.get('name'),
            'user_id': monitor.get('user_id'),
            'alert_type': 'monitor_down',
            'message': f"Monitor '{monitor.get('name')}' is down after {failure_count} consecutive failures",
            'details': {
                'status_code': check_result.get('status_code'),
                'error_message': check_result.get('error_message'),
                'response_time_ms': check_result.get('response_time_ms'),
                'consecutive_failures': failure_count,
                'url': str(monitor.get('url'))
            },
            'ai_analysis': ai_analysis,
            'is_resolved': False
        }
        
        await firestore_service.create_alert(alert_data)
        
        logger.info(f"Alert triggered for monitor {monitor_id}: {monitor.get('name')}")
        
    except Exception as e:
        logger.error(f"Failed to trigger alert: {str(e)}")


async def update_daily_metrics_job():
    """Background job to update daily metrics"""
    try:
        logger.info("Updating daily metrics...")
        
        monitors = await firestore_service.get_all_monitors()
        
        for monitor in monitors:
            try:
                DailyMetricsRepository.update_daily_metrics(monitor['id'])
            except Exception as e:
                logger.error(f"Failed to update metrics for {monitor['id']}: {str(e)}")
        
        logger.info("Daily metrics update completed")
        
    except Exception as e:
        logger.error(f"Error updating daily metrics: {str(e)}")


def start_scheduler():
    """Start the background scheduler"""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running")
        return
    
    scheduler = AsyncIOScheduler()
    
    # Add monitor check job (every 5 minutes by default)
    scheduler.add_job(
        check_all_monitors,
        trigger=IntervalTrigger(minutes=settings.MONITOR_CHECK_INTERVAL_MINUTES),
        id='check_monitors',
        name='Check all monitors',
        replace_existing=True
    )
    
    # Add daily metrics update job (every hour)
    scheduler.add_job(
        update_daily_metrics_job,
        trigger=IntervalTrigger(hours=1),
        id='update_metrics',
        name='Update daily metrics',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Background scheduler started")


def stop_scheduler():
    """Stop the background scheduler"""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Background scheduler stopped")
