"""
Application configuration using Pydantic settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "API Monitor System"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Firebase settings
    FIREBASE_PROJECT_ID: str
    FIREBASE_CREDENTIALS_PATH: str = "/app/secrets/firebase-credentials.json"
    
    # Google Cloud settings
    GCP_PROJECT_ID: str
    GEMINI_API_KEY: str
    
    # Database settings
    SQLITE_DB_PATH: str = "/app/database/metrics.db"
    DATA_RETENTION_DAYS: int = 7
    
    # Cache settings
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Scheduler settings
    MONITOR_CHECK_INTERVAL_MINUTES: int = 5
    MAX_WORKERS: int = 10
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://monitor.yourdomain.com"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    CLOUDWATCH_LOG_GROUP: str = "/aws/ec2/api-monitor"
    
    # Alert settings
    MAX_CONSECUTIVE_FAILURES: int = 3
    ALERT_COOLDOWN_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
