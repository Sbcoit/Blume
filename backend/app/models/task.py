"""
Task model
"""
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from app.models.base import Base, TimestampMixin


class TaskType(str, enum.Enum):
    """Task types"""
    SCHEDULING = "scheduling"
    RESEARCH = "research"
    DOCUMENT = "document"
    WORKFLOW = "workflow"
    CALL = "call"
    TEXT = "text"


class TaskStatus(str, enum.Enum):
    """Task status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(SQLEnum(TaskType), nullable=False)
    input = Column(Text, nullable=False)  # What user requested
    output = Column(Text, nullable=True)  # What agent did
    status = Column(SQLEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    tast_metadata = Column(JSONB, nullable=True)  # Execution details, timestamps, etc.
    
    # Relationship
    user = relationship("User", backref="tasks")

