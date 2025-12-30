"""
Google Calendar integration service
"""
from typing import List, Optional, Dict
from datetime import datetime
import uuid
import logging
from app.integrations.calendar.base_calendar import BaseCalendarIntegration, CalendarEvent
from app.integrations.base import IntegrationStatus
from app.integrations.google.oauth import GoogleOAuth
from googleapiclient.discovery import build
import json

logger = logging.getLogger(__name__)


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
    
    def get_credentials(self) -> Optional[Dict]:
        """Get credentials for internal use by handlers
        
        Returns:
            Credentials dictionary or None if not connected
        """
        return self._credentials if self._connected else None
    
    async def create_event(self, event: CalendarEvent) -> str:
        """Create a calendar event with Google Meet link
        
        Returns:
            str: Event ID. Note: Meet link is stored in event.metadata['meet_link']
        """
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Calendar")
        
        try:
            creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
            service = build('calendar', 'v3', credentials=creds)
            
            # Generate unique request ID for Meet conference
            request_id = str(uuid.uuid4())
            
            event_body = {
                'summary': event.title,
                'description': event.description or '',
                'start': {
                    'dateTime': event.start.isoformat(),
                    'timeZone': event.timezone or 'UTC',
                },
                'end': {
                    'dateTime': event.end.isoformat(),
                    'timeZone': event.timezone or 'UTC',
                },
                # Add Google Meet conference - this creates the actual Meet link
                'conferenceData': {
                    'createRequest': {
                        'requestId': request_id,
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                },
            }
            
            # Add location if provided
            if event.location:
                event_body['location'] = event.location
            
            # Add attendees if provided
            send_updates = 'none'
            if event.attendees:
                event_body['attendees'] = [{'email': email} for email in event.attendees]
                send_updates = 'all'  # Send email invitations to attendees
            
            logger.info(f"Creating calendar event: {event.title} at {event.start.isoformat()} with Meet link")
            
            # Create event with conference data version to enable Meet
            created_event = service.events().insert(
                calendarId='primary',
                body=event_body,
                conferenceDataVersion=1,  # Enable Google Meet - this is required
                sendUpdates=send_updates  # Send email invitations
            ).execute()
            
            event_id = created_event.get('id')
            
            # Extract the Meet link if it was created
            meet_link = None
            conference_data = created_event.get('conferenceData')
            if conference_data:
                entry_points = conference_data.get('entryPoints', [])
                for entry_point in entry_points:
                    if entry_point.get('entryPointType') == 'video':
                        meet_link = entry_point.get('uri')
                        logger.info(f"Google Meet link created: {meet_link}")
                        break
            else:
                logger.warning("Conference data not found in created event response")
            
            # Store meet_link in event metadata for retrieval
            if meet_link:
                event.metadata['meet_link'] = meet_link
            
            logger.info(f"Calendar event created successfully with ID: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}", exc_info=True)
            raise
    
    async def get_event_meet_link(self, event_id: str) -> Optional[str]:
        """Get the Google Meet link for an event"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Calendar")
        
        try:
            creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
            service = build('calendar', 'v3', credentials=creds)
            
            event = service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            conference_data = event.get('conferenceData')
            if conference_data:
                entry_points = conference_data.get('entryPoints', [])
                for entry_point in entry_points:
                    if entry_point.get('entryPointType') == 'video':
                        return entry_point.get('uri')
            return None
        except Exception as e:
            logger.error(f"Error getting Meet link for event {event_id}: {e}", exc_info=True)
            return None
    
    async def get_events(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        search_title: Optional[str] = None
    ) -> List[CalendarEvent]:
        """Get calendar events, optionally filtering by title"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Calendar")
        
        try:
            creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
            service = build('calendar', 'v3', credentials=creds)
            
            # Default to next 30 days if no range specified
            if not start:
                from datetime import timedelta
                start = datetime.utcnow()
            if not end:
                from datetime import timedelta
                end = start + timedelta(days=30)
            
            # Build query - search by title if provided
            query = None
            if search_title:
                query = search_title
            
            # Fetch events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start.isoformat() + 'Z' if start.tzinfo is None else start.isoformat(),
                timeMax=end.isoformat() + 'Z' if end.tzinfo is None else end.isoformat(),
                q=query,  # Search query for title
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Convert to CalendarEvent objects
            calendar_events = []
            for event in events:
                # Parse start/end times
                start_data = event.get('start', {})
                end_data = event.get('end', {})
                
                start_time_str = start_data.get('dateTime') or start_data.get('date')
                end_time_str = end_data.get('dateTime') or end_data.get('date')
                
                if start_time_str:
                    try:
                        if 'T' in start_time_str:
                            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                        else:
                            # All-day event
                            start_time = datetime.fromisoformat(start_time_str)
                            start_time = start_time.replace(hour=0, minute=0)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error parsing start_time '{start_time_str}': {e}")
                        continue
                else:
                    continue
                
                if end_time_str:
                    try:
                        if 'T' in end_time_str:
                            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                        else:
                            end_time = datetime.fromisoformat(end_time_str)
                            end_time = end_time.replace(hour=23, minute=59)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error parsing end_time '{end_time_str}': {e}")
                        end_time = start_time
                else:
                    end_time = start_time
                
                # Extract attendees
                attendees = []
                for attendee in event.get('attendees', []):
                    email = attendee.get('email')
                    if email:
                        attendees.append(email)
                
                calendar_event = CalendarEvent(
                    title=event.get('summary', 'Untitled Event'),
                    start=start_time,
                    end=end_time,
                    description=event.get('description'),
                    location=event.get('location'),
                    attendees=attendees,
                    timezone=start_data.get('timeZone'),
                    metadata={'event_id': event.get('id')}
                )
                calendar_events.append(calendar_event)
            
            return calendar_events
        except Exception as e:
            logger.error(f"Error getting calendar events: {e}", exc_info=True)
            return []
    
    async def find_event_by_title(self, title: str, start_date: Optional[datetime] = None) -> Optional[str]:
        """Find an event by title, return event_id
        
        Args:
            title: Title to search for (case-insensitive partial match)
            start_date: Optional start date to limit search range (defaults to today)
            
        Returns:
            event_id if found, None otherwise
        """
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Calendar")
        
        try:
            # Search in a reasonable date range (past 7 days to future 60 days)
            from datetime import timedelta
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            end_date = start_date + timedelta(days=67)  # 7 days past + 60 days future
            
            events = await self.get_events(start=start_date, end=end_date, search_title=title)
            
            # Find exact or close matches
            title_lower = title.lower().strip()
            matches = []
            
            for event in events:
                event_title = event.title.lower().strip()
                # Exact match or contains the search title
                if event_title == title_lower or title_lower in event_title:
                    event_id = event.metadata.get('event_id')
                    if event_id:
                        matches.append((event_id, event.title, event.start))
            
            if not matches:
                return None
            
            # If multiple matches, return the most recent one (closest to now)
            if len(matches) == 1:
                return matches[0][0]
            
            # Multiple matches - return the one closest to now
            now = datetime.utcnow()
            matches.sort(key=lambda x: abs((x[2] - now).total_seconds()))
            return matches[0][0]
            
        except Exception as e:
            logger.error(f"Error finding event by title '{title}': {e}", exc_info=True)
            return None
    
    async def find_events_by_title(self, title: str, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Find all events matching a title, return list with details
        
        Args:
            title: Title to search for (case-insensitive partial match)
            start_date: Optional start date to limit search range
            
        Returns:
            List of dicts with event_id, title, start_time
        """
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Calendar")
        
        try:
            from datetime import timedelta
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=7)
            end_date = start_date + timedelta(days=67)
            
            events = await self.get_events(start=start_date, end=end_date, search_title=title)
            
            title_lower = title.lower().strip()
            matches = []
            
            for event in events:
                event_title = event.title.lower().strip()
                if event_title == title_lower or title_lower in event_title:
                    event_id = event.metadata.get('event_id')
                    if event_id:
                        matches.append({
                            'event_id': event_id,
                            'title': event.title,
                            'start': event.start,
                            'end': event.end
                        })
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding events by title '{title}': {e}", exc_info=True)
            return []
    
    async def update_event(self, event_id: str, event: CalendarEvent) -> bool:
        """Update a calendar event"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Calendar")
        
        creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
        service = build('calendar', 'v3', credentials=creds)
        
        # Get existing event first to preserve fields not being updated
        existing_event = service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        # Update fields that are marked for update in metadata
        # This allows partial updates while CalendarEvent requires all fields
        update_metadata = event.metadata or {}
        
        if update_metadata.get('update_title', False) and event.title:
            existing_event['summary'] = event.title
        
        if event.description is not None:
            existing_event['description'] = event.description or ''
        
        if update_metadata.get('update_start', False) and event.start:
            existing_event['start'] = {
                'dateTime': event.start.isoformat(),
                'timeZone': event.timezone or 'UTC',
            }
        
        if update_metadata.get('update_end', False) and event.end:
            existing_event['end'] = {
                'dateTime': event.end.isoformat(),
                'timeZone': event.timezone or 'UTC',
            }
        
        if event.location is not None:
            existing_event['location'] = event.location if event.location else None
        if event.attendees is not None:
            existing_event['attendees'] = [{'email': email} for email in event.attendees]
        
        # Send updates if there are attendees (existing or newly added)
        has_attendees = (event.attendees is not None and len(event.attendees) > 0) or \
                       (existing_event.get('attendees') and len(existing_event.get('attendees', [])) > 0)
        send_updates = 'all' if has_attendees else 'none'
        
        # Update the event
        service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=existing_event,
            sendUpdates=send_updates
        ).execute()
        
        return True
    
    async def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        # Implement Google Calendar API call
        return True

