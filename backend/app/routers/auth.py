"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends
from typing import Dict
import logging

from app.models.schemas import UserProfile
from app.core.firebase import verify_firebase_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me", response_model=UserProfile)
async def get_current_user(user_data: Dict = Depends(verify_firebase_token)):
    """Get current authenticated user profile"""
    return {
        "uid": user_data['uid'],
        "email": user_data.get('email'),
        "display_name": user_data.get('name'),
    }


@router.get("/verify")
async def verify_token(user_data: Dict = Depends(verify_firebase_token)):
    """Verify authentication token"""
    return {
        "valid": True,
        "uid": user_data['uid']
    }
