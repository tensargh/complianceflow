# User Service PRD
## Compliance Flow Platform

### Service Information
- **Service Name**: User Service
- **Version**: 1.0
- **Date**: December 2024
- **Domain**: Identity & Access Management

---

## 1. Service Overview

### 1.1 Purpose
The User Service manages user identity, authentication, authorization, and business unit organization within the multi-tenant Compliance Flow platform.

### 1.2 Responsibilities
- **User Lifecycle**: Provision, update, and deactivate users
- **SSO Integration**: Manage per-tenant SSO configuration and authentication
- **Role Management**: Map SSO groups to application roles
- **Business Unit Management**: Organize users into business units
- **Attribute Mapping**: Custom mapping of SSO attributes to user profiles

### 1.3 Service Boundaries
- **Owns**: Users, Business Units, SSO Configuration
- **Reads From**: External SSO providers
- **Writes To**: User events (Kafka)
- **Does NOT**: Handle declaration data, reviews, or cases

---

## 2. Core Entities

### 2.1 User
```json
{
  "user_id": "UUID",
  "tenant_id": "UUID",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "business_unit_id": "UUID",
  "sso_groups": ["string"],
  "roles": ["user", "reviewer", "compliance_officer"],
  "status": "active|suspended|deactivated",
  "last_login": "timestamp",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 2.2 Business Unit
```json
{
  "business_unit_id": "UUID",
  "tenant_id": "UUID",
  "name": "string",
  "parent_id": "UUID", // Optional for hierarchy
  "code": "string", // Short identifier
  "description": "string",
  "created_at": "timestamp"
}
```

### 2.3 SSO Configuration
```json
{
  "sso_config_id": "UUID",
  "tenant_id": "UUID",
  "provider_type": "azure_ad|okta|google",
  "client_id": "string",
  "client_secret": "string", // Encrypted
  "authority": "string",
  "attribute_mappings": {
    "email": "sso_field_name",
    "first_name": "sso_field_name",
    "last_name": "sso_field_name",
    "business_unit": "sso_field_name",
    "groups": "sso_field_name"
  },
  "role_mappings": {
    "sso_group_name": ["application_role"]
  },
  "created_at": "timestamp"
}
```

---

## 3. API Specifications

### 3.1 Authentication APIs

#### POST /auth/login
```json
{
  "tenant_domain": "string",
  "redirect_uri": "string"
}
```
Response: SSO redirect URL

#### POST /auth/callback
```json
{
  "code": "string",
  "state": "string"
}
```
Response: JWT token + user profile

#### POST /auth/refresh
```json
{
  "refresh_token": "string"
}
```
Response: New JWT token

### 3.2 User Management APIs

#### GET /users/{user_id}
Response: User profile

#### PUT /users/{user_id}
```json
{
  "first_name": "string",
  "last_name": "string",
  "business_unit_id": "UUID"
}
```

#### GET /users?tenant_id={tenant_id}&business_unit_id={bu_id}
Response: List of users with filtering

#### POST /users/provision
```json
{
  "tenant_id": "UUID",
  "sso_user_data": "object"
}
```
Response: Created user

### 3.3 Business Unit APIs

#### GET /business-units?tenant_id={tenant_id}
Response: List of business units

#### POST /business-units
```json
{
  "tenant_id": "UUID",
  "name": "string",
  "parent_id": "UUID",
  "code": "string",
  "description": "string"
}
```

#### PUT /business-units/{bu_id}
Update business unit

#### DELETE /business-units/{bu_id}
Soft delete business unit

---

## 4. Events Published

### 4.1 User Events
```json
{
  "event_type": "user.provisioned",
  "user_id": "UUID",
  "tenant_id": "UUID",
  "timestamp": "ISO8601",
  "data": {
    "email": "string",
    "roles": ["string"],
    "business_unit_id": "UUID"
  }
}
```

```json
{
  "event_type": "user.role_changed",
  "user_id": "UUID",
  "tenant_id": "UUID",
  "timestamp": "ISO8601",
  "data": {
    "old_roles": ["string"],
    "new_roles": ["string"]
  }
}
```

```json
{
  "event_type": "user.deactivated",
  "user_id": "UUID",
  "tenant_id": "UUID",
  "timestamp": "ISO8601"
}
```

---

## 5. External Integrations

### 5.1 SSO Providers
- **Azure AD**: Primary provider with OIDC/OAuth2
- **Future**: Okta, Google Workspace support
- **Protocol**: OpenID Connect with PKCE

### 5.2 External Dependencies
- **None**: This service has no dependencies on other internal services

---

## 6. Data Storage

### 6.1 Database Schema
- **Primary Database**: PostgreSQL
- **Multi-tenancy**: Row-level security with tenant_id
- **Encryption**: At-rest encryption for sensitive fields (SSO secrets)

### 6.2 Performance Requirements
- **User Lookup**: < 100ms for authentication
- **Provisioning**: < 500ms for new user creation
- **Bulk Operations**: Support 1000+ user imports per batch

---

## 7. Security Requirements

### 7.1 Authentication
- **JWT Tokens**: Short-lived access tokens (15 min)
- **Refresh Tokens**: Long-lived (24 hours) with rotation
- **Token Validation**: RS256 signing with key rotation

### 7.2 Authorization
- **Tenant Isolation**: Strict tenant data isolation
- **Role Enforcement**: Role-based access control
- **SSO Security**: Secure storage of SSO credentials

### 7.3 Audit Requirements
- **Login Events**: All authentication attempts
- **Role Changes**: User role modifications
- **Admin Actions**: SSO configuration changes

---

## 8. Implementation Notes

### 8.1 Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy
- **Authentication**: python-jose for JWT handling
- **SSO**: authlib for OIDC integration

### 8.2 Deployment
- **Container**: Docker with Azure Container Apps
- **Scaling**: Horizontal auto-scaling
- **Secrets**: Azure Key Vault for SSO credentials

### 8.3 Monitoring
- **Health Checks**: /health endpoint
- **Metrics**: Authentication success/failure rates, response times
- **Alerts**: SSO configuration failures, high error rates

---

## 9. Testing Strategy

### 9.1 Unit Tests
- User CRUD operations
- JWT token generation/validation
- Role mapping logic

### 9.2 Integration Tests
- SSO provider integration
- Database operations
- Event publishing

### 9.3 Security Tests
- Token validation edge cases
- Tenant isolation verification
- SSO attack scenarios
