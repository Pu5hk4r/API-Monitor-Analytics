"""
SQLite database for time-series metrics storage
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from contextlib import contextmanager
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Initialize database tables"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(settings.SQLITE_DB_PATH), exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Health checks table (time-series data)
        # Health checks table (time-series data)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                status_code INTEGER,
                response_time_ms INTEGER,
                is_up BOOLEAN NOT NULL,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Daily metrics table (aggregated stats)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                monitor_id TEXT NOT NULL,
                date DATE NOT NULL,
                total_checks INTEGER DEFAULT 0,
                successful_checks INTEGER DEFAULT 0,
                failed_checks INTEGER DEFAULT 0,
                avg_response_time_ms REAL,
                p50_response_time_ms INTEGER,
                p95_response_time_ms INTEGER,
                p99_response_time_ms INTEGER,
                uptime_percent REAL,
                error_rate REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(monitor_id, date)
            )
        ''')
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_health_checks_monitor 
            ON health_checks(monitor_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_health_checks_timestamp 
            ON health_checks(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_daily_metrics_monitor 
            ON daily_metrics(monitor_id)
        ''')
        
        logger.info("Database initialized successfully")


class HealthCheckRepository:
    """Repository for health check data"""
    
    @staticmethod
    def insert_check(monitor_id: str, status_code: Optional[int], 
                    response_time_ms: Optional[int], is_up: bool, 
                    error_message: Optional[str] = None):
        """Insert a new health check record"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO health_checks 
                (monitor_id, timestamp, status_code, response_time_ms, is_up, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                monitor_id,
                datetime.utcnow(),
                status_code,
                response_time_ms,
                is_up,
                error_message
            ))
            return cursor.lastrowid
    
    @staticmethod
    def get_recent_checks(monitor_id: str, hours: int = 24) -> List[Dict]:
        """Get recent health checks for a monitor"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            since = datetime.utcnow() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT * FROM health_checks
                WHERE monitor_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (monitor_id, since))
            
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_uptime_stats(monitor_id: str, hours: int = 24) -> Dict:
        """Calculate uptime statistics"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            since = datetime.utcnow() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_checks,
                    SUM(CASE WHEN is_up = 1 THEN 1 ELSE 0 END) as successful_checks,
                    SUM(CASE WHEN is_up = 0 THEN 1 ELSE 0 END) as failed_checks,
                    AVG(CASE WHEN is_up = 1 THEN response_time_ms END) as avg_response_time
                FROM health_checks
                WHERE monitor_id = ? AND timestamp >= ?
            ''', (monitor_id, since))
            
            row = cursor.fetchone()
            
            if row['total_checks'] > 0:
                uptime_percent = (row['successful_checks'] / row['total_checks']) * 100
            else:
                uptime_percent = 0
            
            return {
                'total_checks': row['total_checks'],
                'successful_checks': row['successful_checks'],
                'failed_checks': row['failed_checks'],
                'uptime_percent': round(uptime_percent, 2),
                'avg_response_time_ms': round(row['avg_response_time'] or 0, 2)
            }
    
    @staticmethod
    def get_response_time_percentiles(monitor_id: str, hours: int = 24) -> Dict:
        """Calculate response time percentiles"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            since = datetime.utcnow() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT response_time_ms
                FROM health_checks
                WHERE monitor_id = ? 
                  AND timestamp >= ?
                  AND is_up = 1
                  AND response_time_ms IS NOT NULL
                ORDER BY response_time_ms
            ''', (monitor_id, since))
            
            response_times = [row[0] for row in cursor.fetchall()]
            
            if not response_times:
                return {'p50': 0, 'p95': 0, 'p99': 0}
            
            def percentile(data: List[int], p: float) -> int:
                k = (len(data) - 1) * p
                f = int(k)
                c = f + 1
                if c >= len(data):
                    return data[f]
                return int(data[f] + (k - f) * (data[c] - data[f]))
            
            return {
                'p50': percentile(response_times, 0.50),
                'p95': percentile(response_times, 0.95),
                'p99': percentile(response_times, 0.99)
            }
    
    @staticmethod
    def cleanup_old_data(days: int = None):
        """Remove data older than specified days"""
        if days is None:
            days = settings.DATA_RETENTION_DAYS
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            cursor.execute('''
                DELETE FROM health_checks
                WHERE timestamp < ?
            ''', (cutoff,))
            
            deleted = cursor.rowcount
            logger.info(f"Cleaned up {deleted} old health check records")
            return deleted


class DailyMetricsRepository:
    """Repository for daily aggregated metrics"""
    
    @staticmethod
    def update_daily_metrics(monitor_id: str, date: datetime.date = None):
        """Update or create daily metrics for a monitor"""
        if date is None:
            date = datetime.utcnow().date()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Calculate metrics from health_checks
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_up = 1 THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN is_up = 0 THEN 1 ELSE 0 END) as failed,
                    AVG(CASE WHEN is_up = 1 THEN response_time_ms END) as avg_rt
                FROM health_checks
                WHERE monitor_id = ? 
                  AND DATE(timestamp) = ?
            ''', (monitor_id, date))
            
            stats = cursor.fetchone()
            
            # Get percentiles
            percentiles = HealthCheckRepository.get_response_time_percentiles(
                monitor_id, hours=24
            )
            
            uptime_percent = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
            error_rate = (stats['failed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            # Upsert daily metrics
            cursor.execute('''
                INSERT INTO daily_metrics 
                (monitor_id, date, total_checks, successful_checks, failed_checks,
                 avg_response_time_ms, p50_response_time_ms, p95_response_time_ms, 
                 p99_response_time_ms, uptime_percent, error_rate, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(monitor_id, date) DO UPDATE SET
                    total_checks = excluded.total_checks,
                    successful_checks = excluded.successful_checks,
                    failed_checks = excluded.failed_checks,
                    avg_response_time_ms = excluded.avg_response_time_ms,
                    p50_response_time_ms = excluded.p50_response_time_ms,
                    p95_response_time_ms = excluded.p95_response_time_ms,
                    p99_response_time_ms = excluded.p99_response_time_ms,
                    uptime_percent = excluded.uptime_percent,
                    error_rate = excluded.error_rate,
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                monitor_id,
                date,
                stats['total'],
                stats['successful'],
                stats['failed'],
                stats['avg_rt'],
                percentiles['p50'],
                percentiles['p95'],
                percentiles['p99'],
                uptime_percent,
                error_rate
            ))
    
    @staticmethod
    def get_daily_metrics(monitor_id: str, days: int = 7) -> List[Dict]:
        """Get daily metrics for a monitor"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            since = datetime.utcnow().date() - timedelta(days=days)
            
            cursor.execute('''
                SELECT * FROM daily_metrics
                WHERE monitor_id = ? AND date >= ?
                ORDER BY date DESC
            ''', (monitor_id, since))
            
            return [dict(row) for row in cursor.fetchall()]
