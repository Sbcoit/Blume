"""
Voice integration interfaces and implementations
"""
from app.integrations.voice.base_voice import BaseVoiceIntegration, Call
from app.integrations.voice.vapi.service import VapiService

__all__ = ["BaseVoiceIntegration", "Call", "VapiService"]

