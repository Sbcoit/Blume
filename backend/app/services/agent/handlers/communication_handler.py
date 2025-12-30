"""
Communication handler for messaging and calling tasks
"""
from typing import Dict, Any
from app.services.agent.handlers.base_handler import BaseHandler
from app.services.agent.llm.base import LLMMessage, FunctionDefinition
from app.integrations.messaging.bluebubbles.service import BlueBubblesService
from app.integrations.messaging.base_messaging import Message
from app.integrations.voice.vapi.service import VapiService
import json


class CommunicationHandler(BaseHandler):
    """Handler for communication tasks (messaging and calling)"""
    
    def __init__(
        self,
        bluebubbles_service: BlueBubblesService = None,
        vapi_service: VapiService = None
    ):
        self.bluebubbles = bluebubbles_service or BlueBubblesService()
        self.vapi = vapi_service or VapiService()
    
    @property
    def task_type(self) -> str:
        return "communication"
    
    def can_handle(self, task_data: Dict[str, Any]) -> bool:
        """Check if this handler can handle the task"""
        task_input = task_data.get("input", "").lower()
        communication_keywords = [
            "message", "text", "sms", "send", "call", "phone", "voice",
            "contact", "reach out", "get in touch", "call me", "text me"
        ]
        return any(keyword in task_input for keyword in communication_keywords)
    
    async def handle(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a communication task"""
        from app.services.agent.llm.groq_client import GroqClient
        from app.services.conversation_service import ConversationService
        from app.core.database import SessionLocal
        from uuid import UUID
        
        llm = GroqClient()
        input_text = task_data.get("input", "")
        
        # Get conversation history
        db = SessionLocal()
        try:
            user_id = UUID(task_data.get("user_id"))
            chat_guid = task_data.get("metadata", {}).get("chat_guid")
            agent_name = task_data.get("metadata", {}).get("agent_name", "Blume")
            
            # Retrieve recent conversation history (last 10 message pairs)
            history = ConversationService.get_recent_history(
                db=db,
                user_id=user_id,
                limit=10,
                chat_guid=chat_guid
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error retrieving conversation history: {e}", exc_info=True)
            history = []
            agent_name = "Blume"
        finally:
            db.close()
        
        # Define functions for LLM to call
        functions = [
            FunctionDefinition(
                name="execute_communication_action",
                description="Perform communication operations: send (send text message via iMessage), call (make voice call)",
                parameters={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["send", "call"],
                            "description": "Action to perform: 'send' (send text message), 'call' (make voice call)"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Action-specific parameters. For 'send': {recipient (required string), content (required string)}. For 'call': {recipient (required string), purpose (optional string)}."
                        }
                    },
                    "required": ["action", "parameters"]
                }
            )
        ]
        
        # Build messages with system prompt, history, and current message
        messages = [
            LLMMessage(
                role="system",
                content=f"You are {agent_name}, a helpful personal assistant. When the user wants to send a message or make a call, use the appropriate function. Determine the recipient and content from the user's request. You have access to conversation history to maintain context."
            )
        ]
        
        # Add conversation history (excluding the current message which we'll add next)
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
            result = await llm.chat(messages, functions=functions)
            
            # Check if function call was made
            if isinstance(result, dict) and "function_name" in result:
                function_name = result["function_name"]
                arguments = json.loads(result["arguments"]) if isinstance(result["arguments"], str) else result["arguments"]
                
                # Execute the function call
                if function_name == "execute_communication_action":
                    return await self._handle_communication_action(arguments)
                else:
                    return {
                        "status": "failed",
                        "output": f"Unknown function: {function_name}",
                        "metadata": {"handler": "communication_handler"}
                    }
            else:
                # LLM responded with text (no function call)
                return {
                    "status": "completed",
                    "output": result,
                    "metadata": {"handler": "communication_handler", "action": "text_response"}
                }
        except Exception as e:
            return {
                "status": "failed",
                "output": f"Error processing communication task: {str(e)}",
                "metadata": {"error": str(e), "handler": "communication_handler"}
            }
    
    async def _handle_communication_action(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle execute_communication_action function call"""
        action = arguments.get("action")
        params = arguments.get("parameters", {})
        
        if action == "send":
            return await self._handle_send_message(params)
        elif action == "call":
            return await self._handle_make_call(params)
        else:
            return {
                "status": "failed",
                "output": f"Unknown communication action: {action}. Valid actions are: send, call",
                "metadata": {"handler": "communication_handler"}
            }
    
    async def _handle_send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send message action"""
        try:
            recipient = params.get("recipient")
            content = params.get("content")
            
            if not recipient or not content:
                return {
                    "status": "failed",
                    "output": "Missing recipient or content for message",
                    "metadata": {"handler": "communication_handler"}
                }
            
            message = Message(
                content=content,
                recipient=recipient
            )
            
            success = await self.bluebubbles.send_message(message)
            
            if success:
                return {
                    "status": "completed",
                    "output": f"Message sent to {recipient}: {content}",
                    "metadata": {
                        "handler": "communication_handler",
                        "action": "send",
                        "recipient": recipient
                    }
                }
            else:
                return {
                    "status": "failed",
                    "output": f"Failed to send message to {recipient}",
                    "metadata": {"handler": "communication_handler"}
                }
        except Exception as e:
            return {
                "status": "failed",
                "output": f"Error sending message: {str(e)}",
                "metadata": {"error": str(e), "handler": "communication_handler"}
            }
    
    async def _handle_make_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle make call action"""
        try:
            recipient = params.get("recipient")
            purpose = params.get("purpose")
            
            if not recipient:
                return {
                    "status": "failed",
                    "output": "Missing recipient for call",
                    "metadata": {"handler": "communication_handler"}
                }
            
            call = await self.vapi.make_call(recipient, purpose)
            
            return {
                "status": "completed",
                "output": f"Call initiated to {recipient}" + (f" for: {purpose}" if purpose else ""),
                "metadata": {
                    "handler": "communication_handler",
                    "action": "call",
                    "recipient": recipient,
                    "call_id": call.call_id,
                    "status": call.status
                }
            }
        except Exception as e:
            return {
                "status": "failed",
                "output": f"Error making call: {str(e)}",
                "metadata": {"error": str(e), "handler": "communication_handler"}
            }

