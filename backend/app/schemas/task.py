"""
Task schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.task import TaskType, TaskStatus


class TaskBase(BaseModel):
    type: TaskType
    input: str


class TaskCreate(TaskBase):
    metadata: Optional[Dict[str, Any]] = None


class TaskUpdate(BaseModel):
    output: Optional[str] = None
    status: Optional[TaskStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(TaskBase):
    id: UUID
    user_id: UUID
    output: Optional[str]
    status: TaskStatus
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

