"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MonitorMethod(str, Enum):
    """HTTP methods for monitoring"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class AlertCondition(str, Enum):
    """Alert trigger conditions"""
    DOWN = "down"
    SLOW_RESPONSE = "slow_response"
    STATUS_CODE = "status_code"
    CONSECUTIVE_FAILURES = "consecutive_failures"


class MonitorCreate(BaseModel):
    """Schema for creating a monitor"""
    name: str = Field(..., min_length=1, max_length=200)
    url: HttpUrl
    method: MonitorMethod = MonitorMethod.GET
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None
    interval_minutes: int = Field(default=5, ge=1, le=60)
    timeout_seconds: int = Field(default=30, ge=5, le=120)
    expected_status_code: Optional[int] = Field(default=200, ge=100, le=599)
    alert_on_failure: bool = True
    alert_threshold_minutes: int = Field(default=15, ge=5, le=120)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Production API",
                "url": "https://api.example.com/health",
                "method": "GET",
                "interval_minutes": 5,
                "timeout_seconds": 30,
                "expected_status_code": 200,
                "alert_on_failure": True
            }
        }


class MonitorUpdate(BaseModel):
    """Schema for updating a monitor"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[HttpUrl] = None
    method: Optional[MonitorMethod] = None
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None
    interval_minutes: Optional[int] = Field(None, ge=1, le=60)
    timeout_seconds: Optional[int] = Field(None, ge=5, le=120)
    expected_status_code: Optional[int] = Field(None, ge=100, le=599)
    alert_on_failure: Optional[bool] = None
    alert_threshold_minutes: Optional[int] = Field(None, ge=5, le=120)
    is_active: Optional[bool] = None


class MonitorResponse(BaseModel):
    """Schema for monitor response"""
    id: str
    user_id: str
    name: str
    url: str
    method: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None
    interval_minutes: int
    timeout_seconds: int
    expected_status_code: int
    alert_on_failure: bool
    alert_threshold_minutes: int
    is_active: bool
    created_at: Any
    updated_at: Any
    
    # Current status fields
    current_status: Optional[str] = None
    last_check_time: Optional[datetime] = None
    uptime_percent: Optional[float] = None
    avg_response_time_ms: Optional[float] = None


class HealthCheckResponse(BaseModel):
    """Schema for health check response"""
    id: int
    monitor_id: str
    timestamp: datetime
    status_code: Optional[int]
    response_time_ms: Optional[int]
    is_up: bool
    error_message: Optional[str]


class MetricsResponse(BaseModel):
    """Schema for metrics response"""
    monitor_id: str
    time_period: str
    total_checks: int
    successful_checks: int
    failed_checks: int
    uptime_percent: float
    avg_response_time_ms: float
    p50_response_time_ms: int
    p95_response_time_ms: int
    p99_response_time_ms: int
    error_rate: float


class DailyMetricsResponse(BaseModel):
    """Schema for daily metrics"""
    date: str
    total_checks: int
    successful_checks: int
    failed_checks: int
    uptime_percent: float
    avg_response_time_ms: float
    p50_response_time_ms: int
    p95_response_time_ms: int
    p99_response_time_ms: int


class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: str
    monitor_id: str
    monitor_name: str
    alert_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[str] = None
    created_at: Any
    resolved_at: Optional[Any] = None
    is_resolved: bool = False


class AlertCreate(BaseModel):
    """Schema for creating an alert"""
    monitor_id: str
    alert_type: str
    message: str
    details: Optional[Dict[str, Any]] = None


class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    total_monitors: int
    active_monitors: int
    monitors_up: int
    monitors_down: int
    total_alerts: int
    unresolved_alerts: int
    avg_uptime_percent: float
    avg_response_time_ms: float


class UserProfile(BaseModel):
    """Schema for user profile"""
    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    created_at: Optional[datetime] = None
