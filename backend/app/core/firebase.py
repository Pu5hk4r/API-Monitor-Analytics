"""
Firebase Authentication and Firestore integration
"""
import firebase_admin
from firebase_admin import credentials, auth, firestore
from fastapi import HTTPException, status, Header
from typing import Optional, Dict, Any
import logging
import os

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_initialized = False


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_initialized
    
    if _firebase_initialized:
        return
    
    try:
        # Check if running in production or development
        if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        else:
            # Use default credentials in Google Cloud environment
            cred = credentials.ApplicationDefault()
        
        firebase_admin.initialize_app(cred, {
            'projectId': settings.FIREBASE_PROJECT_ID,
        })
        
        _firebase_initialized = True
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        raise


def get_firestore_client():
    """Get Firestore client"""
    if not _firebase_initialized:
        initialize_firebase()
    return firestore.client()


async def verify_firebase_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Verify Firebase ID token from Authorization header
    
    Args:
        authorization: Authorization header with format "Bearer <token>"
    
    Returns:
        Decoded token with user information
    
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
        
        # Verify token with Firebase
        if not _firebase_initialized:
            initialize_firebase()
        
        decoded_token = auth.verify_id_token(token)
        return decoded_token
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


class FirestoreService:
    """Service for Firestore operations"""
    
    def __init__(self):
        self.db = get_firestore_client()
    
    # Monitors Collection
    async def get_user_monitors(self, user_id: str):
        """Get all monitors for a user"""
        try:
            monitors_ref = self.db.collection('monitors')
            query = monitors_ref.where('user_id', '==', user_id)
            docs = query.stream()
            
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get monitors: {str(e)}")
            raise
    
    async def get_monitor(self, monitor_id: str):
        """Get a specific monitor"""
        try:
            doc = self.db.collection('monitors').document(monitor_id).get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logger.error(f"Failed to get monitor: {str(e)}")
            raise
    
    async def create_monitor(self, monitor_data: dict):
        """Create a new monitor"""
        try:
            doc_ref = self.db.collection('monitors').document()
            monitor_data['created_at'] = firestore.SERVER_TIMESTAMP
            monitor_data['updated_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(monitor_data)
            return {'id': doc_ref.id, **monitor_data}
        except Exception as e:
            logger.error(f"Failed to create monitor: {str(e)}")
            raise
    
    async def update_monitor(self, monitor_id: str, update_data: dict):
        """Update a monitor"""
        try:
            doc_ref = self.db.collection('monitors').document(monitor_id)
            update_data['updated_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.update(update_data)
            return True
        except Exception as e:
            logger.error(f"Failed to update monitor: {str(e)}")
            raise
    
    async def delete_monitor(self, monitor_id: str):
        """Delete a monitor"""
        try:
            self.db.collection('monitors').document(monitor_id).delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete monitor: {str(e)}")
            raise
    
    # Alerts Collection
    async def create_alert(self, alert_data: dict):
        """Create an alert"""
        try:
            doc_ref = self.db.collection('alerts').document()
            alert_data['created_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(alert_data)
            return {'id': doc_ref.id, **alert_data}
        except Exception as e:
            logger.error(f"Failed to create alert: {str(e)}")
            raise
    
    async def get_monitor_alerts(self, monitor_id: str, limit: int = 50):
        """Get alerts for a monitor"""
        try:
            alerts_ref = self.db.collection('alerts')
            query = (alerts_ref
                    .where('monitor_id', '==', monitor_id)
                    .order_by('created_at', direction=firestore.Query.DESCENDING)
                    .limit(limit))
            docs = query.stream()
            
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get alerts: {str(e)}")
            raise
    
    async def get_all_monitors(self):
        """Get all monitors for background monitoring"""
        try:
            monitors_ref = self.db.collection('monitors')
            docs = monitors_ref.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            logger.error(f"Failed to get all monitors: {str(e)}")
            raise
