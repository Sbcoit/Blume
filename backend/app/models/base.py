"""
Base model class
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func
from datetime import datetime

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at timestamp"""
    created_at = Column(DateTime, default=func.now(), nullable=False)

