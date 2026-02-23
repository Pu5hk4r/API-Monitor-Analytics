"""
Metrics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
import logging

from app.models.schemas import MetricsResponse, DailyMetricsResponse
from app.core.firebase import verify_firebase_token, FirestoreService
from app.database.sqlite_db import HealthCheckRepository, DailyMetricsRepository

router = APIRouter()
logger = logging.getLogger(__name__)
firestore_service = FirestoreService()


@router.get("/{monitor_id}", response_model=MetricsResponse)
async def get_monitor_metrics(
    monitor_id: str,
    hours: int = 24,
    user_data: Dict = Depends(verify_firebase_token)
):
    """Get metrics for a specific monitor"""
    try:
        # Verify ownership
        monitor = await firestore_service.get_monitor(monitor_id)
        
        if not monitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitor not found"
            )
        
        if monitor['user_id'] != user_data['uid']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this monitor"
            )
        
        # Get metrics
        stats = HealthCheckRepository.get_uptime_stats(monitor_id, hours=hours)
        percentiles = HealthCheckRepository.get_response_time_percentiles(monitor_id, hours=hours)
        
        error_rate = (stats['failed_checks'] / stats['total_checks'] * 100) if stats['total_checks'] > 0 else 0
        
        return {
            "monitor_id": monitor_id,
            "time_period": f"{hours} hours",
            "total_checks": stats['total_checks'],
            "successful_checks": stats['successful_checks'],
            "failed_checks": stats['failed_checks'],
            "uptime_percent": stats['uptime_percent'],
            "avg_response_time_ms": stats['avg_response_time_ms'],
            "p50_response_time_ms": percentiles['p50'],
            "p95_response_time_ms": percentiles['p95'],
            "p99_response_time_ms": percentiles['p99'],
            "error_rate": round(error_rate, 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metrics"
        )


@router.get("/{monitor_id}/daily", response_model=List[DailyMetricsResponse])
async def get_daily_metrics(
    monitor_id: str,
    days: int = 7,
    user_data: Dict = Depends(verify_firebase_token)
):
    """Get daily aggregated metrics"""
    try:
        # Verify ownership
        monitor = await firestore_service.get_monitor(monitor_id)
        
        if not monitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitor not found"
            )
        
        if monitor['user_id'] != user_data['uid']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this monitor"
            )
        
        # Get daily metrics
        metrics = DailyMetricsRepository.get_daily_metrics(monitor_id, days=days)
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get daily metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily metrics"
        )
