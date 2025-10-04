# Case Service PRD
## Compliance Flow Platform

### Service Information
- **Service Name**: Case Service
- **Version**: 1.0
- **Date**: December 2024
- **Domain**: Investigation Management

---

## 1. Service Overview

### 1.1 Purpose
The Case Service manages compliance investigation cases, including silent cases created by rules and escalated cases from reviewers. It provides comprehensive case lifecycle management with notes, attachments, and findings tracking.

### 1.2 Responsibilities
- **Case Lifecycle**: Create, update, and close investigation cases
- **Case Assignment**: Assign cases to compliance officers
- **Evidence Management**: Handle case notes and attachments
- **Investigation Tracking**: Track case progress and findings
- **Visibility Control**: Manage silent case visibility restrictions

### 1.3 Service Boundaries
- **Owns**: Cases, Case Notes, Case Attachments, Investigations
- **Reads From**: Declaration Service (declaration context), User Service (assignee information)
- **Writes To**: Case events (Kafka)
- **Triggered By**: Rule Engine Service, Review Service

---

## 2. Core Entities

### 2.1 Case
```json
{
  "case_id": "UUID",
  "tenant_id": "UUID",
  "declaration_id": "UUID",
  "case_number": "string",
  "type": "silent|escalated|manual",
  "status": "open|investigating|pending|closed|reopened",
  "priority": "low|medium|high",
  "title": "string",
  "description": "string",
  "assigned_to": "UUID",
  "created_by": "UUID",
  "created_at": "timestamp",
  "closed_at": "timestamp",
  "findings": "text",
  "outcome": "no_action|policy_violation|training_required|disciplinary_action"
}
```

### 2.2 Case Note
```json
{
  "note_id": "UUID",
  "case_id": "UUID",
  "author_id": "UUID",
  "content": "text",
  "is_internal": "boolean",
  "created_at": "timestamp"
}
```

### 2.3 Case Attachment
```json
{
  "attachment_id": "UUID",
  "case_id": "UUID",
  "filename": "string",
  "content_type": "string",
  "file_size": "integer",
  "storage_path": "string",
  "uploaded_by": "UUID",
  "uploaded_at": "timestamp"
}
```

---

## 3. API Specifications

### 3.1 Case Management APIs

#### GET /cases?tenant_id={tenant_id}&status={status}&assigned_to={user_id}
Response: List of cases with filtering

#### GET /cases/{case_id}
Response: Full case details with notes and attachments

#### POST /cases
```json
{
  "tenant_id": "UUID",
  "declaration_id": "UUID",
  "type": "manual",
  "priority": "medium",
  "title": "Suspicious trading pattern",
  "description": "Multiple trades in short timeframe",
  "assigned_to": "UUID"
}
```

#### PUT /cases/{case_id}
```json
{
  "status": "investigating",
  "assigned_to": "UUID",
  "priority": "high"
}
```

#### POST /cases/{case_id}/close
```json
{
  "findings": "Investigation revealed no policy violations. Trades were legitimate business activities.",
  "outcome": "no_action"
}
```

#### POST /cases/{case_id}/reopen
```json
{
  "reason": "New evidence discovered"
}
```

### 3.2 Case Notes APIs

#### GET /cases/{case_id}/notes
Response: List of case notes

#### POST /cases/{case_id}/notes
```json
{
  "content": "Reviewed trading records for the past 6 months. Found similar pattern in Q2.",
  "is_internal": true
}
```

#### PUT /cases/{case_id}/notes/{note_id}
Update note content

#### DELETE /cases/{case_id}/notes/{note_id}
Soft delete note

### 3.3 Case Attachments APIs

#### GET /cases/{case_id}/attachments
Response: List of attachments

#### POST /cases/{case_id}/attachments
```
Content-Type: multipart/form-data
file: [binary data]
```

#### GET /cases/{case_id}/attachments/{attachment_id}
Response: File download

#### DELETE /cases/{case_id}/attachments/{attachment_id}
Delete attachment

---

## 4. Business Logic

### 4.1 Case Number Generation
```python
def generate_case_number(tenant_id, case_type):
    year = datetime.now().year
    sequence = get_next_sequence_number(tenant_id, year)
    type_prefix = {
        "silent": "SIL",
        "escalated": "ESC", 
        "manual": "MAN"
    }
    return f"{type_prefix[case_type]}-{year}-{sequence:04d}"
```

### 4.2 Silent Case Visibility
```python
def check_case_visibility(case, requesting_user):
    if case.type == "silent":
        # Silent cases only visible to compliance officers
        if "compliance_officer" not in requesting_user.roles:
            return False
        # Not visible to compliance officer who is subject of case
        if case.declaration and case.declaration.user_id == requesting_user.id:
            return False
    return True
```

### 4.3 Case Assignment Logic
```python
def auto_assign_case(case):
    if case.type == "silent":
        # Assign to least loaded compliance officer
        officers = get_compliance_officers(case.tenant_id)
        workloads = get_case_workloads(officers)
        return min(workloads, key=lambda w: w.active_cases)
    elif case.type == "escalated":
        # Assign to escalation queue owner
        return get_escalation_queue_owner(case.tenant_id)
    return None
```

---

## 5. Events Published

### 5.1 Case Lifecycle Events
```json
{
  "event_type": "case.created",
  "case_id": "UUID",
  "tenant_id": "UUID",
  "declaration_id": "UUID",
  "type": "silent",
  "priority": "medium",
  "assigned_to": "UUID",
  "timestamp": "ISO8601"
}
```

```json
{
  "event_type": "case.status_changed",
  "case_id": "UUID",
  "tenant_id": "UUID",
  "old_status": "open",
  "new_status": "investigating",
  "changed_by": "UUID",
  "timestamp": "ISO8601"
}
```

```json
{
  "event_type": "case.closed",
  "case_id": "UUID",
  "tenant_id": "UUID",
  "outcome": "no_action",
  "closed_by": "UUID",
  "timestamp": "ISO8601"
}
```

---

## 6. External Dependencies

### 6.1 Service Dependencies
- **Declaration Service**: Declaration context and data
- **User Service**: User information for assignments
- **File Storage**: Azure Blob Storage for attachments

### 6.2 Event Subscriptions
- **Rule Engine Events**: case.flagged (create silent cases)
- **Review Events**: review.escalated (create escalated cases)

---

## 7. Implementation Notes

### 7.1 Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with full-text search
- **File Storage**: Azure Blob Storage
- **Search**: PostgreSQL full-text search for case content

### 7.2 Security & Privacy
- **Silent Case Protection**: Special access controls
- **Audit Trail**: Complete audit of case access
- **Data Encryption**: Encrypted storage for sensitive findings

---

## 8. Testing Strategy

### 8.1 Unit Tests
- Case visibility logic
- Assignment algorithms
- Status transition validation

### 8.2 Integration Tests
- Event handling from Rule Engine and Review Service
- File storage operations
- Cross-service data access
