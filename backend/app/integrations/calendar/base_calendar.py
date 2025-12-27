"""
Base calendar interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.integrations.base import BaseIntegration


class CalendarEvent:
    """Calendar event data structure"""
    def __init__(
        self,
        title: str,
        start: datetime,
        end: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.start = start
        self.end = end
        self.description = description
        self.location = location
        self.attendees = attendees or []
        self.metadata = metadata or {}


class BaseCalendarIntegration(BaseIntegration, ABC):
    """Base class for calendar integrations"""
    
    @abstractmethod
    async def create_event(self, event: CalendarEvent) -> str:
        """Create a calendar event, returns event ID"""
        pass
    
    @abstractmethod
    async def get_events(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> List[CalendarEvent]:
        """Get calendar events in date range"""
        pass
    
    @abstractmethod
    async def update_event(self, event_id: str, event: CalendarEvent) -> bool:
        """Update a calendar event"""
        pass
    
    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        pass

