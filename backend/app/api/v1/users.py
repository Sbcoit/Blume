"""
User endpoints
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.dependencies import get_database
from app.api.v1.auth import get_current_user_id
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_database)
):
    """Get current user"""
    user = UserService.get_user_by_id(db, UUID(user_id))
    if not user:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("User not found")
    return user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_database)
):
    """Update current user"""
    user = UserService.update_user(db, UUID(user_id), user_data)
    return user

