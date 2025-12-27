"""
User service
"""
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.auth import get_password_hash, verify_password
from app.core.exceptions import NotFoundError


class UserService:
    """Service for user operations"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            phone_number=user_data.phone_number,
            agent_name=user_data.agent_name
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
        if user_data.agent_name is not None:
            user.agent_name = user_data.agent_name
        
        db.commit()
        db.refresh(user)
        return user

