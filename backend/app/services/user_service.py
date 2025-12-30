"""
User service
"""
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.auth import get_password_hash, verify_password
from app.utils.timezone import detect_timezone_from_phone
from app.core.exceptions import NotFoundError


class UserService:
    """Service for user operations"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        
        # Auto-detect timezone from phone number if provided
        detected_timezone = None
        if user_data.phone_number:
            try:
                detected_timezone = detect_timezone_from_phone(user_data.phone_number)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not detect timezone from phone number {user_data.phone_number}: {e}")
                # If detection fails, use explicit timezone or None (will use DB default)
        
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            phone_number=user_data.phone_number,
            agent_name=user_data.agent_name,
            timezone=user_data.timezone or detected_timezone
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_phone_number(db: Session, phone_number: str) -> Optional[User]:
        """Get user by phone number (normalized comparison)"""
        if not phone_number:
            return None
        
        # Normalize phone number for comparison (remove +, spaces, dashes, etc.)
        normalized = phone_number.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        
        # Get all users with phone numbers and compare normalized versions
        users = db.query(User).filter(User.phone_number.isnot(None)).all()
        for user in users:
            if not user.phone_number:
                continue
            user_normalized = user.phone_number.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
            if user_normalized == normalized:
                return user
        
        return None
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> User:
        """Update user information"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundError("User not found")
        
        if user_data.phone_number is not None:
            user.phone_number = user_data.phone_number
            # Auto-detect timezone when phone number is set/changed
            if not user_data.timezone:  # Only auto-detect if timezone not explicitly set
                try:
                    user.timezone = detect_timezone_from_phone(user_data.phone_number)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Could not detect timezone from phone number {user_data.phone_number}: {e}")
                    # If detection fails, keep existing timezone or leave as None
        
        # Set agent_name: use provided value, or default to "Blume" if not set and phone_number is being set
        if user_data.agent_name is not None:
            user.agent_name = user_data.agent_name
        elif user_data.phone_number is not None and not user.agent_name:
            # If phone number is being set but agent_name is not provided and user doesn't have one, default to "Blume"
            user.agent_name = "Blume"
        
        # Allow explicit timezone override
        if user_data.timezone is not None:
            user.timezone = user_data.timezone
        
        db.commit()
        db.refresh(user)
        return user

