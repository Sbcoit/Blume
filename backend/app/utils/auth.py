"""
Authentication utilities
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings
import hashlib
import base64


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    # Hash the plain password first with SHA-256, then verify against bcrypt hash
    # Use digest() to get 32 bytes, then base64 encode to get a safe string (44 chars = 44 bytes)
    password_hash_bytes = hashlib.sha256(plain_password.encode('utf-8')).digest()
    password_hash_str = base64.b64encode(password_hash_bytes).decode('utf-8')
    
    # Use bcrypt directly to verify
    try:
        return bcrypt.checkpw(password_hash_str.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password - first with SHA-256, then bcrypt"""
    # Hash with SHA-256 first to handle passwords longer than 72 bytes
    # Use digest() to get 32 bytes, then base64 encode to get 44 characters (44 bytes)
    password_hash_bytes = hashlib.sha256(password.encode('utf-8')).digest()
    password_hash_str = base64.b64encode(password_hash_bytes).decode('utf-8')
    
    # Use bcrypt directly to hash (with salt automatically generated)
    hashed = bcrypt.hashpw(password_hash_str.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
