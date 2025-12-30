"""
Integration model
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.models.base import Base, TimestampMixin


class IntegrationProvider(str, enum.Enum):
    """Integration providers"""
    GOOGLE_CALENDAR = "google_calendar"
    GOOGLE_DOCS = "google_docs"
    GOOGLE_GMAIL = "google_gmail"
    NOTION = "notion"
    BLUEBUBBLES = "bluebubbles"
    VAPI = "vapi"


class Integration(Base, TimestampMixin):
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String, nullable=False)  # IntegrationProvider enum value as string
    status = Column(String, nullable=False, default="disconnected")  # connected, disconnected, error
    credentials = Column(JSONB, nullable=True)  # Store OAuth credentials as JSON (encrypted in production)
    access_token = Column(String, nullable=True)  # Legacy field, deprecated - use credentials instead
    refresh_token = Column(String, nullable=True)  # Legacy field, deprecated - use credentials instead
    expires_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", backref="integrations")

