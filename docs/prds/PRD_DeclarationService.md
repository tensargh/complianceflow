# Declaration Service PRD
## Compliance Flow Platform

### Service Information
- **Service Name**: Declaration Service
- **Version**: 1.0
- **Date**: December 2024
- **Domain**: Declaration Management

---

## 1. Service Overview

### 1.1 Purpose
The Declaration Service manages the core declaration lifecycle including creation, submission, status tracking, and coordination with other services for evaluation and review.

### 1.2 Responsibilities
- **Declaration CRUD**: Create, read, update, delete declarations
- **Submission Management**: Handle declaration submissions and status transitions
- **Form Coordination**: Interface with Form Service for form selection
- **File Management**: Handle file attachments and document storage
- **Status Orchestration**: Coordinate with Rule Engine and Review Services

### 1.3 Service Boundaries
- **Owns**: Declarations, Submissions, Attachments
- **Reads From**: User Service (user data), Form Service (form definitions)
- **Writes To**: Declaration events (Kafka)
- **Coordinates With**: Rule Engine Service, Review Service

---

## 2. Core Entities

### 2.1 Declaration
```json
{
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "user_id": "UUID",
  "declaration_type": "personal_trade|gift_received|entertainment_received|holdings_attestation",
  "form_id": "UUID",
  "form_version": "integer",
  "form_data": {
    "field_name": "field_value"
  },
  "status": "draft|submitted|under_review|approved|denied|requires_info",
  "submitted_at": "timestamp",
  "decision_at": "timestamp",
  "decision_reason": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 2.2 Declaration Attachment
```json
{
  "attachment_id": "UUID",
  "declaration_id": "UUID",
  "filename": "string",
  "content_type": "string",
  "file_size": "integer",
  "storage_path": "string",
  "uploaded_at": "timestamp"
}
```

### 2.3 Declaration History
```json
{
  "history_id": "UUID",
  "declaration_id": "UUID",
  "action": "created|submitted|approved|denied|info_requested",
  "actor_id": "UUID",
  "actor_type": "user|system|reviewer",
  "old_status": "string",
  "new_status": "string",
  "reason": "string",
  "timestamp": "timestamp"
}
```

---

## 3. API Specifications

### 3.1 Declaration Management APIs

#### POST /declarations
```json
{
  "declaration_type": "personal_trade",
  "form_data": {
    "trade_date": "2024-01-15",
    "symbol": "AAPL",
    "quantity": 100,
    "price": 150.00,
    "trade_type": "buy"
  }
}
```
Response: Created declaration

#### GET /declarations/{declaration_id}
Response: Full declaration with attachments

#### PUT /declarations/{declaration_id}
```json
{
  "form_data": {
    "updated_field": "new_value"
  }
}
```

#### GET /declarations?user_id={user_id}&status={status}&limit={limit}
Response: List of declarations with filtering

#### POST /declarations/{declaration_id}/submit
Submit declaration for evaluation

#### POST /declarations/{declaration_id}/withdraw
Withdraw submitted declaration (if allowed)

### 3.2 Attachment APIs

#### POST /declarations/{declaration_id}/attachments
```
Content-Type: multipart/form-data
file: [binary data]
```
Response: Created attachment

#### GET /declarations/{declaration_id}/attachments
Response: List of attachments

#### GET /declarations/{declaration_id}/attachments/{attachment_id}
Response: File download

#### DELETE /declarations/{declaration_id}/attachments/{attachment_id}
Delete attachment (only if declaration is draft)

### 3.3 Status and History APIs

#### GET /declarations/{declaration_id}/history
Response: Declaration history

#### PUT /declarations/{declaration_id}/status
```json
{
  "status": "approved",
  "reason": "Automatic approval",
  "actor_type": "system"
}
```

---

## 4. Business Logic

### 4.1 Form Selection Logic
```python
def select_form(user, declaration_type):
    # Get user's business unit
    business_unit = get_user_business_unit(user.user_id)
    
    # Query forms for declaration type
    forms = get_forms_for_type(declaration_type, user.tenant_id)
    
    # Filter by business unit and sort by ranking
    matching_forms = [f for f in forms if f.business_unit == business_unit.id]
    
    if matching_forms:
        return max(matching_forms, key=lambda f: f.ranking)
    else:
        # Return fallback form
        return get_fallback_form(declaration_type, user.tenant_id)
