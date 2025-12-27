"""
Google Calendar integration service
"""
from typing import List, Optional, Dict
from datetime import datetime
from app.integrations.calendar.base_calendar import BaseCalendarIntegration, CalendarEvent
from app.integrations.base import IntegrationStatus
from app.integrations.google.oauth import GoogleOAuth
from googleapiclient.discovery import build
import json


class GoogleCalendarService(BaseCalendarIntegration):
    """Google Calendar integration service"""
    
    def __init__(self):
        self._connected = False
        self._credentials = None
    
    @property
    def name(self) -> str:
        return "Google Calendar"
    
    @property
    def provider(self) -> str:
        return "google_calendar"
    
    async def connect(self, credentials: dict) -> bool:
        """Connect to Google Calendar using shared Google OAuth credentials"""
        try:
            # Refresh credentials if needed
            credentials = GoogleOAuth.refresh_credentials_if_needed(credentials)
            self._credentials = credentials
            self._connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Google Calendar: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Google Calendar"""
        self._connected = False
        self._credentials = None
        return True
    
    async def get_status(self) -> IntegrationStatus:
        """Get connection status"""
        if self._connected:
            return IntegrationStatus.CONNECTED
        return IntegrationStatus.DISCONNECTED
    
    async def refresh_credentials(self) -> bool:
        """Refresh OAuth credentials"""
        # Implement OAuth token refresh
        return True
    
    async def create_event(self, event: CalendarEvent) -> str:
        """Create a calendar event"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Calendar")
        
        creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
        service = build('calendar', 'v3', credentials=creds)
        
        event_body = {
            'summary': event.title,
            'description': event.description,
            'start': {
                'dateTime': event.start.isoformat(),
                'timeZone': event.timezone or 'UTC',
            },
            'end': {
                'dateTime': event.end.isoformat(),
                'timeZone': event.timezone or 'UTC',
            },
        }
        
        created_event = service.events().insert(calendarId='primary', body=event_body).execute()
        return created_event.get('id')
    
    async def get_events(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> List[CalendarEvent]:
        """Get calendar events"""
        # Implement Google Calendar API call
        return []
    
    async def update_event(self, event_id: str, event: CalendarEvent) -> bool:
        """Update a calendar event"""
        # Implement Google Calendar API call
        return True
    
    async def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        # Implement Google Calendar API call
        return True

