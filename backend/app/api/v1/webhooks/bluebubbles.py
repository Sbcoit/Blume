"""
BlueBubbles webhook handler
"""
from fastapi import APIRouter, Request, BackgroundTasks
from typing import Dict, Any
from app.core.events import event_bus, EventType
from app.integrations.messaging.bluebubbles.service import BlueBubblesService

router = APIRouter(prefix="/webhooks/bluebubbles", tags=["webhooks"])


async def process_webhook_event(event_data: Dict[str, Any]):
    """Process webhook event in background"""
    try:
        # Emit event for agent to process
        await event_bus.emit(EventType.MESSAGE_RECEIVED, event_data)
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

