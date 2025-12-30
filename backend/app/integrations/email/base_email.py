"""
Base email interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.integrations.base import BaseIntegration


class Email:
    """Email data structure"""
    def __init__(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        email_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.to = to
        self.subject = subject
        self.body = body
        self.cc = cc or []
        self.bcc = bcc or []
        self.email_id = email_id
        self.metadata = metadata or {}


class BaseEmailIntegration(BaseIntegration, ABC):
    """Base class for email integrations"""
    
    @abstractmethod
    async def send_email(self, email: Email) -> bool:
        """Send an email"""
        pass
    
    @abstractmethod
    async def draft_email(self, email: Email) -> str:
        """Create a draft email, returns draft ID"""
        pass
    
    @abstractmethod
    async def list_emails(self, query: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """List emails"""
        pass
    
    @abstractmethod
    async def get_email(self, email_id: str) -> Email:
        """Get an email by ID"""
        pass

