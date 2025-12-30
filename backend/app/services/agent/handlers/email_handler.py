"""
Email handler for agent tasks
"""
from typing import Dict, Any
from app.services.agent.handlers.base_handler import BaseHandler
from app.services.agent.llm.base import LLMMessage, FunctionDefinition
from app.integrations.email.base_email import Email
from app.integrations.email.gmail.service import GmailService
import json
import logging

logger = logging.getLogger(__name__)


class EmailHandler(BaseHandler):
    """Handler for email tasks"""
    
    @property
    def task_type(self) -> str:
        return "email"
    
    def can_handle(self, task_data: Dict[str, Any]) -> bool:
        """Check if this handler can handle the task"""
        task_input = task_data.get("input", "").lower()
        email_keywords = [
            "email", "send email", "draft email", "compose email", "write email",
            "mail", "send mail", "gmail", "inbox", "check email", "read email"
        ]
        return any(keyword in task_input for keyword in email_keywords)
    
    async def handle(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an email task"""
        from app.services.integration_service import IntegrationService
        from app.services.conversation_service import ConversationService
        from app.services.agent.llm.groq_client import GroqClient
        from app.models.integration import Integration, IntegrationProvider
        from app.core.database import SessionLocal
        from uuid import UUID
        
        user_id = UUID(task_data.get("user_id"))
        db = SessionLocal()
        
        try:
            # Check if Gmail is connected
            if not IntegrationService.is_integration_connected(db, user_id, "google"):
                return {
                    "status": "completed",
                    "output": "You haven't set up Gmail yet. Please connect your Google Account in Settings to use email features.",
                    "metadata": {"handler": "email_handler", "missing_integration": "google"}
                }
            
            # Get Gmail credentials
            gmail_integration = db.query(Integration).filter(
                Integration.user_id == user_id,
                Integration.provider == IntegrationProvider.GOOGLE_GMAIL.value,
                Integration.status == "connected"
            ).first()
            
            if not gmail_integration or not gmail_integration.credentials:
                return {
                    "status": "completed",
                    "output": "Gmail credentials not found. Please reconnect your Google Account in Settings.",
                    "metadata": {"handler": "email_handler", "missing_integration": "google"}
                }
            
            # Get conversation history
            chat_guid = task_data.get("metadata", {}).get("chat_guid")
            agent_name = task_data.get("metadata", {}).get("agent_name", "Blume")
            
            history = ConversationService.get_recent_history(
                db=db,
                user_id=user_id,
                limit=10,
                chat_guid=chat_guid
            )
            
            # Initialize Gmail service
            gmail_service = GmailService()
            await gmail_service.connect(gmail_integration.credentials)
            
            # Use LLM to parse email request
            llm = GroqClient()
            input_text = task_data.get("input", "")
            
            functions = [
                FunctionDefinition(
                    name="execute_email_action",
                    description="Perform email operations: send (send immediately), draft (save as draft), list (list emails from inbox), get (read a specific email by ID)",
                    parameters={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["send", "draft", "list", "get"],
                                "description": "Action to perform: 'send' (send email immediately), 'draft' (save as draft), 'list' (list recent emails), 'get' (read specific email)"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Action-specific parameters. For 'send'/'draft': {to (required), subject (required), body (required), cc (optional array)}. For 'list': {query (optional string), max_results (optional integer, default 10)}. For 'get': {email_id (required string)}"
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
                    content=f"You are {agent_name}, a helpful personal assistant. When the user wants to send, draft, read, or list emails, use the appropriate function. Extract the recipient, subject, and body from the user's request. You have access to conversation history to maintain context."
                )
            ]
            
            # Add conversation history
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
                    
                    if function_name == "execute_email_action":
                        return await self._handle_email_action(arguments, gmail_service)
                    else:
                        return {
                            "status": "failed",
                            "output": f"Unknown function: {function_name}",
                            "metadata": {"handler": "email_handler"}
                        }
                else:
                    # LLM responded with text (no function call)
                    return {
                        "status": "completed",
                        "output": result,
                        "metadata": {"handler": "email_handler", "action": "text_response"}
                    }
            except Exception as e:
                logger.error(f"Error processing email task: {e}", exc_info=True)
                return {
                    "status": "failed",
                    "output": f"Error processing email request: {str(e)}",
                    "metadata": {"error": str(e), "handler": "email_handler"}
                }
        finally:
            db.close()
    
    async def _handle_email_action(self, arguments: Dict[str, Any], gmail_service: GmailService) -> Dict[str, Any]:
        """Handle execute_email_action function call"""
        action = arguments.get("action")
        params = arguments.get("parameters", {})
        
        if action == "send":
            return await self._handle_send_email(params, gmail_service)
        elif action == "draft":
            return await self._handle_draft_email(params, gmail_service)
        elif action == "list":
            return await self._handle_list_emails(params, gmail_service)
        elif action == "get":
            return await self._handle_get_email(params, gmail_service)
        else:
            return {
                "status": "failed",
                "output": f"Unknown email action: {action}. Valid actions are: send, draft, list, get",
                "metadata": {"handler": "email_handler"}
            }
    
    async def _handle_send_email(self, params: Dict[str, Any], gmail_service: GmailService) -> Dict[str, Any]:
        """Handle send email action"""
        try:
            to = params.get("to")
            subject = params.get("subject")
            body = params.get("body")
            cc = params.get("cc", [])
            
            if not to or not subject or not body:
                return {
                    "status": "failed",
                    "output": "Missing required fields: to, subject, and body are required",
                    "metadata": {"handler": "email_handler"}
                }
            
            email = Email(to=to, subject=subject, body=body, cc=cc)
            success = await gmail_service.send_email(email)
            
            if success:
                return {
                    "status": "completed",
                    "output": f"Email sent successfully to {to} with subject: {subject}",
                    "metadata": {
                        "handler": "email_handler",
                        "action": "send",
                        "recipient": to
                    }
                }
            else:
                return {
                    "status": "failed",
                    "output": f"Failed to send email to {to}",
                    "metadata": {"handler": "email_handler"}
                }
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return {
                "status": "failed",
                "output": f"Error sending email: {str(e)}",
                "metadata": {"error": str(e), "handler": "email_handler"}
            }
    
    async def _handle_draft_email(self, params: Dict[str, Any], gmail_service: GmailService) -> Dict[str, Any]:
        """Handle draft email action"""
        try:
            to = params.get("to")
            subject = params.get("subject")
            body = params.get("body")
            cc = params.get("cc", [])
            
            if not to or not subject or not body:
                return {
                    "status": "failed",
                    "output": "Missing required fields: to, subject, and body are required",
                    "metadata": {"handler": "email_handler"}
                }
            
            email = Email(to=to, subject=subject, body=body, cc=cc)
            draft_id = await gmail_service.draft_email(email)
            
            return {
                "status": "completed",
                "output": f"Draft email created for {to} with subject: {subject}. Draft ID: {draft_id}",
                "metadata": {
                    "handler": "email_handler",
                    "action": "draft",
                    "draft_id": draft_id
                }
            }
        except Exception as e:
            logger.error(f"Error creating draft email: {e}", exc_info=True)
            return {
                "status": "failed",
                "output": f"Error creating draft email: {str(e)}",
                "metadata": {"error": str(e), "handler": "email_handler"}
            }
    
    async def _handle_list_emails(self, params: Dict[str, Any], gmail_service: GmailService) -> Dict[str, Any]:
        """Handle list emails action"""
        try:
            query = params.get("query")
            max_results = params.get("max_results", 10)
            
            emails = await gmail_service.list_emails(query=query, max_results=max_results)
            
            if not emails:
                return {
                    "status": "completed",
                    "output": "No emails found.",
                    "metadata": {"handler": "email_handler", "action": "list"}
                }
            
            email_list = "\n".join([
                f"- From: {email.get('from', 'Unknown')}, Subject: {email.get('subject', 'No Subject')} (ID: {email.get('id', 'N/A')})"
                for email in emails
            ])
            
            return {
                "status": "completed",
                "output": f"Recent emails:\n{email_list}",
                "metadata": {
                    "handler": "email_handler",
                    "action": "list",
                    "count": len(emails)
                }
            }
        except Exception as e:
            logger.error(f"Error listing emails: {e}", exc_info=True)
            return {
                "status": "failed",
                "output": f"Error listing emails: {str(e)}",
                "metadata": {"error": str(e), "handler": "email_handler"}
            }
    
    async def _handle_get_email(self, params: Dict[str, Any], gmail_service: GmailService) -> Dict[str, Any]:
        """Handle get email action"""
        try:
            email_id = params.get("email_id")
            
            if not email_id:
                return {
                    "status": "failed",
                    "output": "Missing required field: email_id",
                    "metadata": {"handler": "email_handler"}
                }
            
            email = await gmail_service.get_email(email_id)
            
            return {
                "status": "completed",
                "output": f"Email from {email.to}:\nSubject: {email.subject}\n\n{email.body[:500]}{'...' if len(email.body) > 500 else ''}",
                "metadata": {
                    "handler": "email_handler",
                    "action": "get",
                    "email_id": email_id
                }
            }
        except Exception as e:
            logger.error(f"Error getting email: {e}", exc_info=True)
            return {
                "status": "failed",
                "output": f"Error getting email: {str(e)}",
                "metadata": {"error": str(e), "handler": "email_handler"}
            }

