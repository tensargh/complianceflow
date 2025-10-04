# Review Service PRD
## Compliance Flow Platform

### Service Information
- **Service Name**: Review Service
- **Version**: 1.0
- **Date**: December 2024
- **Domain**: Review Workflow Management

---

## 1. Service Overview

### 1.1 Purpose
The Review Service manages the human review workflow for declarations that require manual evaluation. It handles reviewer group assignment, parallel review coordination, escalation, and break-glass processes.

### 1.2 Responsibilities
- **Review Assignment**: Assign declarations to appropriate reviewer groups
- **Reviewer Groups**: Manage reviewer group membership and configuration
- **Review Coordination**: Handle parallel review processes
- **Escalation Management**: Track aged reviews and escalations
- **Break-Glass Process**: Emergency override capabilities for compliance officers

### 1.3 Service Boundaries
- **Owns**: Reviews, Reviewer Groups, Review Assignments
- **Reads From**: Declaration Service (declaration data), User Service (reviewer information)
- **Writes To**: Review events (Kafka)
- **Coordinates With**: Case Service (for escalated reviews)

---

## 2. Core Entities

### 2.1 Reviewer Group
```json
{
  "group_id": "UUID",
  "tenant_id": "UUID",
  "name": "string",
  "description": "string",
  "business_units": ["UUID"],
  "declaration_types": ["personal_trade", "gift_received"],
  "ranking": "integer",
  "is_fallback": "boolean",
  "members": ["UUID"],
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 2.2 Review
```json
{
  "review_id": "UUID",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "reviewer_group_id": "UUID",
  "assigned_at": "timestamp",
  "reviewer_id": "UUID",
  "status": "pending|in_progress|completed|escalated",
  "decision": "approve|deny|request_info",
  "reason": "string",
  "notes": "string",
  "completed_at": "timestamp",
  "escalated_at": "timestamp",
  "escalation_reason": "string"
}
```

### 2.3 Review Assignment
```json
{
  "assignment_id": "UUID",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "reviewer_groups": ["UUID"],
  "assignment_type": "parallel|sequential",
  "status": "pending|in_progress|completed",
  "created_at": "timestamp",
  "completed_at": "timestamp"
}
```

### 2.4 Break-Glass Action
```json
{
  "action_id": "UUID",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "compliance_officer_id": "UUID",
  "original_status": "string",
  "override_decision": "approve|deny",
  "reason": "string",
  "timestamp": "timestamp"
}
```

---

## 3. API Specifications

### 3.1 Review Assignment APIs

#### POST /assignments
```json
{
  "declaration_id": "UUID",
  "declaration_type": "personal_trade",
  "user_business_unit": "UUID",
  "assignment_type": "parallel"
}
```
Response: Created review assignment

#### GET /assignments/{assignment_id}
Response: Assignment details with reviews

#### GET /assignments?declaration_id={declaration_id}
Response: All assignments for declaration

### 3.2 Review Management APIs

#### GET /reviews/queue?reviewer_id={reviewer_id}
Response: Pending reviews for reviewer (sorted by age)

#### GET /reviews/{review_id}
Response: Review details

#### PUT /reviews/{review_id}/claim
```json
{
  "reviewer_id": "UUID"
}
```
Claim review for processing

#### PUT /reviews/{review_id}/complete
```json
{
  "decision": "approve",
  "reason": "Trade is within policy limits",
  "notes": "Verified against recent similar trades"
}
```

#### POST /reviews/{review_id}/escalate
```json
{
  "reason": "Suspicious pattern detected",
  "escalation_type": "compliance_review"
}
```

#### POST /reviews/{review_id}/request-info
```json
{
  "information_requested": "Please provide additional documentation for this trade",
  "due_date": "2024-01-20T10:00:00Z"
}
```

### 3.3 Reviewer Group APIs

#### GET /reviewer-groups?tenant_id={tenant_id}
Response: List of reviewer groups

#### POST /reviewer-groups
```json
{
  "tenant_id": "UUID",
  "name": "Trading Desk Reviewers",
  "description": "Reviews for trading desk declarations",
  "business_units": ["UUID"],
  "declaration_types": ["personal_trade"],
  "ranking": 100,
  "members": ["UUID", "UUID"]
}
```

#### PUT /reviewer-groups/{group_id}
Update reviewer group

#### POST /reviewer-groups/{group_id}/members
```json
{
  "user_ids": ["UUID", "UUID"]
}
```

#### DELETE /reviewer-groups/{group_id}/members/{user_id}
Remove member from group

### 3.4 Break-Glass APIs

#### POST /break-glass
```json
{
  "declaration_id": "UUID",
  "override_decision": "approve",
  "reason": "Emergency approval required for compliance deadline"
}
```
Response: Break-glass action record

#### GET /break-glass?tenant_id={tenant_id}&date_from={date}
Response: Break-glass audit trail

---

## 4. Business Logic

### 4.1 Reviewer Group Selection
```python
def select_reviewer_groups(declaration_type, user_business_unit, tenant_id):
    # Get all groups for declaration type
    groups = get_groups_by_type(declaration_type, tenant_id)
    
    # Filter by business unit
    matching_groups = [
        g for g in groups 
        if user_business_unit in g.business_units or g.is_fallback
    ]
    
    # Sort by ranking (highest first)
    matching_groups.sort(key=lambda g: g.ranking, reverse=True)
    
    # Return highest ranking non-fallback group, or fallback if none
    non_fallback = [g for g in matching_groups if not g.is_fallback]
    if non_fallback:
        return [non_fallback[0]]  # For now, single group assignment
    else:
        fallback = [g for g in matching_groups if g.is_fallback]
        return fallback[:1]  # Return fallback group
