# Notification Service PRD
## Compliance Flow Platform

### Service Information
- **Service Name**: Notification Service
- **Version**: 1.0
- **Date**: December 2024
- **Domain**: Communication & Notifications

---

## 1. Service Overview

### 1.1 Purpose
The Notification Service manages all communication and notification delivery across the platform, including email notifications, template management, and future support for additional channels.

### 1.2 Responsibilities
- **Email Delivery**: Send transactional and notification emails
- **Template Management**: Manage notification templates with mail-merge capabilities
- **Delivery Tracking**: Track notification delivery status and failures
- **Channel Management**: Support multiple notification channels (email primary)
- **Recipient Configuration**: Manage notification recipients per tenant

### 1.3 Service Boundaries
- **Owns**: Notification Templates, Delivery Records, Channel Configuration
- **Reads From**: All services (via events for notification triggers)
- **Writes To**: Notification events (Kafka), External email providers
- **Integrates With**: Azure Communication Services, SendGrid, etc.

---

## 2. Core Entities

### 2.1 Notification Template
```json
{
  "template_id": "UUID",
  "tenant_id": "UUID",
  "name": "string",
  "description": "string",
  "event_type": "declaration.submitted|review.assigned|case.created",
  "channel": "email|sms|teams|slack",
  "subject_template": "Declaration {{declaration_id}} submitted for review",
  "body_template": "Hello {{user.first_name}}, your {{declaration_type}} declaration has been submitted...",
  "recipients": {
    "to": ["declarer", "reviewers", "compliance"],
    "cc": ["fixed_email@company.com"],
    "bcc": ["audit@company.com"]
  },
  "status": "active|inactive",
  "created_by": "UUID",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 2.2 Notification Record
```json
{
  "notification_id": "UUID",
  "tenant_id": "UUID",
  "template_id": "UUID",
  "event_id": "UUID",
  "channel": "email",
  "recipient": "user@example.com",
  "subject": "string",
  "body": "text",
  "status": "pending|sent|failed|bounced",
  "sent_at": "timestamp",
  "delivered_at": "timestamp",
  "error_message": "string",
  "retry_count": "integer",
  "created_at": "timestamp"
}
```

### 2.3 Channel Configuration
```json
{
  "config_id": "UUID",
  "tenant_id": "UUID",
  "channel": "email",
  "provider": "azure_communication|sendgrid|ses",
  "configuration": {
    "smtp_server": "string",
    "port": "integer",
    "username": "string",
    "api_key": "string",
    "from_address": "noreply@company.com",
    "from_name": "Compliance Flow"
  },
  "status": "active|inactive",
  "created_at": "timestamp"
}
```

---

## 3. API Specifications

### 3.1 Template Management APIs

#### GET /templates?tenant_id={tenant_id}&event_type={type}
Response: List of notification templates

#### GET /templates/{template_id}
Response: Template details

#### POST /templates
```json
{
  "tenant_id": "UUID",
  "name": "Declaration Submitted",
  "event_type": "declaration.submitted",
  "channel": "email",
  "subject_template": "Declaration {{declaration_id}} submitted",
  "body_template": "Your {{declaration_type}} declaration has been submitted for review...",
  "recipients": {
    "to": ["declarer"],
    "cc": ["compliance"]
  }
}
```

#### PUT /templates/{template_id}
Update template

#### DELETE /templates/{template_id}
Deactivate template

### 3.2 Notification Delivery APIs

#### POST /notifications/send
```json
{
  "template_id": "UUID",
  "context_data": {
    "declaration_id": "UUID",
    "user": {...},
    "declaration_type": "personal_trade"
  },
  "override_recipients": ["specific@email.com"]
}
```

#### GET /notifications/{notification_id}
Response: Notification delivery status

#### GET /notifications?tenant_id={tenant_id}&status={status}&date_from={date}
Response: Notification delivery history

#### POST /notifications/{notification_id}/retry
Retry failed notification

### 3.3 Channel Configuration APIs

#### GET /channels?tenant_id={tenant_id}
Response: Channel configurations

#### POST /channels
```json
{
  "tenant_id": "UUID",
  "channel": "email",
  "provider": "sendgrid",
  "configuration": {
    "api_key": "string",
    "from_address": "compliance@company.com",
    "from_name": "Company Compliance"
  }
}
```

#### PUT /channels/{config_id}
Update channel configuration

---

## 4. Business Logic

### 4.1 Template Processing
```python
def process_template(template, context_data):
    # Resolve recipients
    recipients = resolve_recipients(template.recipients, context_data)
    
    # Render subject and body
    subject = render_template(template.subject_template, context_data)
    body = render_template(template.body_template, context_data)
    
    return NotificationRequest(
        recipients=recipients,
        subject=subject,
        body=body,
        channel=template.channel
    )

