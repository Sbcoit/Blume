"""
BlueBubbles webhook handler
"""
from fastapi import APIRouter, Request, BackgroundTasks
from typing import Dict, Any
from app.core.events import event_bus, EventType
from app.integrations.messaging.bluebubbles.service import BlueBubblesService

router = APIRouter(prefix="/webhooks/bluebubbles", tags=["webhooks"])


def parse_bluebubbles_message(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parse BlueBubbles webhook payload into structured message data"""
    # BlueBubbles webhook structure can vary, handle common formats
    event_type = payload.get("event", {}).get("type") or payload.get("type")
    
    # Extract message data
    message_data = payload.get("message") or payload.get("data", {}).get("message") or {}
    chat_data = payload.get("chat") or payload.get("data", {}).get("chat") or {}
    
    # Extract sender information
    sender_handle = message_data.get("handle") or message_data.get("sender")
    if isinstance(sender_handle, dict):
        sender = sender_handle.get("address") or sender_handle.get("id") or str(sender_handle)
    else:
        sender = str(sender_handle) if sender_handle else ""
    
    # Extract message content
    content = message_data.get("text") or message_data.get("body") or message_data.get("message") or ""
    
    # Extract chat GUID
    chat_guid = (
        chat_data.get("guid") or 
        chat_data.get("chatGuid") or 
        message_data.get("chatGuid") or
        payload.get("chatGuid") or
        ""
    )
    
    # Extract message GUID
    message_guid = message_data.get("guid") or message_data.get("id") or ""
    
    return {
        "type": "message",
        "source": "bluebubbles",
        "event_type": event_type,
        "sender": sender,
        "content": content,
        "chat_guid": chat_guid,
        "message_guid": message_guid,
        "raw": payload
    }


async def process_webhook_event(event_data: Dict[str, Any]):
    """Process webhook event in background"""
    try:
        # Parse and structure the message data
        structured_data = parse_bluebubbles_message(event_data)
        
        # Emit event for agent to process
        await event_bus.emit(EventType.MESSAGE_RECEIVED, structured_data)
    except Exception as e:
        print(f"Error processing BlueBubbles webhook event: {e}")


@router.post("")
async def bluebubbles_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle incoming BlueBubbles webhook"""
    try:
        # Get webhook payload
        payload = await request.json()
        
        # Process in background
        background_tasks.add_task(process_webhook_event, payload)
        
        # Return success immediately
        return {"status": "received"}
    except Exception as e:
        print(f"Error handling BlueBubbles webhook: {e}")
        return {"status": "error", "message": str(e)}, 500

