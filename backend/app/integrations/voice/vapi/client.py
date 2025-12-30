"""
Vapi API client
"""
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings


class VapiClient:
    """Client for Vapi REST API"""
    
    def __init__(self):
        self.base_url = settings.VAPI_BASE_URL.rstrip('/')
        self.api_key = settings.VAPI_API_KEY
        self.timeout = 30.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def create_call(
        self,
        phone_number: str,
        agent_id: Optional[str] = None,
        agent_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a voice call via Vapi API"""
        url = f"{self.base_url}/call"
        
        payload = {
            "phoneNumberId": phone_number,  # Vapi uses phoneNumberId or phoneNumber
        }
        
        if agent_id:
            payload["assistantId"] = agent_id
        elif agent_config:
            payload["assistant"] = agent_config
        else:
            # Use default agent config if available
            payload["assistant"] = {
                "model": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7,
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "21m00Tcm4TlvDq8ikWAM",
                },
                "firstMessage": "Hello, this is Blume. How can I help you?",
            }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """Get call details and status"""
        url = f"{self.base_url}/call/{call_id}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                url,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """End an ongoing call"""
        url = f"{self.base_url}/call/{call_id}"
        
        payload = {
            "endCall": True
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.patch(
                url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

