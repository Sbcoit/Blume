"""
BlueBubbles webhook handler

This is the SINGLE entry point for receiving messages from BlueBubbles.
All incoming messages flow through: BlueBubbles Server → webhook endpoint → parse → event bus → MessageProcessor

No other message receiving mechanisms should be used (no polling, no direct API calls).
"""
import logging
from fastapi import APIRouter, Request, BackgroundTasks
from typing import Dict, Any
from app.core.events import event_bus, EventType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/bluebubbles", tags=["webhooks"])


def parse_bluebubbles_message(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parse BlueBubbles webhook payload into structured message data"""
    # BlueBubbles webhook structure: {"type": "new-message", "data": {...message data...}}
    event_type = payload.get("type") or payload.get("event", {}).get("type")
    
    # Extract message data - BlueBubbles sends data directly in "data" field
    message_data = payload.get("data") or payload.get("message") or {}
    
    # If data is nested, try to get it
    if not message_data and isinstance(payload.get("data"), dict):
        message_data = payload.get("data")
    
    # CRITICAL: Skip messages from the agent itself to prevent infinite loops
    is_from_me = message_data.get("isFromMe", False)
    if is_from_me:
        # Return a special marker to skip processing
        return {
            "type": "message",
            "source": "bluebubbles",
            "event_type": event_type,
            "sender": "",
            "content": "",
            "chat_guid": "",
            "message_guid": "",
            "is_from_me": True,  # Marker to skip
            "raw": payload
        }
    
    # Extract sender information
    sender_handle = message_data.get("handle") or message_data.get("sender")
    if isinstance(sender_handle, dict):
        sender = sender_handle.get("address") or sender_handle.get("id") or str(sender_handle)
    else:
        sender = str(sender_handle) if sender_handle else ""
    
    # Extract message content
    content = message_data.get("text") or message_data.get("body") or message_data.get("message") or ""
    
    # Extract chat GUID - BlueBubbles sends chats as an array in message data
    chat_guid = ""
    chats = message_data.get("chats") or []
    if isinstance(chats, list) and len(chats) > 0:
        chat_guid = chats[0].get("guid") or chats[0].get("chatGuid") or ""
    
    # Also try other locations for chat GUID
    if not chat_guid:
        chat_guid = (
            (payload.get("chat") or {}).get("guid") or 
            (payload.get("chat") or {}).get("chatGuid") or 
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
        "is_from_me": False,
        "raw": payload
    }


async def process_webhook_event(event_data: Dict[str, Any]):
    """Process webhook event in background
    
    This is the SINGLE entry point for all incoming BlueBubbles messages.
    Flow: BlueBubbles Server → POST /api/v1/webhooks/bluebubbles → parse → emit event → MessageProcessor
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Parse and structure the message data
        structured_data = parse_bluebubbles_message(event_data)
        
        # Emit event for agent to process
        await event_bus.emit(EventType.MESSAGE_RECEIVED, structured_data)
        logger.debug(f"Emitted MESSAGE_RECEIVED event for {structured_data.get('sender', 'unknown')}")
    except Exception as e:
        logger.error(f"Error processing BlueBubbles webhook event: {e}", exc_info=True)


@router.post("")
async def bluebubbles_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle incoming BlueBubbles webhook
    
    This is the ONLY way messages are received from BlueBubbles.
    Configure this URL in BlueBubbles Server settings: /api/v1/webhooks/bluebubbles
    """
    try:
        # Get webhook payload
        payload = await request.json()
        logger.debug(f"Received webhook payload: {payload.get('type', 'unknown')} event")
        
        # Process in background (non-blocking)
        background_tasks.add_task(process_webhook_event, payload)
        
        # Return success immediately (BlueBubbles expects quick response)
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error handling BlueBubbles webhook: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}, 500

