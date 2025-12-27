"""
Base integration interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum


class IntegrationStatus(str, Enum):
    """Integration connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class BaseIntegration(ABC):
    """Base class for all integrations"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Integration name"""
        pass
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """Integration provider identifier"""
        pass
    
    @abstractmethod
    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """Connect to the integration service"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the integration service"""
        pass
    
    @abstractmethod
    async def get_status(self) -> IntegrationStatus:
        """Get connection status"""
        pass
    
    @abstractmethod
    async def refresh_credentials(self) -> bool:
        """Refresh authentication credentials"""
        pass

