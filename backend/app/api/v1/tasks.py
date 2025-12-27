"""
Task endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.dependencies import get_database
from app.api.v1.auth import get_current_user_id
from app.services.task_service import TaskService
from app.schemas.task import TaskResponse
from app.models.task import TaskType, TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    task_type: Optional[TaskType] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_database)
):
    """List user tasks"""
    tasks = TaskService.list_tasks(
        db=db,
        user_id=UUID(user_id),
        task_type=task_type,
        status=status,
        limit=limit,
        offset=offset
    )
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_database)
):
    """Get task details"""
    task = TaskService.get_task(db, task_id, UUID(user_id))
    if not task:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Task not found")
    return task

