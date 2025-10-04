# ECS-8: User Service - User Stories
## Story Breakdown for Sprint 2

**Epic**: ECS-8 - User Service  
**Total Stories**: 16  
**Estimated Story Points**: 72  
**Sprint Duration**: 1 week (5 working days)

---

## Summary

The User Service is the **identity and access management foundation** for the ComplianceFlow platform. It provides authentication via SSO, authorization via JWT, and user/tenant/business unit management.

### Key Features
- Azure AD SSO authentication with per-tenant configuration
- JWT token generation and validation (RS256)
- Multi-tenant user management with tenant isolation
- Role-based access control (User, Reviewer, Compliance Officer)
- Business unit hierarchy for organizational structure
- Event publishing for user lifecycle events
- Comprehensive admin APIs for tenant and SSO management

### Stories Created
1. **ECS-29**: Database Schema and SQLAlchemy Models (5 pts)
2. **ECS-30**: FastAPI Application Setup (3 pts)
3. **ECS-31**: Database Migrations with Alembic (3 pts)
4. **ECS-32**: JWT Token Generation and Validation (5 pts)
5. **ECS-33**: SSO Authentication Flow (8 pts)
6. **ECS-34**: JWT Key Rotation Endpoints (5 pts) - *Gap addressed*
7. **ECS-35**: User CRUD Operations (5 pts)
8. **ECS-36**: User Status Management (3 pts) - *Gap addressed*
9. **ECS-37**: User Provisioning from SSO (5 pts)
10. **ECS-38**: Tenant Management APIs (5 pts) - *Gap addressed*
11. **ECS-39**: Business Unit Management (5 pts)
12. **ECS-40**: SSO Configuration Management (5 pts)
13. **ECS-41**: Authorization Middleware (3 pts)
14. **ECS-42**: Event Publishing Infrastructure (5 pts) - *Includes login/logout events*
15. **ECS-43**: Testing Infrastructure (5 pts)
16. **ECS-44**: OpenAPI Documentation (3 pts)

**Total**: 75 story points (ECS-38 increased from 5 to 8 due to full onboarding complexity)

---

## Implementation Order

### Phase 1: Foundation (Stories 1-3)
Build the core infrastructure before implementing features.
- ECS-29: Database models
- ECS-30: FastAPI app setup
- ECS-31: Database migrations

### Phase 2: Security Core (Stories 4, 32, 41)
Implement authentication and authorization before user management.
- ECS-32: JWT tokens
- ECS-33: SSO authentication
- ECS-41: Authorization middleware

### Phase 3: User Management (Stories 35-37)
Core user operations and provisioning.
- ECS-35: User CRUD
- ECS-36: User status management
- ECS-37: SSO provisioning

### Phase 4: Multi-Tenancy (Stories 38-40)
Tenant and organizational structure.
- ECS-38: Tenant management
- ECS-39: Business units
- ECS-40: SSO configuration

### Phase 5: Advanced Features (Stories 34, 42)
Key rotation and event publishing.
- ECS-34: JWT key rotation
- ECS-42: Event publishing

### Phase 6: Quality & Documentation (Stories 43-44)
Testing and documentation.
- ECS-43: Testing infrastructure
- ECS-44: OpenAPI docs

---

## Role Model Corrections

During story review, we identified role/persona issues that were corrected:

### Platform vs Tenant Role Confusion
**Problem**: Initial stories conflated Tenant Admin and Compliance Officer responsibilities  
**Impact**: Incorrect permission scoping and security model

