"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.dependencies import get_database
from app.schemas.auth import UserRegister, UserLogin, Token
from app.schemas.user import UserResponse
from app.services.user_service import UserService
from app.utils.auth import create_access_token
from app.core.exceptions import AuthenticationError
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> str:
    """Get current user ID from JWT token"""
    from app.utils.auth import decode_token
    
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise AuthenticationError("Invalid token")
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")
    
    return user_id


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_database)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    from app.schemas.user import UserCreate
    user_create = UserCreate(
        email=user_data.email,
        password=user_data.password
    )
    user = UserService.create_user(db, user_create)
    return user


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_database)
):
    """Login and get access token"""
    user = UserService.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise AuthenticationError("Invalid email or password")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

