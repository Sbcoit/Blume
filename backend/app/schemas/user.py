"""
User schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    phone_number: Optional[str] = None
    agent_name: Optional[str] = None
    timezone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    agent_name: Optional[str] = None
    timezone: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

