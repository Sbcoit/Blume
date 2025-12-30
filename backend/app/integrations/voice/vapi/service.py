"""
Vapi voice integration service implementation
"""
from typing import Dict, Any, Optional
from app.integrations.voice.base_voice import BaseVoiceIntegration, Call
from app.integrations.base import IntegrationStatus
from app.integrations.voice.vapi.client import VapiClient


class VapiService(BaseVoiceIntegration):
    """Vapi voice integration service"""
    
    def __init__(self):
        self.client = VapiClient()
        self._connected = False
    
    @property
    def name(self) -> str:
        return "Vapi"
    
    @property
    def provider(self) -> str:
        return "vapi"
    
    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """Connect to Vapi service"""
        # Test connection by checking API key validity
        try:
            # Vapi doesn't have a simple ping endpoint, so we'll just mark as connected
            # if API key is set
            if self.client.api_key:
                self._connected = True
                return True
            return False
        except Exception as e:
            print(f"Vapi connection error: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Vapi"""
        self._connected = False
        return True
    
    async def get_status(self) -> IntegrationStatus:
        """Get connection status"""
        if self._connected:
            return IntegrationStatus.CONNECTED
        return IntegrationStatus.DISCONNECTED
    
    async def refresh_credentials(self) -> bool:
        """Refresh credentials (not applicable for Vapi)"""
        return True
    
    async def make_call(
        self,
        recipient: str,
        purpose: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Call:
        """Make a voice call via Vapi"""
        try:
            # Build agent config with purpose if provided
            agent_config = None
            if purpose:
                agent_config = {
                    "model": {
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.7,
                    },
                    "voice": {
                        "provider": "11labs",
                        "voiceId": "21m00Tcm4TlvDq8ikWAM",
                    },
                    "firstMessage": f"Hello, this is Blume. {purpose}",
                }
            
            # Create call
            response = await self.client.create_call(
                phone_number=recipient,
                agent_config=agent_config
            )
            
            call_id = response.get("id") or response.get("callId")
            status = response.get("status", "initiated")
            
            return Call(
                recipient=recipient,
                call_id=call_id,
                status=status,
                metadata={**(metadata or {}), "vapi_response": response}
            )
        except Exception as e:
            print(f"Error making Vapi call: {e}")
            raise
    
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Get status of an ongoing call"""
        try:
            return await self.client.get_call(call_id)
        except Exception as e:
            print(f"Error getting Vapi call status: {e}")
            raise
    
    async def end_call(self, call_id: str) -> bool:
        """End an ongoing call"""
        try:
            await self.client.end_call(call_id)
            return True
        except Exception as e:
            print(f"Error ending Vapi call: {e}")
            return False

