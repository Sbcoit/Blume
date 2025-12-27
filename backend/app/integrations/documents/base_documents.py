"""
Base documents interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.integrations.base import BaseIntegration


class Document:
    """Document data structure"""
    def __init__(
        self,
        title: str,
        content: str,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.content = content
        self.document_id = document_id
        self.metadata = metadata or {}


class BaseDocumentsIntegration(BaseIntegration, ABC):
    """Base class for document integrations"""
    
    @abstractmethod
    async def create_document(self, document: Document) -> str:
        """Create a document, returns document ID"""
        pass
    
    @abstractmethod
    async def get_document(self, document_id: str) -> Document:
        """Get a document by ID"""
        pass
    
    @abstractmethod
    async def update_document(self, document_id: str, document: Document) -> bool:
        """Update a document"""
        pass
    
    @abstractmethod
    async def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents"""
        pass

