"""
Agent orchestrator service
"""
from typing import Dict, Any, List, Optional
from app.services.agent.handlers.base_handler import BaseHandler
from app.services.agent.handlers.scheduling_handler import SchedulingHandler
from app.services.agent.handlers.research_handler import ResearchHandler
from app.services.agent.handlers.document_handler import DocumentHandler
from app.services.agent.handlers.workflow_handler import WorkflowHandler
from app.services.agent.handlers.communication_handler import CommunicationHandler
from app.services.agent.handlers.email_handler import EmailHandler
from app.services.agent.llm.base import BaseLLM
from app.services.agent.llm.groq_client import GroqClient
from app.core.events import event_bus, EventType
from app.integrations.messaging.bluebubbles.service import BlueBubblesService
from app.integrations.voice.vapi.service import VapiService


class AgentService:
    """Main agent orchestrator"""
    
    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        bluebubbles_service: Optional[BlueBubblesService] = None,
        vapi_service: Optional[VapiService] = None
    ):
        self.llm = llm or GroqClient()
        self.bluebubbles = bluebubbles_service or BlueBubblesService()
        self.vapi = vapi_service or VapiService()
        
        # Initialize communication handler with services
        communication_handler = CommunicationHandler(
            bluebubbles_service=self.bluebubbles,
            vapi_service=self.vapi
        )
        
        self._handlers: List[BaseHandler] = [
            SchedulingHandler(),  # Scheduling handler FIRST - most specific for calendar/meeting tasks
            communication_handler,  # Communication handler after scheduling
            EmailHandler(),  # Email handler for Gmail
            ResearchHandler(),
            DocumentHandler(),
            WorkflowHandler(),
        ]
    
    def register_handler(self, handler: BaseHandler):
        """Register a new handler"""
        self._handlers.append(handler)
    
    def _find_handler(self, task_data: Dict[str, Any]) -> Optional[BaseHandler]:
        """Find appropriate handler for task"""
        for handler in self._handlers:
            if handler.can_handle(task_data):
                return handler
        return None
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task"""
        # Find appropriate handler
        handler = self._find_handler(task_data)
        if not handler:
            # Default handler - use LLM
            return await self._process_with_llm(task_data)
        
        # Process with handler
        result = await handler.handle(task_data)
        
        # Emit event
        await event_bus.emit(EventType.TASK_COMPLETED, {
            "task_data": task_data,
            "result": result
        })
        
        return result
    
    async def _process_with_llm(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process task with LLM when no specific handler"""
        from app.services.agent.llm.base import LLMMessage
        from app.services.conversation_service import ConversationService
        from app.core.database import SessionLocal
        from uuid import UUID
        
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
        finally:
            db.close()
        
        # Build messages with system prompt, history, and current message
        messages = [
            LLMMessage(
                role="system",
                content=f"You are {agent_name}, a helpful personal assistant. Respond helpfully and concisely. You have access to conversation history to maintain context."
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
                content=task_data.get("input", "")
        ))
        
        try:
            response = await self.llm.chat(messages)
            return {
                "status": "completed",
                "output": response,
                "metadata": {"handler": "llm_default"}
            }
        except Exception as e:
            return {
                "status": "failed",
                "output": f"Error processing task: {str(e)}",
                "metadata": {"error": str(e)}
            }