```

### 4.2 Status Transition Rules
```python
ALLOWED_TRANSITIONS = {
    "draft": ["submitted", "deleted"],
    "submitted": ["under_review", "approved", "denied"],
    "under_review": ["approved", "denied", "requires_info"],
    "requires_info": ["submitted"],
    "approved": [],  # Terminal state
    "denied": []     # Terminal state
}
```

### 4.3 Validation Rules
- **Draft**: Minimal validation, allow incomplete data
- **Submission**: Full form validation, required fields check
- **File Size**: Max 10MB per attachment, 50MB total per declaration
- **File Types**: PDF, DOC, DOCX, JPG, PNG, Excel files only

---

## 5. Events Published

### 5.1 Declaration Lifecycle Events
```json
{
  "event_type": "declaration.created",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "user_id": "UUID",
  "declaration_type": "string",
  "timestamp": "ISO8601"
}
```

```json
{
  "event_type": "declaration.submitted",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "user_id": "UUID",
  "declaration_type": "string",
  "form_data": "object",
  "timestamp": "ISO8601"
}
```

```json
{
  "event_type": "declaration.status_changed",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "old_status": "string",
  "new_status": "string",
  "actor_id": "UUID",
  "actor_type": "string",
  "reason": "string",
  "timestamp": "ISO8601"
}
```

---

## 6. External Dependencies

### 6.1 Service Dependencies
- **User Service**: User validation and business unit lookup
- **Form Service**: Form definitions and validation rules
- **File Storage**: Azure Blob Storage for attachments

### 6.2 Event Subscriptions
- **User Events**: user.deactivated (for data cleanup)
- **Form Events**: form.updated (for form version tracking)

---

## 7. Data Storage

### 7.1 Database Schema
- **Primary Database**: PostgreSQL
- **Multi-tenancy**: Row-level security with tenant_id
- **Indexing**: Indexes on user_id, status, declaration_type, submitted_at

### 7.2 File Storage
- **Provider**: Azure Blob Storage
- **Structure**: /{tenant_id}/declarations/{declaration_id}/{filename}
- **Security**: Signed URLs for secure access
- **Retention**: Follows tenant data retention policy

### 7.3 Performance Requirements
- **Declaration Creation**: < 200ms
- **Declaration Retrieval**: < 100ms
- **File Upload**: < 5 seconds for 10MB file
- **List Operations**: < 500ms for paginated results

---

## 8. Security Requirements

### 8.1 Access Control
- **User Data**: Users can only access their own declarations
- **Reviewer Access**: Reviewers can access assigned declarations
- **Compliance Access**: Full access within tenant
- **Tenant Isolation**: Strict tenant data separation

### 8.2 Data Privacy
- **PII Handling**: Secure handling of personal information
- **File Security**: Encrypted file storage with signed URLs
- **Audit Trail**: Complete action audit trail

---

## 9. Implementation Notes

### 9.1 Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy
- **File Storage**: Azure Blob Storage SDK
- **Validation**: Pydantic models

### 9.2 Caching Strategy
- **Form Definitions**: Cache form data (15 min TTL)
- **User Business Units**: Cache user BU mappings (30 min TTL)
- **Declaration Lists**: No caching (real-time data)

### 9.3 Error Handling
- **File Upload Failures**: Retry mechanism with exponential backoff
- **Form Service Unavailable**: Use cached form definitions
- **Database Failures**: Circuit breaker pattern

---

## 10. Testing Strategy

### 10.1 Unit Tests
- Declaration CRUD operations
- Status transition validation
- Form selection logic
- File upload handling

### 10.2 Integration Tests
- Form Service integration
- User Service integration
- File storage operations
- Event publishing

### 10.3 Performance Tests
- Concurrent declaration submissions
- Large file uploads
- High-volume list operations