```

### 4.2 Review Status Transitions
```python
ALLOWED_TRANSITIONS = {
    "pending": ["in_progress", "escalated"],
    "in_progress": ["completed", "escalated"],
    "completed": [],  # Terminal state
    "escalated": []   # Terminal state
}

def validate_transition(current_status, new_status):
    return new_status in ALLOWED_TRANSITIONS.get(current_status, [])
```

### 4.3 Parallel Review Logic
```python
def check_parallel_completion(assignment_id):
    assignment = get_assignment(assignment_id)
    reviews = get_reviews_by_assignment(assignment_id)
    
    completed_reviews = [r for r in reviews if r.status == "completed"]
    
    if assignment.assignment_type == "parallel":
        # All groups must complete for parallel reviews
        if len(completed_reviews) == len(reviews):
            return finalize_parallel_decision(completed_reviews)
    
    return None  # Not yet complete

def finalize_parallel_decision(reviews):
    # Apply decision hierarchy: deny > review > approve
    decisions = [r.decision for r in reviews]
    
    if "deny" in decisions:
        return "deny"
    elif "request_info" in decisions:
        return "request_info"
    else:
        return "approve"
```

### 4.4 Age Tracking and Prioritization
```python
def get_aged_reviews(tenant_id, reviewer_id=None):
    query = """
    SELECT r.*, 
           EXTRACT(EPOCH FROM (NOW() - r.assigned_at)) / 3600 as age_hours
    FROM reviews r
    WHERE r.tenant_id = %s 
    AND r.status IN ('pending', 'in_progress')
    """
    
    if reviewer_id:
        query += " AND %s = ANY(rg.members)"
        
    query += " ORDER BY age_hours DESC"
    
    return execute_query(query, [tenant_id, reviewer_id])
```

---

## 5. Events Published

### 5.1 Review Assignment Events
```json
{
  "event_type": "review.assigned",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "reviewer_groups": ["UUID"],
  "assignment_type": "parallel",
  "timestamp": "ISO8601"
}
```

### 5.2 Review Lifecycle Events
```json
{
  "event_type": "review.completed",
  "review_id": "UUID",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "reviewer_id": "UUID",
  "decision": "approve",
  "reason": "string",
  "timestamp": "ISO8601"
}
```

```json
{
  "event_type": "review.escalated",
  "review_id": "UUID",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "escalation_reason": "string",
  "escalated_by": "UUID",
  "timestamp": "ISO8601"
}
```

### 5.3 Break-Glass Events
```json
{
  "event_type": "review.break_glass",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "compliance_officer_id": "UUID",
  "override_decision": "approve",
  "reason": "string",
  "timestamp": "ISO8601"
}
```

---

## 6. External Dependencies

### 6.1 Service Dependencies
- **Declaration Service**: Declaration data and status updates
- **User Service**: Reviewer information and business unit data
- **Case Service**: Case creation for escalated reviews

### 6.2 Event Subscriptions
- **Declaration Events**: declaration.sent_to_review (trigger assignment)
- **User Events**: user.role_changed (update reviewer group membership)

---

## 7. Data Storage

### 7.1 Database Schema
- **Primary Database**: PostgreSQL
- **Multi-tenancy**: Row-level security with tenant_id
- **Indexing**: Indexes on reviewer_id, status, assigned_at for queue queries
- **Audit Trail**: Immutable review history records

### 7.2 Performance Requirements
- **Review Queue**: < 200ms for reviewer queue retrieval
- **Assignment**: < 500ms for reviewer group selection and assignment
- **Status Updates**: < 100ms for review status changes
- **Aged Reviews**: < 1s for aged review reports

---

## 8. Security Requirements

### 8.1 Access Control
- **Reviewer Access**: Users can only access reviews for groups they belong to
- **Compliance Access**: Compliance officers have full access within tenant
- **Break-Glass**: Special audit trail for emergency overrides
- **Tenant Isolation**: Strict tenant data separation

### 8.2 Audit Requirements
- **Review Actions**: Complete audit trail of all review decisions
- **Group Changes**: Log all reviewer group membership changes
- **Break-Glass**: Enhanced audit for emergency overrides

---

## 9. Implementation Notes

### 9.1 Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy
- **Caching**: Redis for reviewer queue optimization
- **Background Tasks**: Celery for aged review monitoring

### 9.2 Notification Integration
- **Review Assignments**: Trigger notifications when reviews are assigned
- **Aged Reviews**: Daily notifications for overdue reviews
- **Escalations**: Immediate notifications for escalated reviews

### 9.3 Performance Optimization
- **Queue Caching**: Cache reviewer queues for fast access
- **Batch Operations**: Batch reviewer group updates
- **Connection Pooling**: Database connection pooling for high concurrency

---

## 10. Testing Strategy

### 10.1 Unit Tests
- Reviewer group selection logic
- Parallel review decision aggregation
- Status transition validation
- Age calculation and prioritization

### 10.2 Integration Tests
- Review assignment workflow
- Break-glass process
- Event publishing and subscription
- Cross-service communication

### 10.3 Performance Tests
- Concurrent review processing
- Large reviewer queue handling
- High-volume assignment processing
