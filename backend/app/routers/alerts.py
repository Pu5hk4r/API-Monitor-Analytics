"""
Alerts API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
import logging

from app.models.schemas import AlertResponse
from app.core.firebase import verify_firebase_token, FirestoreService

router = APIRouter()
logger = logging.getLogger(__name__)
firestore_service = FirestoreService()


@router.get("/{monitor_id}", response_model=List[AlertResponse])
async def get_monitor_alerts(
    monitor_id: str,
    limit: int = 50,
    user_data: Dict = Depends(verify_firebase_token)
):
    """Get alerts for a specific monitor"""
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
        
        # Get alerts
        alerts = await firestore_service.get_monitor_alerts(monitor_id, limit=limit)
        
        return alerts
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts"
        )


@router.get("/", response_model=List[AlertResponse])
async def get_user_alerts(
    limit: int = 100,
    user_data: Dict = Depends(verify_firebase_token)
):
    """Get all alerts for the authenticated user"""
    try:
        user_id = user_data['uid']
        
        # Get user's monitors
        monitors = await firestore_service.get_user_monitors(user_id)
        monitor_ids = [m['id'] for m in monitors]
        
        # Get alerts for all monitors (simplified - you may want to optimize this)
        all_alerts = []
        for monitor_id in monitor_ids:
            alerts = await firestore_service.get_monitor_alerts(monitor_id, limit=limit)
            all_alerts.extend(alerts)
        
        # Sort by created_at descending
        all_alerts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return all_alerts[:limit]
    except Exception as e:
        logger.error(f"Failed to get user alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts"
        )
