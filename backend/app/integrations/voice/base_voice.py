"""
Base voice integration interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.integrations.base import BaseIntegration


class Call:
    """Call data structure"""
    def __init__(
        self,
        recipient: str,
        call_id: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.recipient = recipient
        self.call_id = call_id
        self.status = status
        self.metadata = metadata or {}


class BaseVoiceIntegration(BaseIntegration, ABC):
    """Base class for voice calling integrations"""
    
    @abstractmethod
    async def make_call(
        self,
        recipient: str,
        purpose: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Call:
        """Make a voice call to recipient"""
        pass
    
    @abstractmethod
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Get status of an ongoing call"""
        pass
    
    @abstractmethod
    async def end_call(self, call_id: str) -> bool:
        """End an ongoing call"""
        pass

