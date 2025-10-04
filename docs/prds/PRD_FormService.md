# Form Service PRD
## Compliance Flow Platform

### Service Information
- **Service Name**: Form Service
- **Version**: 1.0
- **Date**: December 2024
- **Domain**: Form Management

---

## 1. Service Overview

### 1.1 Purpose
The Form Service manages dynamic form definitions, versioning, and selection logic for declaration types. It provides form builder capabilities for compliance officers and serves form definitions to other services.

### 1.2 Responsibilities
- **Form Definition**: Create and manage form schemas
- **Form Versioning**: Version control and publishing workflows
- **Business Unit Mapping**: Associate forms with business units
- **Form Selection**: Provide selection logic for declaration submissions
- **Validation Rules**: Define and enforce form validation

### 1.3 Service Boundaries
- **Owns**: Forms, Form Versions, Form Templates, Validation Rules
- **Reads From**: User Service (business unit information)
- **Writes To**: Form events (Kafka)
- **Serves**: Declaration Service, Analytics Service

---

## 2. Core Entities

### 2.1 Form Definition
```json
{
  "form_id": "UUID",
  "tenant_id": "UUID",
  "declaration_type": "personal_trade|gift_received|entertainment_received|holdings_attestation",
  "name": "string",
  "description": "string",
  "business_units": ["UUID"],
  "ranking": "integer",
  "is_fallback": "boolean",
  "status": "draft|published|archived",
  "current_version": "integer",
  "created_by": "UUID",
  "created_at": "timestamp",
  "published_at": "timestamp"
}
```

### 2.2 Form Version
```json
{
  "version_id": "UUID",
  "form_id": "UUID",
  "version_number": "integer",
  "schema": {
    "sections": [
      {
        "section_id": "trade_details",
        "title": "Trade Details",
        "fields": [
          {
            "field_id": "trade_date",
            "type": "date",
            "label": "Trade Date",
            "required": true,
            "validation": {
              "max_date": "today"
            }
          },
          {
            "field_id": "symbol",
            "type": "text",
            "label": "Stock Symbol",
            "required": true,
            "validation": {
              "pattern": "^[A-Z]{1,5}$",
              "max_length": 5
            }
          }
        ]
      }
    ],
    "conditional_logic": [
      {
        "condition": "trade_type == 'options'",
        "show_fields": ["expiration_date", "strike_price"],
        "hide_fields": []
      }
    ]
  },
  "created_by": "UUID",
  "created_at": "timestamp",
  "approved_by": "UUID",
  "approved_at": "timestamp"
}
```

### 2.3 Field Type Definition
```json
{
  "type": "text|number|date|dropdown|checkbox|file_upload|currency",
  "properties": {
    "max_length": "integer",
    "min_value": "number",
    "max_value": "number",
    "options": ["array of strings for dropdown"],
    "multiple": "boolean for file uploads",
    "currency_code": "string for currency fields"
  }
}
```

---

## 3. API Specifications

### 3.1 Form Selection APIs

#### GET /forms/select?declaration_type={type}&business_unit_id={bu_id}&tenant_id={tenant_id}
Response: Selected form definition for declaration

#### GET /forms/{form_id}/versions/{version}
Response: Specific form version schema

### 3.2 Form Management APIs

#### GET /forms?tenant_id={tenant_id}&declaration_type={type}&status={status}
Response: List of forms with filtering

#### POST /forms
```json
{
  "tenant_id": "UUID",
  "declaration_type": "personal_trade",
  "name": "Trading Desk Personal Trade Form",
  "description": "Form for trading desk personal trade declarations",
  "business_units": ["UUID"],
  "ranking": 100
}
```

#### PUT /forms/{form_id}
Update form metadata

#### POST /forms/{form_id}/versions
```json
{
  "schema": {
    "sections": [...],
    "conditional_logic": [...]
  },
  "change_notes": "Added options trading fields"
}
```

#### POST /forms/{form_id}/publish
```json
{
  "version_number": 2,
  "effective_date": "2024-02-01T00:00:00Z"
}
```

### 3.3 Form Builder APIs

#### GET /form-builder/field-types
Response: Available field types and properties

#### POST /form-builder/validate
```json
{
  "schema": {...},
  "test_data": {...}
}
```
Response: Validation results

#### GET /form-builder/templates
Response: Form templates for common declaration types

---

## 4. Business Logic

### 4.1 Form Selection Algorithm
```python
def select_form(declaration_type, business_unit_id, tenant_id):
    # Get published forms for declaration type
    forms = get_published_forms(declaration_type, tenant_id)
    
    # Filter by business unit
    matching_forms = [
        f for f in forms 
        if business_unit_id in f.business_units or f.is_fallback
    ]
    
    # Sort by ranking (highest first)
    matching_forms.sort(key=lambda f: f.ranking, reverse=True)
    
    # Return highest ranking non-fallback form, or fallback
    non_fallback = [f for f in matching_forms if not f.is_fallback]
    if non_fallback:
        return non_fallback[0]
    else:
        fallback = [f for f in matching_forms if f.is_fallback]
        return fallback[0] if fallback else None
```

### 4.2 Form Validation
```python
def validate_form_data(form_version, data):
    errors = []
    
    for section in form_version.schema.sections:
        for field in section.fields:
            field_value = data.get(field.field_id)
            
            # Required field validation
            if field.required and not field_value:
                errors.append(f"{field.label} is required")
                continue
                
            # Type-specific validation
            if field_value:
                field_errors = validate_field(field, field_value)
                errors.extend(field_errors)
    
    # Conditional logic validation
    errors.extend(validate_conditional_logic(form_version.schema, data))
    
    return errors
```

### 4.3 Version Management
```python
def create_new_version(form_id, schema, created_by):
    current_version = get_current_version(form_id)
    new_version_number = current_version.version_number + 1
    
    return FormVersion(
        form_id=form_id,
        version_number=new_version_number,
        schema=schema,
        created_by=created_by,
        status="draft"
    )
```

---

## 5. Events Published

### 5.1 Form Events
```json
{
  "event_type": "form.created",
  "form_id": "UUID",
  "tenant_id": "UUID",
  "declaration_type": "string",
  "created_by": "UUID",
  "timestamp": "ISO8601"
}
```

```json
{
  "event_type": "form.published",
  "form_id": "UUID",
  "tenant_id": "UUID",
  "version_number": "integer",
  "effective_date": "ISO8601",
  "published_by": "UUID",
  "timestamp": "ISO8601"
}
```

---

## 6. External Dependencies

### 6.1 Service Dependencies
- **User Service**: Business unit information for form selection

### 6.2 Event Subscriptions
- **User Events**: business_unit.updated (refresh form assignments)

---

## 7. Implementation Notes

### 7.1 Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with JSON support for schema storage
- **Validation**: JSON Schema for form validation
- **Caching**: Redis for form definition caching

### 7.2 Performance Optimization
- **Form Caching**: Cache published forms (30 min TTL)
- **Schema Validation**: Pre-compile validation schemas
- **Selection Logic**: Index on business_units and ranking

---

## 8. Testing Strategy

### 8.1 Unit Tests
- Form selection algorithm
- Schema validation logic
- Version management
- Conditional field logic

### 8.2 Integration Tests
- Form builder workflow
- Version publishing process
- Cross-service form retrieval
