"""
Base messaging interface
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from app.integrations.base import BaseIntegration


class Message:
    """Message data structure"""
    def __init__(
        self,
        content: str,
        recipient: str,
        sender: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.recipient = recipient
        self.sender = sender
        self.attachments = attachments or []
        self.metadata = metadata or {}


class BaseMessagingIntegration(BaseIntegration, ABC):
    """Base class for messaging integrations"""
    
    @abstractmethod
    async def send_message(self, message: Message) -> bool:
        """Send a message"""
        pass
    
    @abstractmethod
    async def receive_message(self, message_data: Dict[str, Any]) -> Message:
        """Process a received message"""
        pass
    
    @abstractmethod
    async def get_chats(self) -> List[Dict[str, Any]]:
        """Get list of chats/conversations"""
        pass

