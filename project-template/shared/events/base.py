"""
Base event schemas for the Compliance Flow platform.
All events must inherit from BaseEvent to ensure consistency.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """
    Base event schema that all platform events must inherit from.
    
    Follows the naming convention: {service}.{entity}.{action}
    Examples: user.user.created, declaration.declaration.submitted
    """
    
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str = Field(..., description="Event type in format: service.entity.action")
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0", description="Event schema version")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    data: Dict[str, Any] = Field(..., description="Event-specific payload")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    def get_topic_name(self) -> str:
        """Generate Kafka topic name from event type."""
        return self.event_type.replace(".", "_")
    
    def get_routing_key(self) -> str:
        """Generate routing key for message brokers."""
        return self.event_type


class UserEvent(BaseEvent):
    """Base class for all user-related events."""
    
    @property
    def user_id(self) -> str:
        """Extract user_id from event data."""
        return self.data.get("user_id", "")


class DeclarationEvent(BaseEvent):
    """Base class for all declaration-related events."""
    
    @property
    def declaration_id(self) -> str:
        """Extract declaration_id from event data."""
        return self.data.get("declaration_id", "")
    
    @property
    def user_id(self) -> str:
        """Extract user_id from event data."""
        return self.data.get("user_id", "")


class ReviewEvent(BaseEvent):
    """Base class for all review-related events."""
    
    @property
    def review_id(self) -> str:
        """Extract review_id from event data."""
        return self.data.get("review_id", "")
    
    @property
    def declaration_id(self) -> str:
        """Extract declaration_id from event data."""
        return self.data.get("declaration_id", "")


class CaseEvent(BaseEvent):
    """Base class for all case-related events."""
    
    @property
    def case_id(self) -> str:
        """Extract case_id from event data."""
        return self.data.get("case_id", "")
    
    @property
    def declaration_id(self) -> Optional[str]:
        """Extract declaration_id from event data if present."""
        return self.data.get("declaration_id")








