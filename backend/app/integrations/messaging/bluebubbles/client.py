"""
BlueBubbles API client
"""
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.integrations.messaging.base_messaging import Message


class BlueBubblesClient:
    """Client for BlueBubbles REST API"""
    
    def __init__(self):
        self.base_url = settings.BLUEBUBBLES_SERVER_URL.rstrip('/')
        self.password = settings.BLUEBUBBLES_SERVER_PASSWORD
        self.timeout = 30.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.password}",
            "Content-Type": "application/json",
        }
    
    async def send_message(
        self,
        chat_guid: str,
        message: str,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send a message via BlueBubbles API"""
        # Note: Exact endpoint structure needs verification from BlueBubbles docs
        # This is a placeholder implementation
        url = f"{self.base_url}/api/v1/message/send"
        
        payload = {
            "chatGuid": chat_guid,
            "message": message,
        }
        
        if attachments:
            payload["attachments"] = attachments
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_chats(self) -> List[Dict[str, Any]]:
        """Get list of chats"""
        url = f"{self.base_url}/api/v1/chat"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                url,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def create_chat(self, recipient: str) -> Dict[str, Any]:
        """Create or get chat for recipient"""
        # Note: Exact endpoint needs verification
        url = f"{self.base_url}/api/v1/chat"
        
        payload = {
            "recipient": recipient,
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

