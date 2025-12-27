"""
Base notes interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.integrations.base import BaseIntegration


class Note:
    """Note data structure"""
    def __init__(
        self,
        title: str,
        content: str,
        note_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.content = content
        self.note_id = note_id
        self.metadata = metadata or {}


class BaseNotesIntegration(BaseIntegration, ABC):
    """Base class for notes integrations"""
    
    @abstractmethod
    async def create_note(self, note: Note) -> str:
        """Create a note, returns note ID"""
        pass
    
    @abstractmethod
    async def get_note(self, note_id: str) -> Note:
        """Get a note by ID"""
        pass
    
    @abstractmethod
    async def update_note(self, note_id: str, note: Note) -> bool:
        """Update a note"""
        pass
    
    @abstractmethod
    async def list_notes(self) -> List[Dict[str, Any]]:
        """List all notes"""
        pass

