"""
Message processor for handling incoming messages
"""
from typing import Dict, Any
from app.core.events import event_bus, EventType
from app.services.agent.agent import AgentService
from app.integrations.messaging.bluebubbles.service import BlueBubblesService
from app.integrations.messaging.base_messaging import Message


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
            source = message_data.get("source", "")
            content = message_data.get("content", "")
            sender = message_data.get("sender", "")
            
            # Skip if no content or sender
            if not content or not sender:
                print(f"Skipping message with missing content or sender: {message_data}")
                return
            
            # Process message with agent
            task_data = {
                "input": content,
                "type": "message",
                "metadata": {
                    "source": source,
                    "sender": sender,
                    "chat_guid": message_data.get("chat_guid"),
                    "message_guid": message_data.get("message_guid"),
                }
            }
            
            result = await self.agent.process_task(task_data)
            
            # If agent produced a response, send it back via BlueBubbles
            if result.get("status") == "completed" and result.get("output"):
                output = result.get("output")
                
                # Only send response if it's not a function call result
                # (function calls handle their own responses)
                if not isinstance(output, dict) or "function_name" not in output:
                    await self._send_response(sender, output, message_data.get("chat_guid"))
        
        except Exception as e:
            print(f"Error handling message: {e}")
    
    async def _send_response(self, recipient: str, content: str, chat_guid: str = None):
        """Send response message back to sender"""
        try:
            message = Message(
                content=content,
                recipient=recipient
            )
            
            # If we have chat_guid, we can use it directly
            if chat_guid:
                # Use BlueBubbles client directly to send to existing chat
                from app.integrations.messaging.bluebubbles.client import BlueBubblesClient
                client = BlueBubblesClient()
                await client.send_message(
                    chat_guid=chat_guid,
                    message=content
                )
            else:
                # Fallback to service method which will create/find chat
                await self.bluebubbles.send_message(message)
        except Exception as e:
            print(f"Error sending response: {e}")


# Global message processor instance
message_processor = MessageProcessor()

