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
        
        llm = GroqClient()
        input_text = task_data.get("input", "")
        
        # Define functions for LLM to call
        functions = [
            FunctionDefinition(
                name="send_message",
                description="Send a text message to a phone number via iMessage",
                parameters={
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Phone number or contact identifier to send message to"
                        },
                        "content": {
                            "type": "string",
                            "description": "Message content to send"
                        }
                    },
                    "required": ["recipient", "content"]
                }
            ),
            FunctionDefinition(
                name="make_call",
                description="Make a voice call to a phone number",
                parameters={
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": "Phone number to call"
                        },
                        "purpose": {
                            "type": "string",
                            "description": "Optional purpose or context for the call"
                        }
                    },
                    "required": ["recipient"]
                }
            )
        ]
        
        # Create messages with system prompt
        messages = [
            LLMMessage(
                role="system",
                content="You are Blume, a helpful personal assistant. When the user wants to send a message or make a call, use the appropriate function. Determine the recipient and content from the user's request."
            ),
            LLMMessage(
                role="user",
                content=input_text
            )
        ]
        
        try:
            # Call LLM with function definitions
            result = await llm.chat(messages, functions=functions)
            
            # Check if function call was made
            if isinstance(result, dict) and "function_name" in result:
                function_name = result["function_name"]
                arguments = json.loads(result["arguments"]) if isinstance(result["arguments"], str) else result["arguments"]
                
                # Execute the function call
                if function_name == "send_message":
                    return await self._handle_send_message(arguments)
                elif function_name == "make_call":
                    return await self._handle_make_call(arguments)
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
    
    async def _handle_send_message(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle send_message function call"""
        try:
            recipient = arguments.get("recipient")
            content = arguments.get("content")
            
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
                        "action": "send_message",
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
    
    async def _handle_make_call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle make_call function call"""
        try:
            recipient = arguments.get("recipient")
            purpose = arguments.get("purpose")
            
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
                    "action": "make_call",
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

