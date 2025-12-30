"""
Message processor for handling incoming messages

SINGLE MESSAGE FLOW (ONLY PATH):
1. BlueBubbles Server → POST /api/v1/webhooks/bluebubbles
2. Webhook handler parses → parse_bluebubbles_message()
3. Emits MESSAGE_RECEIVED event → event_bus.emit()
4. MessageProcessor.handle_message() processes
5. Identifies user by phone number from chat_guid
6. Routes to user's agent → AgentService.process_task()
7. Sends response via BlueBubbles → BlueBubblesService.send_message()

This is the ONLY path for receiving messages. No polling, no direct API calls.
"""
import logging
from typing import Dict, Any, Optional
from app.core.events import event_bus, EventType
from app.core.dependencies import get_database
from app.services.agent.agent import AgentService
from app.services.user_service import UserService
from app.integrations.messaging.bluebubbles.service import BlueBubblesService
from app.integrations.messaging.base_messaging import Message
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class MessageProcessor:
    """Processes incoming messages and routes to agent"""
    
    def __init__(self):
        self.agent = AgentService()
        self.bluebubbles = BlueBubblesService()
        self._initialized = False
    
    async def initialize(self):
        """Initialize message processor and subscribe to events"""
        if self._initialized:
            return
        
        # Subscribe to MESSAGE_RECEIVED events
        # Wrap in a lambda to ensure proper async handling
        async def message_handler(data):
            await self.handle_message(data)
        
        event_bus.subscribe(EventType.MESSAGE_RECEIVED, message_handler)
        self._initialized = True
    
    async def handle_message(self, message_data: Dict[str, Any]):
        """Handle incoming message event"""
        try:
            # Skip messages from the agent itself to prevent infinite loops
            if message_data.get("is_from_me", False):
                logger.debug("Skipping message from agent itself (isFromMe=True)")
                return
            
            source = message_data.get("source", "")
            content = message_data.get("content", "")
            sender = message_data.get("sender", "")
            
            # Skip if no content or sender
            if not content or not sender:
                logger.warning(f"Skipping message with missing content or sender: {message_data}")
                return
            
            # Identify which user this message belongs to
            # In BlueBubbles, messages are sent TO the user's configured phone number
            # We need to find which user's phone number received this message
            # The chat_guid contains the recipient's phone number
            user = await self._identify_user_from_message(message_data)
            
            if not user:
                logger.warning(
                    f"Could not identify user for message from {sender}. "
                    f"Chat GUID: {message_data.get('chat_guid', 'N/A')}. "
                    f"Message will not be processed. Make sure a user has this phone number configured."
                )
                return
            
            logger.info(f"Processing incoming message from {sender} for user {user.email} (agent: {user.agent_name or 'Blume'}): {content[:50]}...")
            
            # Store user message in conversation history
            from app.core.database import SessionLocal
            from app.services.conversation_service import ConversationService
            
            db = SessionLocal()
            try:
                chat_guid = message_data.get("chat_guid")
                # Store the user message (we'll update it with the response later)
                # user.id is already a UUID object, no need to convert
                task = ConversationService.store_message(
                    db=db,
                    user_id=user.id,
                    user_message=content,
                    agent_response=None,  # Will be updated after agent responds
                    chat_guid=chat_guid,
                    metadata={
                        "source": source,
                        "sender": sender,
                        "message_guid": message_data.get("message_guid"),
                        "agent_name": user.agent_name or "Blume",
                    }
                )
                task_id = task.id
            except Exception as e:
                logger.error(f"Error storing user message: {e}", exc_info=True)
                task_id = None
            finally:
                db.close()
            
            # Process message with agent (each user gets their own agent instance)
            task_data = {
                "input": content,
                "type": "message",
                "user_id": str(user.id),
                "task_id": str(task_id) if task_id else None,  # Pass task_id to update response later
                "metadata": {
                    "source": source,
                    "sender": sender,
                    "chat_guid": message_data.get("chat_guid"),
                    "message_guid": message_data.get("message_guid"),
                    "user_id": str(user.id),
                    "agent_name": user.agent_name or "Blume",
                }
            }
            
            # Use user-specific agent (could be enhanced to have per-user agent instances)
            result = await self.agent.process_task(task_data)
            
            # If agent produced a response, send it back via BlueBubbles
            # Also handle pending_confirmation status
            if (result.get("status") in ["completed", "pending_confirmation"] and result.get("output")):
                output = result.get("output")
                
                # Only send response if it's not a function call result
                # (function calls handle their own responses)
                if not isinstance(output, dict) or "function_name" not in output:
                    # Update conversation history with agent response
                    # For pending_confirmation, also store the metadata for later retrieval
                    if task_id:
                        db = SessionLocal()
                        try:
                            ConversationService.update_agent_response(
                                db=db,
                                task_id=task_id,
                                agent_response=output
                            )
                            
                            # If this is a pending confirmation, update task metadata
                            if result.get("status") == "pending_confirmation":
                                from app.models.task import Task
                                task = db.query(Task).filter(Task.id == task_id).first()
                                if task and result.get("metadata"):
                                    # Merge confirmation metadata into task metadata
                                    if task.tast_metadata:
                                        task.tast_metadata.update(result.get("metadata", {}))
                                    else:
                                        task.tast_metadata = result.get("metadata", {})
                                    db.commit()
                        except Exception as e:
                            logger.error(f"Error updating agent response in history: {e}", exc_info=True)
                        finally:
                            db.close()
                    
                    await self._send_response(sender, output, message_data.get("chat_guid"), user)
            else:
                logger.debug(f"Agent did not produce a response. Status: {result.get('status')}, Output: {result.get('output')}")
        
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    async def _identify_user_from_message(self, message_data: Dict[str, Any]) -> Optional[Any]:
        """Identify which user a message belongs to based on chat GUID
        
        The chat GUID format is: "iMessage;-;+14089167303" where the last part is the user's phone number
        """
        try:
            from app.core.database import SessionLocal
            from app.models.user import User
            
            # Create a new database session
            db = SessionLocal()
            try:
                # Extract chat GUID which contains the recipient's phone number
                chat_guid = message_data.get("chat_guid", "")
                
                if not chat_guid:
                    logger.warning(f"No chat_guid in message data: {message_data}")
                    return None
                
                # Chat GUID format: "iMessage;-;+14089167303" or "iMessage;+;+14089167303"
                # Extract phone number from chat GUID (last part after semicolons)
                phone_number = None
                parts = chat_guid.split(";")
                
                if len(parts) >= 3:
                    # Last part is the phone number
                    potential_number = parts[-1].strip()
                    # Remove "chat" prefix if present (some formats have "chat1234567890")
                    if potential_number.startswith("chat"):
                        phone_number = potential_number.replace("chat", "").strip()
                    elif potential_number.startswith("+"):
                        phone_number = potential_number
                    else:
                        # Try adding + if it's just digits
                        phone_number = f"+{potential_number}" if potential_number.isdigit() else potential_number
                
                logger.debug(f"Extracted phone number from chat_guid '{chat_guid}': {phone_number}")
                
                # Look up user by phone number
                if phone_number:
                    user = UserService.get_user_by_phone_number(db, phone_number)
                    
                    if user:
                        logger.info(f"Identified user {user.email} from phone number {phone_number}")
                        return user
                    else:
                        logger.warning(f"No user found with phone number {phone_number}")
                
                # Fallback: Try to match any user's phone number within the chat GUID
                # This handles edge cases where the format might be slightly different
                all_users = db.query(User).filter(User.phone_number.isnot(None)).all()
                chat_guid_normalized = chat_guid.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                
                for u in all_users:
                    if not u.phone_number:
                        continue
                    user_phone_normalized = u.phone_number.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                    # Check if user's phone number appears in the chat GUID
                    if user_phone_normalized in chat_guid_normalized:
                        logger.info(f"Identified user {u.email} from chat GUID matching phone number (fallback method)")
                        return u
                
                logger.warning(f"Could not identify user for message. Chat GUID: {chat_guid}, Phone extracted: {phone_number}")
                return None
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error identifying user from message: {e}", exc_info=True)
            return None
    
    async def _send_response(self, recipient: str, content: str, chat_guid: str = None, user: Optional[Any] = None):
        """Send response message back to sender"""
        try:
            agent_name = (user.agent_name if user else None) or "Blume"
            logger.info(f"Preparing to send response to {recipient} from {agent_name}")
            
            # Create message with chat_guid in metadata if available
            # The service will use this to send directly to the existing chat
            message = Message(
                content=content,
                recipient=recipient,
                metadata={
                    "chat_guid": chat_guid,
                    "user_id": str(user.id) if user else None,
                    "agent_name": agent_name
                } if chat_guid or user else {}
            )
            
            # Use the service method which handles chat creation/finding automatically
            # It will use chat_guid from metadata if available, or find/create chat
            success = await self.bluebubbles.send_message(message)
            
            if success:
                logger.info(f"Successfully sent response to {recipient} from {agent_name}")
            else:
                logger.warning(f"Failed to send response to {recipient}")
        except Exception as e:
            logger.error(f"Error sending response to {recipient}: {e}", exc_info=True)


# Global message processor instance
message_processor = MessageProcessor()

