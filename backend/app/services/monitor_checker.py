"""
Service for checking monitor health
"""
import httpx
from typing import Dict, Optional, Tuple
import logging
from datetime import datetime

from app.core.config import settings
from app.database.sqlite_db import HealthCheckRepository

logger = logging.getLogger(__name__)


class MonitorChecker:
    """Service to check monitor endpoints"""
    
    def __init__(self):
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS
    
    async def check_monitor(self, monitor: Dict) -> Tuple[bool, Optional[int], Optional[int], Optional[str]]:
        """
        Check a monitor endpoint
        
        Returns:
            Tuple of (is_up, status_code, response_time_ms, error_message)
        """
        url = str(monitor['url'])
        method = monitor.get('method', 'GET')
        headers = monitor.get('headers', {})
        body = monitor.get('body')
        expected_status = monitor.get('expected_status_code', 200)
        
        start_time = datetime.utcnow()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                # Make request based on method
                if method == 'GET':
                    response = await client.get(url, headers=headers)
                elif method == 'POST':
                    response = await client.post(url, headers=headers, content=body)
                elif method == 'PUT':
                    response = await client.put(url, headers=headers, content=body)
                elif method == 'DELETE':
                    response = await client.delete(url, headers=headers)
                elif method == 'PATCH':
                    response = await client.patch(url, headers=headers, content=body)
                else:
                    return False, None, None, f"Unsupported HTTP method: {method}"
                
                # Calculate response time
                end_time = datetime.utcnow()
                response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Check if status code matches expected
                is_up = response.status_code == expected_status
                error_message = None if is_up else f"Expected {expected_status}, got {response.status_code}"
                
                return is_up, response.status_code, response_time_ms, error_message
                
        except httpx.TimeoutException:
            end_time = datetime.utcnow()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            return False, None, response_time_ms, "Request timeout"
        
        except httpx.ConnectError as e:
            return False, None, None, f"Connection error: {str(e)}"
        
        except httpx.HTTPError as e:
            return False, None, None, f"HTTP error: {str(e)}"
        
        except Exception as e:
            logger.error(f"Unexpected error checking monitor {monitor.get('id')}: {str(e)}")
            return False, None, None, f"Unexpected error: {str(e)}"
    
    async def check_and_record(self, monitor: Dict) -> Dict:
        """
        Check monitor and record result to database
        
        Returns:
            Dict with check results
        """
        monitor_id = monitor['id']
        
        is_up, status_code, response_time_ms, error_message = await self.check_monitor(monitor)
        
        # Record to database
        try:
            HealthCheckRepository.insert_check(
                monitor_id=monitor_id,
                status_code=status_code,
                response_time_ms=response_time_ms,
                is_up=is_up,
                error_message=error_message
            )
        except Exception as e:
            logger.error(f"Failed to record health check for {monitor_id}: {str(e)}")
        
        return {
            'monitor_id': monitor_id,
            'monitor_name': monitor.get('name'),
            'is_up': is_up,
            'status_code': status_code,
            'response_time_ms': response_time_ms,
            'error_message': error_message,
            'timestamp': datetime.utcnow()
        }


# Global instance
monitor_checker = MonitorChecker()
