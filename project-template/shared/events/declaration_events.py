"""
Declaration service event schemas following Cursor Rules naming conventions.
Event types follow pattern: declaration.{entity}.{action}
"""

from typing import Any, Dict, Optional

from .base import DeclarationEvent


class DeclarationCreatedEvent(DeclarationEvent):
    """
    Event fired when a new declaration is created.
    Topic: declaration_declaration_created
    """
    
    def __init__(self, tenant_id: str, declaration_id: str, user_id: str,
                 declaration_type: str, correlation_id: Optional[str] = None,
                 **kwargs):
        super().__init__(
            event_type="declaration.declaration.created",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "declaration_id": declaration_id,
                "user_id": user_id,
                "declaration_type": declaration_type,
                **kwargs
            }
        )


class DeclarationSubmittedEvent(DeclarationEvent):
    """
    Event fired when a declaration is submitted for processing.
    Topic: declaration_declaration_submitted
    """
    
    def __init__(self, tenant_id: str, declaration_id: str, user_id: str,
                 declaration_type: str, form_data: Dict[str, Any],
                 correlation_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="declaration.declaration.submitted",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "declaration_id": declaration_id,
                "user_id": user_id,
                "declaration_type": declaration_type,
                "form_data": form_data,
                **kwargs
            }
        )


class DeclarationApprovedEvent(DeclarationEvent):
    """
    Event fired when a declaration is approved.
    Topic: declaration_declaration_approved
    """
    
    def __init__(self, tenant_id: str, declaration_id: str, user_id: str,
                 approved_by: str, reason: str, auto_decision: bool = False,
                 correlation_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="declaration.declaration.approved",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "declaration_id": declaration_id,
                "user_id": user_id,
                "approved_by": approved_by,
                "reason": reason,
                "auto_decision": auto_decision,
                **kwargs
            }
        )


class DeclarationDeniedEvent(DeclarationEvent):
    """
    Event fired when a declaration is denied.
    Topic: declaration_declaration_denied
    """
    
    def __init__(self, tenant_id: str, declaration_id: str, user_id: str,
                 denied_by: str, reason: str, auto_decision: bool = False,
                 correlation_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="declaration.declaration.denied",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "declaration_id": declaration_id,
                "user_id": user_id,
                "denied_by": denied_by,
                "reason": reason,
                "auto_decision": auto_decision,
                **kwargs
            }
        )


class DeclarationSentToReviewEvent(DeclarationEvent):
    """
    Event fired when a declaration is sent for human review.
    Topic: declaration_declaration_sent_to_review
    """
    
    def __init__(self, tenant_id: str, declaration_id: str, user_id: str,
                 reviewer_groups: list, reason: str,
                 correlation_id: Optional[str] = None, **kwargs):
        super().__init__(
            event_type="declaration.declaration.sent_to_review",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "declaration_id": declaration_id,
                "user_id": user_id,
                "reviewer_groups": reviewer_groups,
                "reason": reason,
                **kwargs
            }
        )


class DeclarationStatusChangedEvent(DeclarationEvent):
    """
    Event fired when declaration status changes.
    Topic: declaration_declaration_status_changed
    """
    
    def __init__(self, tenant_id: str, declaration_id: str, user_id: str,
                 old_status: str, new_status: str, changed_by: str,
                 reason: Optional[str] = None, correlation_id: Optional[str] = None,
                 **kwargs):
        super().__init__(
            event_type="declaration.declaration.status_changed",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "declaration_id": declaration_id,
                "user_id": user_id,
                "old_status": old_status,
                "new_status": new_status,
                "changed_by": changed_by,
                "reason": reason,
                **kwargs
            }
        )


class DeclarationRuleEvaluatedEvent(DeclarationEvent):
    """
    Event fired when declaration is evaluated by rule engine.
    Topic: declaration_declaration_rule_evaluated
    """
    
    def __init__(self, tenant_id: str, declaration_id: str, user_id: str,
                 decision: str, reason: str, rules_applied: list,
                 execution_time_ms: int, correlation_id: Optional[str] = None,
                 **kwargs):
        super().__init__(
            event_type="declaration.declaration.rule_evaluated",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            data={
                "declaration_id": declaration_id,
                "user_id": user_id,
                "decision": decision,
                "reason": reason,
                "rules_applied": rules_applied,
                "execution_time_ms": execution_time_ms,
                **kwargs
            }
        )



