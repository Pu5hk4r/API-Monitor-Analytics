"""
Gemini AI service for error analysis
"""
import google.generativeai as genai
from typing import Dict, Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for Gemini AI analysis"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def analyze_error(self, monitor: Dict, error_details: Dict) -> Optional[str]:
        """
        Analyze monitor error using Gemini AI
        
        Args:
            monitor: Monitor configuration
            error_details: Error information
        
        Returns:
            AI-generated analysis text
        """
        try:
            # Construct prompt
            prompt = f"""
You are an API monitoring expert. Analyze the following API endpoint error and provide:
1. Likely root cause
2. Recommended actions
3. Prevention tips

Monitor Details:
- Name: {monitor.get('name')}
- URL: {monitor.get('url')}
- Method: {monitor.get('method', 'GET')}
- Expected Status: {monitor.get('expected_status_code', 200)}

Error Details:
- Status Code: {error_details.get('status_code', 'N/A')}
- Error Message: {error_details.get('error_message', 'Unknown error')}
- Response Time: {error_details.get('response_time_ms', 'N/A')} ms
- Consecutive Failures: {error_details.get('consecutive_failures', 1)}

Provide a concise, actionable analysis in 3-4 sentences.
"""
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {str(e)}")
            return None


# Global instance
gemini_service = GeminiService()
