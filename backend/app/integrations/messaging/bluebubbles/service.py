"""
BlueBubbles messaging service implementation
"""
from typing import List, Dict, Any
from app.integrations.messaging.base_messaging import BaseMessagingIntegration, Message
from app.integrations.base import IntegrationStatus
from app.integrations.messaging.bluebubbles.client import BlueBubblesClient


class BlueBubblesService(BaseMessagingIntegration):
    """BlueBubbles messaging integration service"""
    
    def __init__(self):
        self.client = BlueBubblesClient()
        self._connected = False
    
    @property
    def name(self) -> str:
        return "BlueBubbles"
    
    @property
    def provider(self) -> str:
        return "bluebubbles"
    
    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """Connect to BlueBubbles server"""
        # Test connection by getting chats
        try:
            await self.client.get_chats()
            self._connected = True
            return True
        except Exception as e:
            print(f"BlueBubbles connection error: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from BlueBubbles"""
        self._connected = False
        return True
    
    async def get_status(self) -> IntegrationStatus:
        """Get connection status"""
        if self._connected:
            return IntegrationStatus.CONNECTED
        return IntegrationStatus.DISCONNECTED
    
    async def refresh_credentials(self) -> bool:
        """Refresh credentials (not applicable for BlueBubbles)"""
        return True
    
    async def send_message(self, message: Message) -> bool:
        """Send a message via BlueBubbles"""
        try:
            # Get or create chat for recipient
            chat = await self.client.create_chat(message.recipient)
            chat_guid = chat.get("guid") or chat.get("chatGuid")
            
            if not chat_guid:
                raise ValueError("Could not get chat GUID")
            
            # Send message
            await self.client.send_message(
                chat_guid=chat_guid,
                message=message.content,
                attachments=message.attachments
            )
            return True
        except Exception as e:
            print(f"Error sending BlueBubbles message: {e}")
            return False
    
    async def receive_message(self, message_data: Dict[str, Any]) -> Message:
        """Process a received message from webhook"""
        # Parse webhook payload (structure needs verification)
        content = message_data.get("message", {}).get("text", "")
        sender = message_data.get("message", {}).get("handle", {})
        chat_guid = message_data.get("chatGuid") or message_data.get("chat", {}).get("guid")
        
        return Message(
            content=content,
            recipient="",  # Not applicable for received messages
            sender=str(sender),
            metadata={"chatGuid": chat_guid, "raw": message_data}
        )
    
    async def get_chats(self) -> List[Dict[str, Any]]:
        """Get list of chats"""
        return await self.client.get_chats()

