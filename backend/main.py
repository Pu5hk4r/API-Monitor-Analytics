"""
API Monitor System - FastAPI Backend
Main application file
"""
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional
import logging

from app.routers import monitors, alerts, metrics, auth
from app.core.config import settings
from app.core.firebase import verify_firebase_token
from app.scheduler.monitor_scheduler import start_scheduler, stop_scheduler
from app.database.sqlite_db import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for FastAPI app"""
    logger.info("Starting API Monitor System...")
    
    # Initialize database
    init_database()
    logger.info("Database initialized")
    
    # Start background scheduler
    start_scheduler()
    logger.info("Monitor scheduler started")
    
    yield
    
    # Cleanup
    logger.info("Shutting down API Monitor System...")
    stop_scheduler()
    logger.info("Monitor scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title="API Monitor System",
    description="Real-time API monitoring and alerting system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint (no auth required)
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "service": "api-monitor-system",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "API Monitor System",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(monitors.router, prefix="/api/monitors", tags=["Monitors"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
