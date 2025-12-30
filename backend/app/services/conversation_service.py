"""
Conversation history service for storing and retrieving message history
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.task import Task, TaskType, TaskStatus
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversation history"""
    
    @staticmethod
    def store_message(
        db: Session,
        user_id: UUID,
        user_message: str,
        agent_response: Optional[str] = None,
        chat_guid: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Store a user message and optionally an agent response"""
        task = Task(
            user_id=user_id,
            type=TaskType.TEXT,  # Use TEXT type for conversation messages
            input=user_message,
            output=agent_response,
            status=TaskStatus.COMPLETED if agent_response else TaskStatus.PENDING,
            tast_metadata={
                "chat_guid": chat_guid,
                "conversation": True,
                **(metadata or {})
            }  # Note: Column is named "tast_metadata" in the model (typo, but keeping for compatibility)
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.debug(f"Stored message for user {user_id}: {user_message[:50]}...")
        return task
    
    @staticmethod
    def get_recent_history(
        db: Session,
        user_id: UUID,
        limit: int = 10,
        chat_guid: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent conversation history for a user
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of message pairs to retrieve
            chat_guid: Optional chat GUID to filter by specific conversation
            
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        query = db.query(Task).filter(
            Task.user_id == user_id,
            Task.type == TaskType.TEXT,
            Task.status == TaskStatus.COMPLETED,
            Task.output.isnot(None)  # Only get messages with responses
        )
        
        # Filter by chat_guid if provided (for multi-conversation support)
        if chat_guid:
            # Note: Column is named "tast_metadata" in the model (typo, but keeping for compatibility)
            query = query.filter(
                Task.tast_metadata['chat_guid'].astext == chat_guid
            )
        
        # Get recent messages, ordered by creation time
        tasks = query.order_by(desc(Task.created_at)).limit(limit).all()
        
        # Convert to conversation format: [user message, assistant response, ...]
        history = []
        for task in reversed(tasks):  # Reverse to get chronological order
            if task.input:
                history.append({
                    "role": "user",
                    "content": task.input
                })
            if task.output:
                history.append({
                    "role": "assistant",
                    "content": task.output
                })
        
        logger.debug(f"Retrieved {len(history)} messages from history for user {user_id}")
        return history
    
    @staticmethod
    def update_agent_response(
        db: Session,
        task_id: UUID,
        agent_response: str
    ) -> Task:
        """Update a task with the agent's response"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.output = agent_response
            task.status = TaskStatus.COMPLETED
            db.commit()
            db.refresh(task)
            logger.debug(f"Updated task {task_id} with agent response")
        return task

