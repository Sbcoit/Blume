"""
Twilio webhook handler for voice calls
"""
from fastapi import APIRouter, Request, Form, Response
from twilio.twiml.voice_response import VoiceResponse
from twilio.request_validator import RequestValidator
from app.core.config import settings
from app.core.events import event_bus, EventType

router = APIRouter(prefix="/webhooks/twilio", tags=["webhooks"])


@router.post("/voice")
async def twilio_voice_webhook(request: Request):
    """Handle incoming Twilio voice call"""
    # Validate Twilio request (optional but recommended)
    # validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    # if not validator.validate(request.url, request.form, request.headers.get('X-Twilio-Signature')):
    #     return Response(status_code=403)
    
    # Get call data
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From")
    to_number = form_data.get("To")
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Say greeting
    response.say("Hello, this is Blume. How can I help you?", voice="alice")
    
    # Gather speech input
    gather = response.gather(
        input="speech",
        language="en-US",
        timeout=10,
        action=f"/api/v1/webhooks/twilio/process-speech?callSid={call_sid}",
        method="POST"
    )
    
    # If no input, repeat
    response.say("I didn't hear anything. Please try again.", voice="alice")
    response.redirect("/api/v1/webhooks/twilio/voice")
    
    return Response(content=str(response), media_type="application/xml")


@router.post("/process-speech")
async def process_speech(
    request: Request,
    callSid: str = Form(...),
    SpeechResult: str = Form("")
):
    """Process speech input from Twilio"""
    # Emit event for agent to process
    await event_bus.emit(EventType.MESSAGE_RECEIVED, {
        "type": "voice",
        "callSid": callSid,
        "text": SpeechResult,
        "source": "twilio"
    })
    
    # Create response
    response = VoiceResponse()
    
    if SpeechResult:
        response.say(
            "I heard you say: " + SpeechResult + ". Processing your request.",
            voice="alice"
        )
        # In production, you would wait for agent response and say it
        # For now, just acknowledge
        response.say(
            "Your request is being processed. You will receive a response via text message.",
            voice="alice"
        )
    else:
        response.say("I didn't catch that. Please try again.", voice="alice")
        response.redirect("/api/v1/webhooks/twilio/voice")
    
    response.hangup()
    
    return Response(content=str(response), media_type="application/xml")

