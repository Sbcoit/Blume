"""
Task service for managing tasks
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.task import Task, TaskType, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.core.exceptions import NotFoundError


class TaskService:
    """Service for task operations"""
    
    @staticmethod
    def create_task(
        db: Session,
        user_id: UUID,
        task_data: Dict[str, Any]
    ) -> Task:
        """Create a new task"""
        task = Task(
            user_id=user_id,
            type=TaskType(task_data.get("type", "text")),
            input=task_data.get("input", ""),
            status=TaskStatus.PENDING,
            metadata=task_data.get("metadata")
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def get_task(db: Session, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """Get a task by ID"""
        return db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
    
    @staticmethod
    def list_tasks(
        db: Session,
        user_id: UUID,
        task_type: Optional[TaskType] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Task]:
        """List tasks for a user"""
        query = db.query(Task).filter(Task.user_id == user_id)
        
        if task_type:
            query = query.filter(Task.type == task_type)
        if status:
            query = query.filter(Task.status == status)
        
        return query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def update_task(
        db: Session,
        task_id: UUID,
        user_id: UUID,
        output: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Update a task"""
        task = TaskService.get_task(db, task_id, user_id)
        if not task:
            raise NotFoundError("Task not found")
        
        if output is not None:
            task.output = output
        if status is not None:
            task.status = status
        if metadata is not None:
            task.metadata = metadata
        
        db.commit()
        db.refresh(task)
        return task

