"""
Base schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

