"""
BlueBubbles messaging service implementation
"""
import logging
from typing import List, Dict, Any
from app.integrations.messaging.base_messaging import BaseMessagingIntegration, Message
from app.integrations.base import IntegrationStatus
from app.integrations.messaging.bluebubbles.client import BlueBubblesClient

logger = logging.getLogger(__name__)


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
            logger.info(f"Attempting to send message to {message.recipient}")
            logger.debug(f"Message content: {message.content[:50]}...")
            
            # First, check if chat_guid is provided in message metadata (from incoming message)
            chat_guid = None
            if message.metadata and message.metadata.get("chat_guid"):
                chat_guid = message.metadata.get("chat_guid")
                logger.info(f"Using chat_guid from message metadata: {chat_guid}")
            
            # If no chat_guid in metadata, try to find existing chat for this recipient
            if not chat_guid:
                try:
                    logger.debug(f"Looking for existing chat for recipient: {message.recipient}")
                    chats = await self.client.get_chats()
                    
                    if isinstance(chats, list):
                        for chat in chats:
                            participants = chat.get("participants", []) or chat.get("handles", []) or []
                            # Check if recipient matches any participant
                            for participant in participants:
                                if isinstance(participant, dict):
                                    address = participant.get("address") or participant.get("id") or str(participant)
                                else:
                                    address = str(participant)
                                
                                # Normalize phone numbers for comparison
                                normalized_recipient = message.recipient.replace("+", "").replace("-", "").replace(" ", "")
                                normalized_address = address.replace("+", "").replace("-", "").replace(" ", "")
                                
                                if normalized_address == normalized_recipient or address == message.recipient:
                                    chat_guid = chat.get("guid") or chat.get("chatGuid")
                                    if chat_guid:
                                        logger.info(f"Found existing chat GUID: {chat_guid} for {message.recipient}")
                                        break
                            if chat_guid:
                                break
                except Exception as e:
                    logger.debug(f"Could not search existing chats (will create new chat): {e}")
            
            # If we found an existing chat, send message to it
            if chat_guid:
                logger.info(f"Using existing chat GUID: {chat_guid}")
                try:
                    result = await self.client.send_message(
                        chat_guid=chat_guid,
                        message=message.content,
                        attachments=message.attachments
                    )
                    logger.info(f"Successfully sent message to {message.recipient}")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to send to existing chat, will create new chat: {e}")
                    chat_guid = None  # Reset to create new chat
            
            # If no existing chat found or sending failed, create a new chat with the message
            if not chat_guid:
                logger.info(f"Creating new chat for recipient: {message.recipient}")
                try:
                    # Use create_chat with the message - this will create the chat and send the message in one call
                    # According to BlueBubbles API docs, /api/v1/chat/new can optionally send a message
                    chat_result = await self.client.create_chat(message.recipient, message.content)
                    logger.debug(f"Chat creation response: {chat_result}")
                    
                    # If chat was created successfully, the message should have been sent
                    if chat_result.get("success"):
                        logger.info(f"Successfully created chat and sent message to {message.recipient}")
                        return True
                    else:
                        logger.warning(f"Chat creation returned but success=False: {chat_result}")
                        return False
                except Exception as e:
                    logger.error(f"Failed to create chat for {message.recipient}: {e}", exc_info=True)
                    return False
            
            return False
        except Exception as e:
            logger.error(f"Error sending BlueBubbles message to {message.recipient}: {e}", exc_info=True)
            return False
    
    async def receive_message(self, message_data: Dict[str, Any]) -> Message:
        """Process a received message from webhook
        
        NOTE: This method is not currently used. Messages are received via webhook
        endpoint and processed directly in the webhook handler.
        Kept for interface compatibility.
        """
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

