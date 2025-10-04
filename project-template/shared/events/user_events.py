"""
User service event schemas following Cursor Rules naming conventions.
Event types follow pattern: user.{entity}.{action}
"""

from typing import List, Optional

from .base import UserEvent


class UserCreatedEvent(UserEvent):
    """
    Event fired when a new user is created/provisioned.
    Topic: user_user_created
    """
    
    def __init__(self, tenant_id: str, user_id: str, email: str, 
                 roles: List[str], business_unit_id: Optional[str] = None,
                 correlation_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="user.user.created",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "user_id": user_id,
                "email": email,
                "roles": roles,
                "business_unit_id": business_unit_id,
                **kwargs
            }
        )


class UserUpdatedEvent(UserEvent):
    """
    Event fired when user information is updated.
    Topic: user_user_updated
    """
    
    def __init__(self, tenant_id: str, user_id: str, 
                 updated_fields: dict, correlation_id: Optional[str] = None,
                 **kwargs):
        super().__init__(
            event_type="user.user.updated",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "user_id": user_id,
                "updated_fields": updated_fields,
                **kwargs
            }
        )


class UserRoleChangedEvent(UserEvent):
    """
    Event fired when user roles are modified.
    Topic: user_user_role_changed
    """
    
    def __init__(self, tenant_id: str, user_id: str, 
                 old_roles: List[str], new_roles: List[str],
                 correlation_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="user.user.role_changed",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "user_id": user_id,
                "old_roles": old_roles,
                "new_roles": new_roles,
                **kwargs
            }
        )


class UserDeactivatedEvent(UserEvent):
    """
    Event fired when a user is deactivated.
    Topic: user_user_deactivated
    """
    
    def __init__(self, tenant_id: str, user_id: str, reason: str,
                 correlation_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="user.user.deactivated",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "user_id": user_id,
                "reason": reason,
                **kwargs
            }
        )


class BusinessUnitCreatedEvent(UserEvent):
    """
    Event fired when a new business unit is created.
    Topic: user_business_unit_created
    """
    
    def __init__(self, tenant_id: str, business_unit_id: str, name: str,
                 parent_id: Optional[str] = None, correlation_id: Optional[str] = None,
                 **kwargs):
        super().__init__(
            event_type="user.business_unit.created",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "business_unit_id": business_unit_id,
                "name": name,
                "parent_id": parent_id,
                **kwargs
            }
        )


class BusinessUnitUpdatedEvent(UserEvent):
    """
    Event fired when business unit information is updated.
    Topic: user_business_unit_updated
    """
    
    def __init__(self, tenant_id: str, business_unit_id: str,
                 updated_fields: dict, correlation_id: Optional[str] = None,
                 **kwargs):
        super().__init__(
            event_type="user.business_unit.updated",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "business_unit_id": business_unit_id,
                "updated_fields": updated_fields,
                **kwargs
            }
        )








