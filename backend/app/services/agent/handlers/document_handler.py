"""
Document handler for agent tasks
"""
from typing import Dict, Any
from app.services.agent.handlers.base_handler import BaseHandler
from app.integrations.documents.google_docs.service import GoogleDocsService
from app.integrations.documents.base_documents import Document


class DocumentHandler(BaseHandler):
    """Handler for document processing tasks"""
    
    @property
    def task_type(self) -> str:
        return "document"
    
    def can_handle(self, task_data: Dict[str, Any]) -> bool:
        """Check if this handler can handle the task"""
        task_input = task_data.get("input", "").lower()
        document_keywords = [
            "document", "pdf", "file", "read", "analyze", 
            "summarize", "extract", "parse", "notion", "note", "notes",
            "page", "pages", "update", "create", "delete"
        ]
        return any(keyword in task_input for keyword in document_keywords)
    
    async def handle(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a document processing task"""
        from app.services.integration_service import IntegrationService
        from app.services.conversation_service import ConversationService
        from app.services.agent.llm.groq_client import GroqClient
        from app.services.agent.llm.base import LLMMessage, FunctionDefinition
        from app.integrations.documents.google_docs.service import GoogleDocsService
        from app.integrations.documents.base_documents import Document
        from app.models.integration import Integration, IntegrationProvider
        from app.core.database import SessionLocal
        from uuid import UUID
        import logging
        import json
        
        logger = logging.getLogger(__name__)
        
        user_id = UUID(task_data.get("user_id"))
        db = SessionLocal()
        
        try:
            task_input = task_data.get("input", "").lower()
            
            # Check for Google Docs if task mentions Google Docs
            if "google" in task_input or "docs" in task_input or "document" in task_input:
                if not IntegrationService.is_integration_connected(db, user_id, "google"):
                    return {
                        "status": "completed",
                        "output": "You haven't set up Google Docs yet. Please connect your Google Account in Settings.",
                        "metadata": {"handler": "document_handler", "missing_integration": "google"}
                    }
                
                # Get Google Docs credentials
                docs_integration = db.query(Integration).filter(
                    Integration.user_id == user_id,
                    Integration.provider == IntegrationProvider.GOOGLE_DOCS.value,
                    Integration.status == "connected"
                ).first()
                
                if not docs_integration or not docs_integration.credentials:
                    return {
                        "status": "completed",
                        "output": "Google Docs credentials not found. Please reconnect your Google Account in Settings.",
                        "metadata": {"handler": "document_handler", "missing_integration": "google"}
                    }
                
                # Initialize docs service
                docs_service = GoogleDocsService()
                await docs_service.connect(docs_integration.credentials)
                
                # Get conversation history
                chat_guid = task_data.get("metadata", {}).get("chat_guid")
                agent_name = task_data.get("metadata", {}).get("agent_name", "Blume")
                
                history = ConversationService.get_recent_history(
                    db=db,
                    user_id=user_id,
                    limit=10,
                    chat_guid=chat_guid
                )
                
                # Use LLM to parse document request
                llm = GroqClient()
                input_text = task_data.get("input", "")
                
                functions = [
                    FunctionDefinition(
                        name="execute_document_action",
                        description="Perform document operations: create (create new document), get (read a document by ID or search), list (list all documents), update (update existing document)",
                        parameters={
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "enum": ["create", "get", "list", "update"],
                                    "description": "Action to perform: 'create' (create new document), 'get' (read document by ID or search), 'list' (list all documents), 'update' (update existing document)"
                                },
                                "parameters": {
                                    "type": "object",
                                    "description": "Action-specific parameters. For 'create': {title (required), content (required)}. For 'get': {document_id (optional string), search_query (optional string)}. For 'list': {} (no parameters). For 'update': {document_id (required string), content (required string)}."
                                }
                            },
                            "required": ["action", "parameters"]
                        }
                    )
                ]
                
                # Build messages
                messages = [
                    LLMMessage(
                        role="system",
                        content=f"You are {agent_name}, a helpful personal assistant. When the user wants to create, read, update, or list Google Docs, use the appropriate function. You have access to conversation history to maintain context."
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
                        
                        if function_name == "execute_document_action":
                            return await self._handle_document_action(arguments, docs_service)
                        else:
                            return {
                                "status": "failed",
                                "output": f"Unknown function: {function_name}",
                                "metadata": {"handler": "document_handler"}
                            }
                    else:
                        # LLM responded with text
                        return {
                            "status": "completed",
                            "output": result,
                            "metadata": {"handler": "document_handler", "action": "text_response"}
                        }
                except Exception as e:
                    logger.error(f"Error processing document task: {e}", exc_info=True)
                    return {
                        "status": "failed",
                        "output": f"Error processing document request: {str(e)}",
                        "metadata": {"error": str(e), "handler": "document_handler"}
                    }
            
            # Check for Notion if task mentions Notion explicitly
            if "notion" in task_input:
                logger.debug(f"Checking Notion integration for user {user_id}")
                is_connected = IntegrationService.is_integration_connected(db, user_id, "notion")
                logger.debug(f"Notion integration connected: {is_connected}")
                if not is_connected:
                    return {
                        "status": "completed",
                        "output": "You haven't set up Notion yet. Please connect Notion in Settings.",
                        "metadata": {"handler": "document_handler", "missing_integration": "notion"}
                    }
                # Notion implementation pending
                return {
                    "status": "completed",
                    "output": "Notion integration is not yet fully implemented.",
                    "metadata": {"handler": "document_handler"}
                }
            
            # Default response
            return {
                "status": "completed",
                "output": "I can help you with Google Docs. Try saying 'create a document' or 'list my documents'.",
                "metadata": {"handler": "document_handler"}
            }
        finally:
            db.close()
    
    async def _handle_document_action(self, arguments: Dict[str, Any], docs_service: GoogleDocsService) -> Dict[str, Any]:
        """Handle execute_document_action function call"""
        action = arguments.get("action")
        params = arguments.get("parameters", {})
        
        if action == "create":
            return await self._handle_create_document(params, docs_service)
        elif action == "get":
            return await self._handle_get_document(params, docs_service)
        elif action == "list":
            return await self._handle_list_documents(docs_service)
        elif action == "update":
            return await self._handle_update_document(params, docs_service)
        else:
            return {
                "status": "failed",
                "output": f"Unknown document action: {action}. Valid actions are: create, get, list, update",
                "metadata": {"handler": "document_handler"}
            }
    
    async def _handle_create_document(self, params: Dict[str, Any], docs_service: GoogleDocsService) -> Dict[str, Any]:
        """Handle create document action"""
        try:
            title = params.get("title")
            content = params.get("content")
            
            if not title or not content:
                return {
                    "status": "failed",
                    "output": "Missing required fields: title and content are required",
                    "metadata": {"handler": "document_handler"}
                }
            
            document = Document(title=title, content=content)
            doc_id = await docs_service.create_document(document)
            
            return {
                "status": "completed",
                "output": f"Successfully created document '{title}'. Document ID: {doc_id}",
                "metadata": {
                    "handler": "document_handler",
                    "action": "create",
                    "document_id": doc_id
                }
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating document: {e}", exc_info=True)
            return {
                "status": "failed",
                "output": f"Error creating document: {str(e)}",
                "metadata": {"error": str(e), "handler": "document_handler"}
            }
    
    async def _handle_get_document(self, params: Dict[str, Any], docs_service: GoogleDocsService) -> Dict[str, Any]:
        """Handle get document action"""
        try:
            document_id = params.get("document_id")
            search_query = params.get("search_query")
            
            if not document_id and not search_query:
                return {
                    "status": "failed",
                    "output": "Please provide either a document_id or search_query",
                    "metadata": {"handler": "document_handler"}
                }
            
            # If search query, list documents and find match
            if search_query and not document_id:
                documents = await docs_service.list_documents()
                # Find document by name match
                for doc in documents:
                    if search_query.lower() in doc.get('title', '').lower():
                        document_id = doc.get('id')
                        break
                
                if not document_id:
                    return {
                        "status": "completed",
                        "output": f"Could not find a document matching '{search_query}'",
                        "metadata": {"handler": "document_handler"}
                    }
            
            document = await docs_service.get_document(document_id)
            
            return {
                "status": "completed",
                "output": f"Document: {document.title}\n\n{document.content[:500]}{'...' if len(document.content) > 500 else ''}",
                "metadata": {
                    "handler": "document_handler",
                    "action": "get",
                    "document_id": document_id
                }
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting document: {e}", exc_info=True)
            return {
                "status": "failed",
                "output": f"Error getting document: {str(e)}",
                "metadata": {"error": str(e), "handler": "document_handler"}
            }
    
    async def _handle_list_documents(self, docs_service: GoogleDocsService) -> Dict[str, Any]:
        """Handle list documents action"""
        try:
            documents = await docs_service.list_documents()
            
            if not documents:
                return {
                    "status": "completed",
                    "output": "You don't have any Google Docs yet.",
                    "metadata": {"handler": "document_handler", "action": "list_documents"}
                }
            
            doc_list = "\n".join([f"- {doc.get('title', 'Untitled')} (ID: {doc.get('id', 'N/A')})" for doc in documents[:10]])
            
            return {
                "status": "completed",
                "output": f"Your Google Docs:\n{doc_list}" + (f"\n... and {len(documents) - 10} more" if len(documents) > 10 else ""),
                "metadata": {
                    "handler": "document_handler",
                    "action": "list",
                    "count": len(documents)
                }
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error listing documents: {e}", exc_info=True)
            return {
                "status": "failed",
                "output": f"Error listing documents: {str(e)}",
                "metadata": {"error": str(e), "handler": "document_handler"}
            }
    
    async def _handle_update_document(self, params: Dict[str, Any], docs_service: GoogleDocsService) -> Dict[str, Any]:
        """Handle update document action"""
        try:
            document_id = params.get("document_id")
            content = params.get("content")
            
            if not document_id or not content:
                return {
                    "status": "failed",
                    "output": "Missing required fields: document_id and content are required",
            "metadata": {"handler": "document_handler"}
                }
            
            # Get existing document to preserve title
            existing_doc = await docs_service.get_document(document_id)
            document = Document(title=existing_doc.title, content=content, document_id=document_id)
            
            success = await docs_service.update_document(document_id, document)
            
            if success:
                return {
                    "status": "completed",
                    "output": f"Successfully updated document '{existing_doc.title}'",
                    "metadata": {
                        "handler": "document_handler",
                        "action": "update",
                        "document_id": document_id
                    }
                }
            else:
                return {
                    "status": "failed",
                    "output": "Failed to update document",
                    "metadata": {"handler": "document_handler"}
                }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating document: {e}", exc_info=True)
            return {
                "status": "failed",
                "output": f"Error updating document: {str(e)}",
                "metadata": {"error": str(e), "handler": "document_handler"}
        }

