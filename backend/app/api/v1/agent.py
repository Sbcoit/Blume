"""
Agent endpoints
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.dependencies import get_database
from app.api.v1.auth import get_current_user_id
from app.services.agent.agent import AgentService
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID

router = APIRouter(prefix="/agent", tags=["agent"])


class ProcessRequest(BaseModel):
    input: str
    metadata: Optional[Dict[str, Any]] = None


async def process_task_background(
    db: Session,
    user_id: UUID,
    task_id: UUID,
    agent: AgentService
):
    """Background task to process with agent"""
    from app.models.task import TaskStatus
    
    # Get task
    task = TaskService.get_task(db, task_id, user_id)
    if not task:
        return
    
    try:
        # Process with agent
        task_data = {
            "input": task.input,
            "type": task.type.value,
            "metadata": task.metadata
        }
        result = await agent.process_task(task_data)
        
        # Update task
        TaskService.update_task(
            db=db,
            task_id=task_id,
            user_id=user_id,
            output=result.get("output"),
            status=TaskStatus.COMPLETED if result.get("status") == "completed" else TaskStatus.FAILED,
            metadata=result.get("metadata")
        )
    except Exception as e:
        # Update task with error
        TaskService.update_task(
            db=db,
            task_id=task_id,
            user_id=user_id,
            status=TaskStatus.FAILED,
            metadata={"error": str(e)}
        )


@router.post("/process", response_model=TaskResponse)
async def process_request(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_database)
):
    """Process a user request with the agent"""
    from app.models.task import TaskType
    from app.schemas.task import TaskCreate
    
    # Determine task type (simplified - can be enhanced with LLM)
    task_type = TaskType.TEXT  # Default
    
    # Create task
    task_data = TaskCreate(
        type=task_type,
        input=request.input,
        metadata=request.metadata
    )
    
    task = TaskService.create_task(
        db=db,
        user_id=UUID(user_id),
        task_data=task_data.dict()
    )
    
    # Process in background
    agent = AgentService()
    background_tasks.add_task(
        process_task_background,
        db=db,
        user_id=UUID(user_id),
        task_id=task.id,
        agent=agent
    )
    
    return task