**Corrected Stories:**
1. **ECS-34** - JWT Key Rotation: ~~compliance_officer~~ → **Platform Admin** (platform-level security)
2. **ECS-35** - User CRUD: ~~compliance_officer~~ → **Tenant Admin** (manages users within organization)
3. **ECS-36** - User Status: ~~compliance_officer~~ → **Tenant Admin** (employee lifecycle within org)
4. **ECS-38** - Tenant Management: ~~compliance_officer~~ → **Platform Support** (onboards new customers)
5. **ECS-40** - SSO Config: ~~compliance_officer~~ → **Tenant Admin** (configures their org's SSO)
6. **ECS-29** - Database Models: Added platform roles (platform_admin, platform_support, platform_devops)

### Corrected Role Model

**Platform Roles** (ComplianceFlow company staff, tenant_id = null):
- **Platform Admin** - Full platform access, JWT key rotation, emergency access
- **Platform Support** - Customer onboarding, tenant provisioning, support
- **Platform DevOps** - Infrastructure, deployments, monitoring

**Tenant Roles** (Customer organization users, tenant_id = specific tenant):
- **Tenant Admin** - SSO config, user management, business units (IT admin)
- **Compliance Officer** - Rules, forms, cases, investigations (compliance program manager)
- **Reviewer** - Review declarations within their business unit
- **User** - Submit declarations

**Key Insight:** Compliance Officers manage compliance PROGRAMS, not user administration or system configuration.

**Reference:** See `docs/Roles_and_Personas.md` for complete role definitions

---

## Gaps Addressed from PRD Review

During PRD review, we identified 5 functional gaps that have been addressed:

### 1. ✅ Missing Tenant Management APIs
**Problem**: Tenant entity defined but no CRUD APIs
**Solution**: ECS-38 - Complete tenant lifecycle management

### 2. ✅ Missing User Status Management
**Problem**: User.status field but no APIs to change it
**Solution**: ECS-36 - Suspend, reactivate, deactivate endpoints

### 3. ✅ Missing Login/Logout Events
**Problem**: Authentication events not defined
**Solution**: ECS-42 - Added user.login and user.logout events

### 4. ✅ Missing JWT Key Rotation
**Problem**: Key rotation mentioned but no APIs
**Solution**: ECS-34 - Full key rotation with graceful transition

### 5. ✅ SSO Configuration Management
**Problem**: Mentioned in PRD but no detailed APIs
**Solution**: ECS-40 - Complete SSO config management with testing

---

## Dependencies

### External Dependencies
- **ECS-7**: Infrastructure Setup (PostgreSQL, Redis, Event Hubs, Key Vault)
- **Azure AD**: Tenant configured for SSO testing

### Service Dependencies
- **None**: User Service has no internal service dependencies
- **Consumers**: All other services depend on User Service for authentication

---

## Critical Path

```
ECS-29 (Models) → ECS-31 (Migrations) → ECS-32 (JWT) → ECS-33 (SSO) → ECS-37 (Provisioning)
```

This path represents the minimum viable authentication flow.

---

## Risk Items

1. **SSO Integration Complexity**
   - Risk: Azure AD configuration issues
   - Mitigation: Start with spike/testing story

2. **Multi-Tenancy Isolation**
   - Risk: Tenant data leakage
   - Mitigation: Comprehensive security testing

3. **JWT Key Management**
   - Risk: Key rotation disrupts active sessions
   - Mitigation: Graceful rotation with 24-hour grace period

4. **Performance at Scale**
   - Risk: User lookup becomes bottleneck
   - Mitigation: Redis caching, database indexing

---

## Success Criteria

- ✅ Users can authenticate via Azure AD SSO
- ✅ JWT tokens issued and validated correctly
- ✅ Multi-tenant isolation enforced
- ✅ Role-based authorization working
- ✅ Business units support hierarchy
- ✅ Events published to Kafka
- ✅ 80%+ test coverage
- ✅ OpenAPI documentation complete
- ✅ Performance: <100ms authentication, <50ms authorization

---

## Technology Stack

- **Framework**: FastAPI 0.104+ (Python 3.11+)
- **Database**: PostgreSQL 15+ via SQLAlchemy 2.0
- **Authentication**: python-jose (Apache 2.0), authlib (BSD-3-Clause)
- **Messaging**: confluent-kafka-python (Apache 2.0)
- **Testing**: pytest, factory-boy, pact-python (all MIT)
- **Documentation**: FastAPI auto-generated OpenAPI/Swagger

All libraries verified for license compliance (no GPL/LGPL).

---

## Estimated Velocity

**Assuming 1 developer:**
- Foundation (3 stories): 2-3 days
- Security Core (3 stories): 3-4 days
- User Management (3 stories): 2-3 days
- Multi-Tenancy (3 stories): 2-3 days
- Advanced Features (2 stories): 2 days
- Quality & Docs (2 stories): 2 days

**Total: 13-17 days** (approximately 3 sprint weeks with reviews/testing)

**With AI assistance:** 7-10 days (40-50% time savings)

---

## Notes

This epic provides the authentication and authorization foundation for the entire platform. All other services will depend on User Service for:
- User authentication via JWT validation
- User information lookup
- Business unit membership
- Role-based permissions

Quality and security are paramount - this service must be bulletproof.
