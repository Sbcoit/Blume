"""
BlueBubbles webhook event handler
"""
from typing import Dict, Any
from app.integrations.messaging.bluebubbles.service import BlueBubblesService


class BlueBubblesWebhookHandler:
    """Handler for BlueBubbles webhook events"""
    
    def __init__(self):
        self.service = BlueBubblesService()
    
    async def handle_message_received(self, event_data: Dict[str, Any]):
        """Handle new message received event"""
        message = await self.service.receive_message(event_data)
        return message
    
    async def handle_message_updated(self, event_data: Dict[str, Any]):
        """Handle message updated event"""
        # Process message update if needed
        pass