def resolve_recipients(recipient_config, context_data):
    recipients = {"to": [], "cc": [], "bcc": []}
    
    for role in recipient_config.get("to", []):
        if role == "declarer":
            recipients["to"].append(context_data["user"]["email"])
        elif role == "reviewers":
            recipients["to"].extend(get_reviewer_emails(context_data))
        elif role == "compliance":
            recipients["to"].extend(get_compliance_emails(context_data["tenant_id"]))
    
    # Add fixed email addresses
    recipients["cc"].extend(recipient_config.get("cc", []))
    recipients["bcc"].extend(recipient_config.get("bcc", []))
    
    return recipients
```

### 4.2 Delivery Management
```python
def send_notification(notification_request):
    try:
        channel_config = get_channel_config(
            notification_request.tenant_id, 
            notification_request.channel
        )
        
        provider = get_provider(channel_config.provider)
        result = provider.send(notification_request)
        
        record_delivery(notification_request, "sent", result)
        
    except Exception as e:
        record_delivery(notification_request, "failed", error=str(e))
        schedule_retry(notification_request)
```

### 4.3 Retry Logic
```python
def should_retry(notification_record):
    if notification_record.retry_count >= MAX_RETRIES:
        return False
        
    if notification_record.status in ["bounced", "invalid_email"]:
        return False
        
    return True

def calculate_retry_delay(retry_count):
    # Exponential backoff: 1min, 5min, 15min, 1hour
    delays = [60, 300, 900, 3600]
    return delays[min(retry_count, len(delays) - 1)]
```

---

## 5. Event Handling

### 5.1 Event Subscriptions
The service subscribes to all domain events that may trigger notifications:

```python
EVENT_TEMPLATE_MAPPING = {
    "declaration.submitted": ["declaration_submitted"],
    "declaration.approved": ["declaration_approved"],
    "declaration.denied": ["declaration_denied"],
    "review.assigned": ["review_assigned"],
    "review.completed": ["review_completed"],
    "review.escalated": ["review_escalated"],
    "case.created": ["case_created"],
    "case.assigned": ["case_assigned"],
    "user.provisioned": ["user_welcome"]
}
```

### 5.2 Event Processing
```python
async def handle_event(event):
    # Find applicable templates
    templates = get_templates_for_event(event.type, event.tenant_id)
    
    for template in templates:
        if template.status == "active":
            # Enrich event data with context
            context_data = enrich_event_context(event)
            
            # Process and send notification
            await process_and_send_notification(template, context_data)
```

---

## 6. External Dependencies

### 6.1 Email Providers
- **Azure Communication Services**: Primary email provider
- **SendGrid**: Alternative provider
- **Amazon SES**: Future support

### 6.2 Service Dependencies
- **User Service**: User email addresses and preferences
- **Declaration Service**: Declaration context data
- **Review Service**: Reviewer information
- **Case Service**: Case details

---

## 7. Implementation Notes

### 7.1 Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL for templates and delivery records
- **Queue**: Celery with Redis for async delivery
- **Templates**: Jinja2 for template rendering
- **Email**: Azure Communication Services SDK

### 7.2 Performance & Reliability
- **Async Processing**: All notifications sent asynchronously
- **Retry Mechanism**: Exponential backoff for failed deliveries
- **Rate Limiting**: Respect provider rate limits
- **Dead Letter Queue**: For notifications that fail permanently

### 7.3 Security
- **Template Validation**: Prevent injection attacks in templates
- **Recipient Validation**: Validate email addresses before sending
- **Credential Security**: Secure storage of provider credentials

---

## 8. Testing Strategy

### 8.1 Unit Tests
- Template rendering with various data
- Recipient resolution logic
- Retry mechanism
- Error handling

### 8.2 Integration Tests
- Email provider integration
- Event processing workflow
- Template CRUD operations
- Delivery tracking

### 8.3 Performance Tests
- High-volume notification processing
- Template rendering performance
- Provider failover scenarios
