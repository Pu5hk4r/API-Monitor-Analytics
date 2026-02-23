"""
Monitors API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging

from app.models.schemas import (
    MonitorCreate, MonitorUpdate, MonitorResponse, 
    HealthCheckResponse, DashboardStats
)
from app.core.firebase import verify_firebase_token, FirestoreService
from app.database.sqlite_db import HealthCheckRepository
from app.services.cache_service import cache_service

router = APIRouter()
logger = logging.getLogger(__name__)
firestore_service = FirestoreService()


@router.get("/", response_model=List[MonitorResponse])
async def get_monitors(user_data: Dict = Depends(verify_firebase_token)):
    """Get all monitors for the authenticated user"""
    try:
        user_id = user_data['uid']
        monitors = await firestore_service.get_user_monitors(user_id)
        
        # Enrich with current status from cache/database
        for monitor in monitors:
            cache_key = f"monitor_status:{monitor['id']}"
            status_data = cache_service.get(cache_key)
            
            if status_data:
                monitor.update(status_data)
            else:
                # Get from database
                stats = HealthCheckRepository.get_uptime_stats(monitor['id'], hours=24)
                monitor['uptime_percent'] = stats['uptime_percent']
                monitor['avg_response_time_ms'] = stats['avg_response_time_ms']
                
                # Get most recent check
                recent = HealthCheckRepository.get_recent_checks(monitor['id'], hours=1)
                if recent:
                    latest = recent[0]
                    monitor['current_status'] = 'up' if latest['is_up'] else 'down'
                    monitor['last_check_time'] = latest['timestamp']
        
        return monitors
    except Exception as e:
        logger.error(f"Failed to get monitors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve monitors"
        )


@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_monitor(
    monitor_id: str,
    user_data: Dict = Depends(verify_firebase_token)
):
    """Get a specific monitor"""
    try:
        monitor = await firestore_service.get_monitor(monitor_id)
        
        if not monitor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Monitor not found"
            )
        
        # Verify ownership
        if monitor['user_id'] != user_data['uid']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this monitor"
            )
        
        # Enrich with current status
        stats = HealthCheckRepository.get_uptime_stats(monitor_id, hours=24)
        monitor['uptime_percent'] = stats['uptime_percent']
        monitor['avg_response_time_ms'] = stats['avg_response_time_ms']
        
        recent = HealthCheckRepository.get_recent_checks(monitor_id, hours=1)
        if recent:
            latest = recent[0]
            monitor['current_status'] = 'up' if latest['is_up'] else 'down'
            monitor['last_check_time'] = latest['timestamp']
        
        return monitor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get monitor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve monitor"
        )


@router.post("/", response_model=MonitorResponse, status_code=status.HTTP_201_CREATED)
async def create_monitor(
    monitor: MonitorCreate,
    user_data: Dict = Depends(verify_firebase_token)
):
    """Create a new monitor"""
    try:
        # monitor_data = monitor.dict()
        # monitor_data['user_id'] = user_data['uid']
        # monitor_data['is_active'] = True

        monitor_data = monitor.dict()

        # Convert HttpUrl to string for Firestore
        monitor_data['url'] = str(monitor_data['url'])

        monitor_data['user_id'] = user_data['uid']
        monitor_data['is_active'] = True

        
        created_monitor = await firestore_service.create_monitor(monitor_data)
        logger.info(f"Monitor created: {created_monitor['id']} by user {user_data['uid']}")
        
        return created_monitor
    except Exception as e:
        logger.error(f"Failed to create monitor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create monitor"
        )


@router.put("/{monitor_id}", response_model=Dict[str, str])
async def update_monitor(
    monitor_id: str,
    monitor_update: MonitorUpdate,
    user_data: Dict = Depends(verify_firebase_token)
):
    """Update a monitor"""
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
                detail="Not authorized to update this monitor"
            )
        
        # Update monitor
        update_data = monitor_update.dict(exclude_unset=True)
        if 'url' in update_data:
            update_data['url'] = str(update_data['url'])
        
        
        # Clear cache
        cache_service.delete(f"monitor_status:{monitor_id}")
        
        logger.info(f"Monitor updated: {monitor_id} by user {user_data['uid']}")
        
        return {"message": "Monitor updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update monitor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update monitor"
        )


@router.delete("/{monitor_id}", response_model=Dict[str, str])
async def delete_monitor(
    monitor_id: str,
    user_data: Dict = Depends(verify_firebase_token)
):
    """Delete a monitor"""
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
                detail="Not authorized to delete this monitor"
            )
        
        # Delete monitor
        await firestore_service.delete_monitor(monitor_id)
        
        # Clear cache
        cache_service.delete(f"monitor_status:{monitor_id}")
        
        logger.info(f"Monitor deleted: {monitor_id} by user {user_data['uid']}")
        
        return {"message": "Monitor deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete monitor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete monitor"
        )


@router.get("/{monitor_id}/health-checks", response_model=List[HealthCheckResponse])
async def get_health_checks(
    monitor_id: str,
    hours: int = 24,
    user_data: Dict = Depends(verify_firebase_token)
):
    """Get health check history for a monitor"""
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
        
        # Get health checks
        checks = HealthCheckRepository.get_recent_checks(monitor_id, hours=hours)
        
        return checks
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get health checks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve health checks"
        )


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(user_data: Dict = Depends(verify_firebase_token)):
    """Get dashboard statistics for user"""
    try:
        user_id = user_data['uid']
        
        # Check cache first
        cache_key = f"dashboard_stats:{user_id}"
        cached_stats = cache_service.get(cache_key)
        
        if cached_stats:
            return cached_stats
        
        # Get monitors
        monitors = await firestore_service.get_user_monitors(user_id)
        
        total_monitors = len(monitors)
        active_monitors = sum(1 for m in monitors if m.get('is_active', True))
        
        monitors_up = 0
        monitors_down = 0
        total_uptime = 0
        total_response_time = 0
        
        for monitor in monitors:
            if monitor.get('is_active', True):
                recent = HealthCheckRepository.get_recent_checks(monitor['id'], hours=1)
                if recent:
                    latest = recent[0]
                    if latest['is_up']:
                        monitors_up += 1
                    else:
                        monitors_down += 1
                
                stats = HealthCheckRepository.get_uptime_stats(monitor['id'], hours=24)
                total_uptime += stats['uptime_percent']
                total_response_time += stats['avg_response_time_ms']
        
        avg_uptime = (total_uptime / active_monitors) if active_monitors > 0 else 0
        avg_response = (total_response_time / active_monitors) if active_monitors > 0 else 0
        
        # Get alerts count (simplified - you can enhance this)
        total_alerts = 0  # Implement if needed
        unresolved_alerts = 0  # Implement if needed
        
        stats = {
            "total_monitors": total_monitors,
            "active_monitors": active_monitors,
            "monitors_up": monitors_up,
            "monitors_down": monitors_down,
            "total_alerts": total_alerts,
            "unresolved_alerts": unresolved_alerts,
            "avg_uptime_percent": round(avg_uptime, 2),
            "avg_response_time_ms": round(avg_response, 2)
        }
        
        # Cache for 5 minutes
        cache_service.set(cache_key, stats, ttl=300)
        
        return stats
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )
