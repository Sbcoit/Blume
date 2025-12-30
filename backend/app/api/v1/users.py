"""
User endpoints
"""
import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.dependencies import get_database
from app.api.v1.auth import get_current_user_id
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.models.user import User

logger = logging.getLogger(__name__)

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
    # Get current user to check if phone number is being set for the first time
    current_user = UserService.get_user_by_id(db, UUID(user_id))
    # Send message if: phone number is being explicitly set in the request
    # This will send on first time, when changed, or when explicitly set again
    phone_number_being_set = user_data.phone_number is not None
    is_first_time = current_user is None or not current_user.phone_number
    phone_number_changed = (
        current_user and 
        current_user.phone_number != user_data.phone_number
    )
    # Send message whenever phone number is explicitly provided in request
    should_send_message = phone_number_being_set
    
    # Update user
    user = UserService.update_user(db, UUID(user_id), user_data)
    
    # Send confirmation message if phone number was set/changed
    if should_send_message and user.phone_number:
        try:
            from app.integrations.messaging.bluebubbles.service import BlueBubblesService
            from app.integrations.messaging.base_messaging import Message
            
            agent_name = user.agent_name or "Blume"
            confirmation_message = (
                f"Hi! This is {agent_name}, your personal assistant. "
                f"Your phone number has been successfully configured. "
                f"You can now reach me via iMessage at this number!"
            )
            
            logger.info(f"Preparing to send confirmation message to {user.phone_number}")
            
            bluebubbles = BlueBubblesService()
            message = Message(
                content=confirmation_message,
                recipient=user.phone_number
            )
            
            # Send message asynchronously (don't wait for it to complete)
            # Log errors but don't fail the update
            logger.info(f"Calling bluebubbles.send_message for {user.phone_number}")
            
            send_success = await bluebubbles.send_message(message)
            
            if not send_success:
                logger.warning(f"Failed to send confirmation message to {user.phone_number} - send_message returned False")
            else:
                logger.info(f"Successfully sent confirmation message to {user.phone_number}")
        except Exception as e:
            # Log error but don't fail the user update
            logger.error(f"Exception sending confirmation message to {user.phone_number}: {e}", exc_info=True)
    
    return user

