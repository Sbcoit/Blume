"""
Scheduling handler for agent tasks
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
import json
import logging

from app.core.database import SessionLocal
from app.integrations.calendar.base_calendar import CalendarEvent
from app.integrations.calendar.google_calendar.service import GoogleCalendarService
from app.integrations.google.oauth import GoogleOAuth
from app.models.integration import Integration, IntegrationProvider
from app.models.task import Task, TaskStatus
from app.services.agent.handlers.base_handler import BaseHandler
from app.services.agent.llm.base import LLMMessage, FunctionDefinition
from app.services.agent.llm.groq_client import GroqClient
from app.services.conversation_service import ConversationService
from app.services.integration_service import IntegrationService
from app.services.user_service import UserService
from sqlalchemy import desc

logger = logging.getLogger(__name__)


class SchedulingHandler(BaseHandler):
    """Handler for scheduling tasks"""
    
    @property
    def task_type(self) -> str:
        return "scheduling"
    
    def can_handle(self, task_data: Dict[str, Any]) -> bool:
        """Check if this handler can handle the task"""
        task_input = task_data.get("input", "").lower()
        
        # Check if this is a confirmation response for a pending update
        metadata = task_data.get("metadata", {})
        if metadata.get("pending_update_event_id"):
            # This is a confirmation for a pending update
            return True
        
        scheduling_keywords = [
            "schedule", "meeting", "appointment", "calendar", 
            "book", "reserve", "set up", "plan", "event", "meet", "google meet",
            "yes", "no", "confirm", "proceed"  # Also handle confirmations
        ]
        # Match if it contains any scheduling-related keyword
        # This will catch both create and update requests (update requests usually mention "meeting", "meet", etc.)
        return any(keyword in task_input for keyword in scheduling_keywords)
    
    async def handle(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a scheduling task"""
        user_id = UUID(task_data.get("user_id"))
        db = SessionLocal()
        
        try:
            # Check if this is a confirmation response for a pending update
            input_text = task_data.get("input", "").lower().strip()
            metadata = task_data.get("metadata", {})
            
            # Check conversation history for pending confirmation
            chat_guid = task_data.get("metadata", {}).get("chat_guid")
            history = ConversationService.get_recent_history(
                db=db,
                user_id=user_id,
                limit=5,
                chat_guid=chat_guid
            )
            
            # Look for recent pending_confirmation status in history
            # Check the most recent agent response for pending update info
            if history and len(history) >= 2:
                # Get the most recent agent response
                for i in range(len(history) - 1, -1, -1):
                    if history[i].get("role") == "assistant":
                        # Check if this response was asking for confirmation
                        # We'll check the task metadata instead
                        break
            
            # Check recent tasks for pending confirmation
            recent_tasks = db.query(Task).filter(
                Task.user_id == user_id,
                Task.status == TaskStatus.COMPLETED,
                Task.tast_metadata.isnot(None)
            ).order_by(desc(Task.created_at)).limit(3).all()
            
            for task in recent_tasks:
                if task.tast_metadata and isinstance(task.tast_metadata, dict):
                    task_meta = task.tast_metadata
                    # Check if this task had a pending confirmation
                    if (task_meta.get("handler") == "scheduling_handler" and 
                        task_meta.get("action") == "update" and
                        task_meta.get("requires_confirmation") and
                        task_meta.get("event_id")):
                        
                        # This is a confirmation response
                        event_id = task_meta.get("event_id")
                        update_params = task_meta.get("update_params", {})
                        
                        # Check if user confirmed
                        is_confirmation = any(word in input_text for word in ["yes", "yep", "yeah", "confirm", "proceed", "go ahead", "do it"])
                        is_rejection = any(word in input_text for word in ["no", "nope", "cancel", "stop", "don't", "dont"])
                        
                        if is_confirmation:
                            # User confirmed - proceed with update
                            user = UserService.get_user_by_id(db, user_id)
                            user_timezone = user.timezone if user and user.timezone else 'America/Los_Angeles'
                            
                            calendar_integration = db.query(Integration).filter(
                                Integration.user_id == user_id,
                                Integration.provider == IntegrationProvider.GOOGLE_CALENDAR.value,
                                Integration.status == "connected"
                            ).first()
                            
                            if calendar_integration and calendar_integration.credentials:
                                calendar_service = GoogleCalendarService()
                                await calendar_service.connect(calendar_integration.credentials)
                                
                                return await self._handle_update_event(event_id, update_params, calendar_service, user_timezone)
                        
                        elif is_rejection:
                            return {
                                "status": "completed",
                                "output": "Update cancelled. No changes were made.",
                                "metadata": {"handler": "scheduling_handler"}
                            }
                        # If neither confirmation nor rejection, continue with normal flow
            
            # Get user to access their timezone
            user = UserService.get_user_by_id(db, user_id)
            user_timezone = user.timezone if user and user.timezone else 'America/Los_Angeles'
            
            # Check if Google Calendar is connected
            if not IntegrationService.is_integration_connected(db, user_id, "google"):
                return {
                    "status": "completed",
                    "output": "You haven't set up Google Calendar yet. Please connect your Google Account in Settings to use calendar features.",
                    "metadata": {"handler": "scheduling_handler", "missing_integration": "google"}
                }
            
            # Get Google Calendar credentials
            calendar_integration = db.query(Integration).filter(
                Integration.user_id == user_id,
                Integration.provider == IntegrationProvider.GOOGLE_CALENDAR.value,
                Integration.status == "connected"
            ).first()
            
            if not calendar_integration or not calendar_integration.credentials:
                return {
                    "status": "completed",
                    "output": "Google Calendar credentials not found. Please reconnect your Google Account in Settings.",
                    "metadata": {"handler": "scheduling_handler", "missing_integration": "google"}
                }
            
            # Get conversation history
            chat_guid = task_data.get("metadata", {}).get("chat_guid")
            agent_name = task_data.get("metadata", {}).get("agent_name", "Blume")
            
            history = ConversationService.get_recent_history(
                db=db,
                user_id=user_id,
                limit=10,
                chat_guid=chat_guid
            )
            
            # Initialize calendar service
            calendar_service = GoogleCalendarService()
            await calendar_service.connect(calendar_integration.credentials)
            
            # Use LLM to parse scheduling request
            llm = GroqClient()
            input_text = task_data.get("input", "")
            
            functions = [
                FunctionDefinition(
                    name="execute_calendar_action",
                    description="Perform calendar/event operations: create (create new event), update (update existing event), delete (delete event)",
                    parameters={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["create", "update"],
                                "description": "Action to perform: 'create' (create new calendar event/meeting), 'update' (update existing event - use this when user says 'change', 'update', 'modify', 'edit')"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Action-specific parameters. For 'create': {title (required), start_time (required), end_time (optional), description (optional), location (optional), attendees (optional array)}. For 'update': {event_id (optional), search_title (optional - search for event by title), title (optional - new title), start_time (optional), end_time (optional), description (optional), location (optional), attendees (optional array)}. If neither event_id nor search_title is provided, will use most recent event. Use ISO 8601 format for times."
                            }
                        },
                        "required": ["action", "parameters"]
                    }
                )
            ]
            
            # Get current date/time for context (using user's timezone)
            user_tz = ZoneInfo(user_timezone)
            current_datetime = datetime.now(user_tz)
            current_date_str = current_datetime.strftime("%Y-%m-%d")
            current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")
            
            # Build messages with system prompt, history, and current message
            messages = [
                LLMMessage(
                    role="system",
                    content=f"You are {agent_name}, a helpful personal assistant. IMPORTANT: When the user wants to schedule, create, update, change, modify, or edit a meeting/appointment/calendar event, you MUST use the execute_calendar_action function. Use action='create' for new events, action='update' for modifying existing events (when user says 'change', 'update', 'modify', 'edit'). For updates: you can provide 'search_title' to find an event by its title (e.g., if user says 'change the meeting called Google Meet', use search_title='Google Meet'). If neither event_id nor search_title is provided, the system will use the most recent event. Extract the title, start time, end time (or calculate 1 hour duration if not specified), location, and attendees from the user's request. Use ISO 8601 format for dates in {user_timezone} timezone. Example: 2024-12-30T21:00:00 for 9 PM in {user_timezone}. CURRENT DATE AND TIME: {current_datetime_str} (Today is {current_date_str}). When the user says 'tomorrow', 'next week', '9 PM', etc., calculate the actual date and time based on the current date and time in {user_timezone}. You have access to conversation history to maintain context."
                )
            ]
            
            # Add conversation history
            for msg in history:
                messages.append(LLMMessage(
                    role=msg["role"],
                    content=msg["content"]
                ))
            
            # Add current user message
            messages.append(LLMMessage(
                role="user",
                content=input_text
            ))
            
            try:
                # Call LLM with function definitions
                logger.info(f"[SchedulingHandler] Calling LLM with {len(functions)} function(s) for scheduling request: {input_text[:100]}")
                result = await llm.chat(messages, functions=functions)
                
                # Log what we got back
                logger.info(f"LLM result type: {type(result)}, content preview: {str(result)[:300]}")
                
                # Check if function call was made
                if isinstance(result, dict) and "function_name" in result:
                    function_name = result["function_name"]
                    logger.info(f"✅ Function call detected: {function_name}")
                    arguments = json.loads(result["arguments"]) if isinstance(result["arguments"], str) else result["arguments"]
                    logger.info(f"Function arguments: {arguments}")
                    
                    if function_name == "execute_calendar_action":
                        chat_guid_for_lookup = task_data.get("metadata", {}).get("chat_guid")
                        return await self._handle_calendar_action(arguments, calendar_service, user_timezone, user_id, db, chat_guid_for_lookup)
                    else:
                        return {
                            "status": "failed",
                            "output": f"Unknown function: {function_name}",
                            "metadata": {"handler": "scheduling_handler"}
                        }
                else:
                    # LLM responded with text (no function call)
                    logger.warning(f"⚠️ LLM returned text instead of function call. Result: {result}")
                    return {
                        "status": "completed",
                        "output": result,
                        "metadata": {"handler": "scheduling_handler", "action": "text_response"}
                    }
            except Exception as e:
                logger.error(f"Error processing scheduling task: {e}", exc_info=True)
                return {
                    "status": "failed",
                    "output": f"Error processing scheduling request: {str(e)}",
                    "metadata": {"error": str(e), "handler": "scheduling_handler"}
                }
        finally:
            db.close()
    
    def _get_most_recent_event_id(self, db: Session, user_id: UUID, chat_guid: Optional[str] = None) -> Optional[str]:
        """Get the most recent event_id from task metadata"""
        try:
            query = db.query(Task).filter(
                Task.user_id == user_id,
                Task.status == TaskStatus.COMPLETED,
                Task.tast_metadata.isnot(None)
            )
            
            if chat_guid:
                query = query.filter(
                    Task.tast_metadata['chat_guid'].astext == chat_guid
                )
            
            # Get recent tasks ordered by creation time
            tasks = query.order_by(desc(Task.created_at)).limit(20).all()
            
            # Find the most recent task with event_id in metadata
            for task in tasks:
                if task.tast_metadata and isinstance(task.tast_metadata, dict):
                    # Check if metadata has event_id (could be nested)
                    metadata = task.tast_metadata
                    if isinstance(metadata, dict):
                        # Check handler metadata
                        if metadata.get("handler") == "scheduling_handler":
                            # Check nested metadata structure
                            result_metadata = metadata.get("metadata") or {}
                            if isinstance(result_metadata, dict) and "event_id" in result_metadata:
                                return result_metadata["event_id"]
                            # Also check direct metadata
                            if "event_id" in metadata:
                                return metadata["event_id"]
                        # Also check if event_id is at top level (from previous versions)
                        if "event_id" in metadata:
                            return metadata["event_id"]
            
            return None
        except Exception as e:
            logger.warning(f"Error getting most recent event_id: {e}")
            return None
    
    async def _handle_calendar_action(self, arguments: Dict[str, Any], calendar_service: GoogleCalendarService, user_timezone: str, user_id: UUID, db: Session, chat_guid: Optional[str] = None) -> Dict[str, Any]:
        """Handle execute_calendar_action function call"""
        action = arguments.get("action")
        params = arguments.get("parameters", {})
        
        if action == "create":
            result = await self._handle_create_event(params, calendar_service, user_timezone)
            # Store event_id in task metadata so we can retrieve it later for updates
            if result.get("status") == "completed" and result.get("metadata", {}).get("event_id"):
                # This will be stored when the result is processed
                pass
            return result
        elif action == "update":
            # Get event_id from params, search by title, or use most recent
            event_id = params.get("event_id")
            search_title = params.get("search_title")
            found_by_title = False
            
            if not event_id:
                if search_title:
                    # Search for event by title
                    logger.info(f"Searching for event by title: {search_title}")
                    matching_events = await calendar_service.find_events_by_title(search_title)
                    
                    if not matching_events:
                        return {
                            "status": "failed",
                            "output": f"No event found with title matching '{search_title}'. Please check the title or create a new event.",
                            "metadata": {"handler": "scheduling_handler"}
                        }
                    
                    if len(matching_events) == 1:
                        # Single match - use it
                        event_id = matching_events[0]['event_id']
                        found_by_title = True
                        logger.info(f"Found single event by title: {event_id} - {matching_events[0]['title']}")
                    else:
                        # Multiple matches - ask for confirmation
                        event_list = "\n".join([
                            f"{i+1}. '{ev['title']}' on {ev['start'].strftime('%Y-%m-%d %H:%M')}"
                            for i, ev in enumerate(matching_events[:5])  # Limit to 5
                        ])
                        return {
                            "status": "pending_confirmation",
                            "output": f"Found {len(matching_events)} events matching '{search_title}':\n{event_list}\n\nWhich event would you like to update? Please specify the number (1-{min(len(matching_events), 5)}) or provide more details.",
                            "metadata": {
                                "handler": "scheduling_handler",
                                "action": "update",
                                "matching_events": matching_events[:5],
                                "search_title": search_title,
                                "update_params": params
                            }
                        }
                else:
                    # Fall back to most recent
                    logger.info(f"Looking up most recent event_id for user {user_id}, chat_guid {chat_guid}")
                    event_id = self._get_most_recent_event_id(db, user_id, chat_guid)
                    logger.info(f"Found event_id: {event_id}")
                    if not event_id:
                        return {
                            "status": "failed",
                            "output": "No event_id provided and no recent event found. Please specify which event to update by title or create a new event first.",
                            "metadata": {"handler": "scheduling_handler"}
                        }
            
            # Get event details for confirmation
            if found_by_title or search_title:
                # Fetch event details to show user what will be updated
                try:
                    creds = GoogleOAuth.get_credentials_from_dict(calendar_service.get_credentials())
                    from googleapiclient.discovery import build
                    service = build('calendar', 'v3', credentials=creds)
                    existing_event = service.events().get(
                        calendarId='primary',
                        eventId=event_id
                    ).execute()
                    
                    event_title = existing_event.get('summary', 'Untitled')
                    start_data = existing_event.get('start', {})
                    start_time_str = start_data.get('dateTime') or start_data.get('date', '')
                    
                    # Ask for confirmation before updating
                    changes = []
                    if params.get("title"):
                        changes.append(f"title from '{event_title}' to '{params['title']}'")
                    if params.get("start_time"):
                        changes.append("start time")
                    if params.get("end_time"):
                        changes.append("end time")
                    if params.get("description") is not None:
                        changes.append("description")
                    if params.get("location") is not None:
                        changes.append("location")
                    if params.get("attendees") is not None:
                        changes.append("attendees")
                    
                    if changes:
                        confirmation_msg = f"Found event '{event_title}'"
                        if start_time_str:
                            confirmation_msg += f" scheduled for {start_time_str[:10]}"
                        confirmation_msg += f". I'll update: {', '.join(changes)}. Should I proceed? (yes/no)"
                        
                        return {
                            "status": "pending_confirmation",
                            "output": confirmation_msg,
                            "metadata": {
                                "handler": "scheduling_handler",
                                "action": "update",
                                "event_id": event_id,
                                "event_title": event_title,
                                "update_params": params,
                                "requires_confirmation": True
                            }
                        }
                except Exception as e:
                    logger.warning(f"Error fetching event for confirmation: {e}")
                    # Continue without confirmation if we can't fetch event details
            
            logger.info(f"Updating event {event_id} with params: {params}")
            return await self._handle_update_event(event_id, params, calendar_service, user_timezone)
        else:
            return {
                "status": "failed",
                "output": f"Unknown calendar action: {action}. Valid actions are: create, update",
                "metadata": {"handler": "scheduling_handler"}
            }
    
    async def _handle_create_event(self, params: Dict[str, Any], calendar_service: GoogleCalendarService, user_timezone: str = 'America/Los_Angeles') -> Dict[str, Any]:
        """Handle create calendar event action"""
        try:
            title = params.get("title")
            start_time_str = params.get("start_time")
            end_time_str = params.get("end_time")
            description = params.get("description")
            location = params.get("location")
            attendees = params.get("attendees", [])
            
            if not title or not start_time_str:
                return {
                    "status": "failed",
                    "output": "Missing required fields: title and start_time are required",
                    "metadata": {"handler": "scheduling_handler"}
                }
            
            # Parse datetime strings and ensure they're in user's timezone
            user_tz = ZoneInfo(user_timezone)
            
            try:
                # Parse the datetime string
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                # If no timezone info, assume it's in user's timezone
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=user_tz)
                # Convert to user's timezone if it's in a different timezone
                else:
                    start_time = start_time.astimezone(user_tz)
            except ValueError:
                return {
                    "status": "failed",
                    "output": f"Invalid start_time format: {start_time_str}. Please use ISO 8601 format (e.g., 2024-01-15T14:00:00)",
                    "metadata": {"handler": "scheduling_handler"}
                }
            
            # Calculate end time (default to 1 hour if not provided)
            if end_time_str:
                try:
                    end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                    # If no timezone info, assume it's in user's timezone
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=user_tz)
                    # Convert to user's timezone if it's in a different timezone
                    else:
                        end_time = end_time.astimezone(user_tz)
                except ValueError:
                    return {
                        "status": "failed",
                        "output": f"Invalid end_time format: {end_time_str}. Please use ISO 8601 format",
                        "metadata": {"handler": "scheduling_handler"}
                    }
            else:
                # Default to 1 hour duration
                end_time = start_time + timedelta(hours=1)
            
            # Create calendar event with user's timezone
            event = CalendarEvent(
                title=title,
                start=start_time,
                end=end_time,
                description=description,
                location=location,
                attendees=attendees,
                timezone=user_timezone
            )
            
            event_id = await calendar_service.create_event(event)
            
            # Get the Meet link from event metadata or by fetching the event
            meet_link = event.metadata.get('meet_link')
            if not meet_link:
                meet_link = await calendar_service.get_event_meet_link(event_id)
            
            output = f"Successfully scheduled '{title}' from {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}"
            if meet_link:
                output += f"\n\nGoogle Meet: {meet_link}"
            if location:
                output += f"\nLocation: {location}"
            
            return {
                "status": "completed",
                "output": output,
                "metadata": {
                    "handler": "scheduling_handler",
                    "action": "create",
                    "event_id": event_id,
                    "meet_link": meet_link
                }
            }
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}", exc_info=True)
            return {
                "status": "failed",
                "output": f"Error creating calendar event: {str(e)}",
                "metadata": {"error": str(e), "handler": "scheduling_handler"}
            }
    
    async def _handle_update_event(self, event_id: str, params: Dict[str, Any], calendar_service: GoogleCalendarService, user_timezone: str = 'America/Los_Angeles') -> Dict[str, Any]:
        """Handle update calendar event action"""
        try:
            from datetime import datetime
            from zoneinfo import ZoneInfo
            
            user_tz = ZoneInfo(user_timezone)
            
            # Parse times if provided
            start_time = None
            end_time = None
            
            if params.get("start_time"):
                try:
                    start_time_str = params.get("start_time")
                    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    if start_time.tzinfo is None:
                        start_time = start_time.replace(tzinfo=user_tz)
                    else:
                        start_time = start_time.astimezone(user_tz)
                except ValueError:
                    return {
                        "status": "failed",
                        "output": f"Invalid start_time format: {params.get('start_time')}. Please use ISO 8601 format",
                        "metadata": {"handler": "scheduling_handler"}
                    }
            
            if params.get("end_time"):
                try:
                    end_time_str = params.get("end_time")
                    end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=user_tz)
                    else:
                        end_time = end_time.astimezone(user_tz)
                except ValueError:
                    return {
                        "status": "failed",
                        "output": f"Invalid end_time format: {params.get('end_time')}. Please use ISO 8601 format",
                        "metadata": {"handler": "scheduling_handler"}
                    }
            
            # Determine which fields to update - use metadata to mark fields for update
            # The update_event method will get existing values, so we can use dummy values here
            # for required CalendarEvent fields
            update_metadata = {}
            now = datetime.now(user_tz)
            
            if params.get("title"):
                update_metadata['update_title'] = True
            if start_time:
                update_metadata['update_start'] = True
            if end_time:
                update_metadata['update_end'] = True
            
            # Create CalendarEvent with fields to update
            # Use dummy values for required fields - update_event will get real values from existing event
            event = CalendarEvent(
                title=params.get("title", ""),  # Will only be used if update_title is True
                start=start_time or now,  # Will only be used if update_start is True
                end=end_time or (now + timedelta(hours=1)),  # Will only be used if update_end is True
                description=params.get("description"),  # None means don't update
                location=params.get("location"),  # None means don't update
                attendees=params.get("attendees"),  # None means don't update
                timezone=user_timezone,
                metadata=update_metadata
            )
            
            # Update the event - update_event will get existing values and only update marked fields
            success = await calendar_service.update_event(event_id, event)
            
            if success:
                updated_fields = []
                if params.get("title"):
                    updated_fields.append(f"title to '{params['title']}'")
                if params.get("start_time"):
                    updated_fields.append("start time")
                if params.get("end_time"):
                    updated_fields.append("end time")
                if params.get("description") is not None:
                    updated_fields.append("description")
                if params.get("location") is not None:
                    updated_fields.append("location")
                if params.get("attendees") is not None:
                    updated_fields.append("attendees")
                
                return {
                    "status": "completed",
                    "output": f"Successfully updated calendar event. Changed: {', '.join(updated_fields) if updated_fields else 'event details'}",
                    "metadata": {
                        "handler": "scheduling_handler",
                        "action": "update",
                        "event_id": event_id
                    }
                }
            else:
                return {
                    "status": "failed",
                    "output": f"Failed to update calendar event",
                    "metadata": {"handler": "scheduling_handler"}
                }
        except Exception as e:
            logger.error(f"Error updating calendar event: {e}", exc_info=True)
            return {
                "status": "failed",
                "output": f"Error updating calendar event: {str(e)}",
                "metadata": {"error": str(e), "handler": "scheduling_handler"}
            }

