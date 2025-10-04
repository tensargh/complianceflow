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
- **User Lifecycle**: Provision, update, and deactivate users (tenant-scoped and platform-scoped)
- **SSO Integration**: Manage per-tenant SSO configuration and authentication
- **Role Management**: Map SSO groups to application roles (platform and tenant roles)
- **Business Unit Management**: Organize users into business units (tenant-scoped)
- **Attribute Mapping**: Custom mapping of SSO attributes to user profiles
- **Tenant Provisioning**: Onboarding new customer organizations to the platform
- **Platform Administration**: Manage platform-level security and operations

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
  "tenant_id": "UUID", // nullable for platform roles
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "business_unit_id": "UUID", // nullable
  "sso_groups": ["string"],
  "roles": ["user", "reviewer", "compliance_officer", "tenant_admin", "platform_admin", "platform_support", "platform_devops"],
  "status": "active|suspended|deactivated",
  "last_login": "timestamp",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

**Role Definitions:**
- **Platform Roles** (tenant_id = null): `platform_admin`, `platform_support`, `platform_devops`
- **Tenant Roles** (tenant_id = specific tenant): `user`, `reviewer`, `compliance_officer`, `tenant_admin`

### 2.2 Tenant
```json
{
  "tenant_id": "UUID",
  "name": "string", // Customer organization name
  "domain": "string", // Unique domain identifier
  "status": "active|suspended|archived",
  "billing_contact": "string",
  "technical_contact": "string",
  "created_at": "timestamp",
  "onboarded_at": "timestamp"
}
```

### 2.3 Business Unit
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

### 2.4 SSO Configuration
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
  "is_configured": "boolean", // false until Tenant Admin completes setup
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

---

## 3. API Specifications

### 3.1 Platform Administration APIs

#### POST /api/v1/platform/tenants (Platform Support)
Create new tenant for customer onboarding
```json
{
  "name": "string",
  "domain": "string",
  "billing_contact": "string",
  "technical_contact": "string"
}
```
Response: Tenant + temp admin credentials

#### GET /api/v1/platform/tenants (Platform Support/Admin)
List all tenants across platform

#### POST /api/v1/platform/tenants/{id}/suspend (Platform Support/Admin)
Suspend tenant (billing issues, contract termination)

#### POST /api/v1/platform/jwt-keys/generate (Platform Admin)
Rotate JWT signing keys (affects all tenants)

### 3.2 Tenant Administration APIs

#### POST /api/v1/admin/sso-config (Tenant Admin)
Configure SSO for this tenant's organization

#### GET /api/v1/admin/sso-config (Tenant Admin)
Get this tenant's SSO configuration

#### POST /api/v1/admin/sso-config/test (Tenant Admin)
Test SSO configuration

### 3.3 Authentication APIs

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

### 3.4 User Management APIs (Tenant Admin)

#### GET /users/{user_id}
Response: User profile (tenant-isolated)

#### PUT /users/{user_id}
Update user within tenant
```json
{
  "first_name": "string",
  "last_name": "string",
  "business_unit_id": "UUID",
  "roles": ["string"]
}
```

#### POST /users/{user_id}/suspend (Tenant Admin)
Suspend user account

#### POST /users/{user_id}/deactivate (Tenant Admin)
Deactivate user (employee departure)

#### GET /users?business_unit_id={bu_id}
List users within tenant with filtering

#### POST /users/provision (Internal)
Auto-provision user from SSO
```json
{
  "tenant_id": "UUID",
  "sso_user_data": "object"
}
```
Response: Created user

### 3.5 Business Unit APIs (Tenant Admin)

#### GET /business-units
Response: List of business units in my tenant

#### POST /business-units (Tenant Admin)
```json
{
  "name": "string",
  "parent_id": "UUID",
  "code": "string",
  "description": "string"
}
```

#### PUT /business-units/{bu_id} (Tenant Admin)
Update business unit within tenant

#### DELETE /business-units/{bu_id} (Tenant Admin)
Soft delete business unit (if no active users)

---

## 4. Events Published

### 4.1 Tenant Events
```json
{
  "event_type": "tenant.created",
  "tenant_id": "UUID",
  "timestamp": "ISO8601",
  "data": {
    "name": "string",
    "domain": "string",
    "created_by": "platform_support_user_id"
  }
}
```

```json
{
  "event_type": "tenant.suspended",
  "tenant_id": "UUID",
  "timestamp": "ISO8601",
  "data": {
    "reason": "string",
    "suspended_by": "platform_support_user_id"
  }
}
```

### 4.2 User Events
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

```json
{
  "event_type": "user.login",
  "user_id": "UUID",
  "tenant_id": "UUID",
  "timestamp": "ISO8601",
  "data": {
    "ip_address": "string",
    "user_agent": "string"
  }
}
```

```json
{
  "event_type": "user.logout",
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
