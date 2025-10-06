# Infrastructure Architecture
## ComplianceFlow Multi-Region, Multi-Instance Deployment

**Version:** 1.0  
**Date:** October 6, 2025  
**Status:** Active Architecture Document  
**Purpose:** Define infrastructure deployment strategy, CIDR allocation, and multi-region support

---

## 🎯 Overview

ComplianceFlow infrastructure is designed to support **multi-region, multi-instance deployments** with complete isolation between deployments. This enables:

- **Geographic distribution** for data residency compliance (EU, US)
- **Environment separation** (test/dev, staging, production)
- **Blue/Green deployments** (multiple production instances per region)
- **Independent scaling** (each deployment scales independently)
- **Disaster recovery** (cross-region failover capability)

---

## 📐 Deployment Naming Convention

### Format

**Global Deployments** (shared infrastructure):
```
global-{environment}
```

**Regional Deployments**:
```
{region-code}-{environment}-{instance}
```

### Components
- **region-code**: Azure region identifier (lowercase, abbreviated)
- **environment**: `dev`, `stg`, `prod`
- **instance**: Sequential number starting at 1

### Global vs Regional

**Global Deployments** (no numbering needed):
- Purpose: Shared master data, tenant registry, global APIs
- Location: West Europe (GDPR compliance)
- Examples: `global-dev`, `global-stg`, `global-prod`

**Regional Deployments** (numbered for scale):
- Purpose: Regional application instances
- Location: Any Azure region
- Instance numbering for:
  - **Scalability**: When hitting Azure subscription/region limits
  - **Customer isolation**: Dedicated instance for enterprise customer requiring standalone deployment
- Examples: `westeu-dev-1`, `eastus-prod-1`, `westeu-prod-2`

**Note on Blue/Green**: Handled at **application layer** (Azure Container Apps), NOT infrastructure layer. All environments use blue/green deployment strategy for zero-downtime updates.

### Examples
| Deployment Name | Azure Region | Purpose |
|-----------------|--------------|---------|
| `global-dev` | West Europe | Global dev: Tenant registry, master data |
| `global-stg` | West Europe | Global staging: Tenant registry, master data |
| `global-prod` | West Europe | Global production: Tenant registry, master data |
| `westeu-dev-1` | West Europe | Primary dev/test environment |
| `westeu-stg-1` | West Europe | Staging/UAT environment |
| `westeu-prod-1` | West Europe | Primary production (Europe) |
| `westeu-prod-2` | West Europe | Scale-out or dedicated customer instance |
| `eastus-prod-1` | East US | Production (US data residency) |
| `northeu-prod-1` | North Europe | Production (Nordic data residency) |

---

## 🗺️ CIDR Allocation Strategy

### Allocation Principles
1. **Non-overlapping ranges** - Each deployment gets a unique /16 CIDR block
2. **Regional grouping** - Adjacent /16 blocks for same region enable peering
3. **Future growth** - Reserve ranges for planned deployments
4. **Subnet consistency** - Same subnet structure within each /16

### CIDR Allocation Table

| Deployment | CIDR Block | IP Range | Addresses | Status |
|------------|------------|----------|-----------|--------|
| **Global (West Europe)** |
| `global-dev` | `10.0.0.0/16` | 10.0.0.0 - 10.0.255.255 | 65,536 | Active (MVP) |
| `global-stg` | `10.1.0.0/16` | 10.1.0.0 - 10.1.255.255 | 65,536 | Reserved |
| `global-prod` | `10.2.0.0/16` | 10.2.0.0 - 10.2.255.255 | 65,536 | Reserved |
| **West Europe Regional** |
| `westeu-dev-1` | `10.10.0.0/16` | 10.10.0.0 - 10.10.255.255 | 65,536 | Active (MVP) |
| `westeu-stg-1` | `10.20.0.0/16` | 10.20.0.0 - 10.20.255.255 | 65,536 | Reserved |
| `westeu-prod-1` | `10.30.0.0/16` | 10.30.0.0 - 10.30.255.255 | 65,536 | Reserved |
| `westeu-prod-2` | `10.31.0.0/16` | 10.31.0.0 - 10.31.255.255 | 65,536 | Reserved |
| **East US Regional** |
| `eastus-dev-1` | `10.11.0.0/16` | 10.11.0.0 - 10.11.255.255 | 65,536 | Reserved |
| `eastus-stg-1` | `10.21.0.0/16` | 10.21.0.0 - 10.21.255.255 | 65,536 | Reserved |
| `eastus-prod-1` | `10.40.0.0/16` | 10.40.0.0 - 10.40.255.255 | 65,536 | Reserved |
| **North Europe Regional** |
| `northeu-prod-1` | `10.50.0.0/16` | 10.50.0.0 - 10.50.255.255 | 65,536 | Reserved |
| **Future Regions** |
| RESERVED | `10.60.0.0/16` - `10.99.0.0/16` | - | - | Available |

### Subnet Structure (within each /16)

Each deployment uses consistent subnet allocation:

| Subnet Name | CIDR Suffix | Example (westeu-prod-1) | Purpose |
|-------------|-------------|-------------------------|---------|
| Container Apps | `.1.0/24` | `10.30.1.0/24` | Azure Container Apps environment |
| Database | `.2.0/24` | `10.30.2.0/24` | PostgreSQL Flexible Server |
| Redis | `.3.0/24` | `10.30.3.0/24` | Azure Cache for Redis |
| Storage | `.4.0/24` | `10.30.4.0/24` | Private endpoints for Storage |
| API Management | `.5.0/24` | `10.30.5.0/24` | Azure API Management (prod only) |
| Management | `.10.0/24` | `10.30.10.0/24` | Bastion, jump boxes, management VMs |
| RESERVED | `.20.0/24` - `.255.0/24` | - | Future services |

---

## 🏗️ Terraform Deployment Strategy

### Approach: Workspace + tfvars Files

We use **Terraform workspaces** combined with **deployment-specific tfvars files** to manage multiple deployments from a single Terraform codebase.

### Directory Structure

```
infrastructure/
├── main.tf                          # Root module (deployment-agnostic)
├── variables.tf                     # Variable definitions
├── outputs.tf                       # Output definitions
├── backend.tf                       # Backend configuration
├── locals.tf                        # CIDR map and derived values
├── modules/                         # Reusable Terraform modules
│   ├── networking/
│   ├── database/
│   ├── redis/
│   ├── key_vault/
│   └── ...
├── deployments/                     # One tfvars file per deployment
│   ├── westeu-test-1.tfvars         # West Europe test environment
│   ├── westeu-stg-1.tfvars          # West Europe staging
│   ├── westeu-prod-1.tfvars         # West Europe production #1
│   ├── westeu-prod-2.tfvars         # West Europe production #2 (blue/green)
│   └── eastus-prod-1.tfvars         # East US production
└── scripts/
    ├── deploy.sh                    # Deployment wrapper script
    └── destroy.sh                   # Destruction wrapper script
```

### Deployment Process

```bash
# Deploy West Europe test environment
cd infrastructure/
terraform init -backend-config="key=westeu-test-1.tfstate"
terraform workspace select westeu-test-1 || terraform workspace new westeu-test-1
terraform plan -var-file="deployments/westeu-test-1.tfvars"
terraform apply -var-file="deployments/westeu-test-1.tfvars"

# Deploy East US production environment
terraform init -backend-config="key=eastus-prod-1.tfstate"
terraform workspace select eastus-prod-1 || terraform workspace new eastus-prod-1
terraform plan -var-file="deployments/eastus-prod-1.tfvars"
terraform apply -var-file="deployments/eastus-prod-1.tfvars"
```

### Backend State Management

Each deployment has its own state file in Azure Blob Storage:

```hcl
# backend.tf
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-complianceflow-terraform"
    storage_account_name = "stcfterraform"
    container_name       = "tfstate"
    # key is specified at init time: {deployment-name}.tfstate
  }
}
```

State files:
- `westeu-test-1.tfstate`
- `westeu-stg-1.tfstate`
- `westeu-prod-1.tfstate`
- `eastus-prod-1.tfstate`

---

## 🌍 Region Mapping

### Azure Region Codes

| Region Code | Azure Region Name | Purpose |
|-------------|-------------------|---------|
| `westeu` | West Europe (Netherlands) | Primary EU region |
| `northeu` | North Europe (Ireland) | Secondary EU region |
| `eastus` | East US (Virginia) | Primary US region |
| `westus` | West US (California) | Secondary US region |
| `uksouth` | UK South (London) | UK data residency |
| `australiaeast` | Australia East (Sydney) | APAC region |

### Region Selection Criteria

- **Data residency**: Legal requirements (GDPR, US data sovereignty)
- **Latency**: Geographic proximity to users
- **Cost**: Regional pricing differences
- **Availability zones**: Multi-AZ support for HA
- **Service availability**: Some Azure services have regional limitations

---

## 🏷️ Resource Naming Convention

### Format
```
{resource-type}-{app-name}-{deployment-name}-{descriptor}
```

### Examples

| Resource Type | Example |
|---------------|---------|
| Resource Group | `rg-cf-westeu-prod-1` |
| Virtual Network | `vnet-cf-westeu-prod-1` |
| Subnet | `snet-cf-westeu-prod-1-db` |
| PostgreSQL Server | `psql-cf-westeu-prod-1` |
| Redis Cache | `redis-cf-westeu-prod-1` |
| Key Vault | `kv-cf-westeu-prod-1-ab12` (suffix for global uniqueness) |
| Storage Account | `stcfwesteuprod1` (alphanumeric only) |
| Container Registry | `acrcfwesteuprod1` (alphanumeric only) |
| Log Analytics | `log-cf-westeu-prod-1` |
| App Insights | `appi-cf-westeu-prod-1` |

### Naming Constraints

- **Key Vault**: 3-24 chars, alphanumeric + hyphens, globally unique
- **Storage Account**: 3-24 chars, lowercase alphanumeric only, globally unique
- **Container Registry**: 5-50 chars, alphanumeric only, globally unique

---

## 🗄️ Database Architecture

### Three-Tier Database Model

ComplianceFlow uses a **three-tier database strategy** to balance cost, performance, and tenant isolation:

#### **Tier 1: Global Databases** (per environment)
**Purpose**: Shared master data accessible across all regions

```
global-dev:
  └─ PostgreSQL Flexible Server: psql-cf-global-dev
     ├─ tenant_registry DB → Customer identifiers, onboarding data
     ├─ master_data DB → Securities, issuers, reference data
     └─ global_config DB → Platform-wide configuration
```

**Characteristics**:
- Single server per environment (global-dev, global-stg, global-prod)
- Geo-replicated read replicas (future)
- Global APIs expose this data to regional instances

#### **Tier 2: Regional Service Databases** (per deployment)
**Purpose**: Microservice metadata and configuration

```
westeu-dev-1:
  └─ PostgreSQL Flexible Server: psql-cf-westeu-dev-1
     ├─ user_service DB → User accounts, roles, permissions
     ├─ form_service DB → Form definitions, versions
     ├─ rule_service DB → Rule definitions, versions
     ├─ declaration_service DB → (Tenant-specific declarations via RLS)
     ├─ review_service DB → (Tenant-specific reviews via RLS)
     ├─ case_service DB → (Tenant-specific cases via RLS)
     ├─ notification_service DB → Templates, logs
     └─ analytics_service DB → (Tenant-specific aggregations via RLS)
```

**Characteristics**:
- One server per regional deployment
- Multiple databases (one per microservice)
- **Row-Level Security (RLS)** for tenant isolation
- RLS must be **automatic** in all queries (baked into templates)

#### **Tier 3: Per-Tenant Databases** (Future - Phase 2)
**Purpose**: Complete tenant isolation with BYOK encryption

```
westeu-prod-1:
  ├─ PostgreSQL Server: psql-cf-westeu-prod-1-tenant-acme
  │  ├─ Customer-managed encryption key (BYOK)
  │  ├─ user_data DB
  │  ├─ declaration_data DB
  │  └─ ... (all tenant-specific data)
  │
  └─ PostgreSQL Server: psql-cf-westeu-prod-1-tenant-contoso
     ├─ Customer-managed encryption key (BYOK)
     └─ ... (all tenant-specific data)
```

**Characteristics**:
- **NOT IMPLEMENTED IN MVP** - planned for Phase 2
- One server per tenant (for enterprise customers)
- Bring-Your-Own-Key (BYOK) encryption
- Complete data isolation
- Automatic provisioning on tenant onboarding

### Current Strategy: Row-Level Security (RLS)

**Phase 1 (MVP/Current)**:
- Use **Tier 1 + Tier 2 only**
- Tenant data isolated via PostgreSQL Row-Level Security (RLS)
- Every table has `tenant_id` column
- RLS policies enforce `tenant_id = current_tenant_id()`
- **CRITICAL**: RLS must be **automatic** in all queries
  - Built into ORM/query templates
  - No developer can accidentally query across tenants
  - All queries filtered by `tenant_id` by default

**Phase 2 (Future/Scale)**:
- Migrate high-value customers to **Tier 3** (per-tenant databases)
- Enable BYOK encryption
- Document migration path: RLS → Dedicated Server
- Triggered by: Customer demand, compliance requirements, or revenue threshold

### RLS Implementation Requirements

**Every service MUST**:
1. Include `tenant_id` in all multi-tenant tables
2. Set `tenant_id` from JWT token context automatically
3. Apply RLS policies that filter by `tenant_id`
4. Prevent any query from accessing other tenant data
5. Test cross-tenant isolation in integration tests
6. Document RLS policies in service README

**SQLAlchemy Example** (baked into templates):
```python
# Automatic tenant filtering via session
class TenantSession:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        
    def query(self, model):
        q = super().query(model)
        if hasattr(model, 'tenant_id'):
            q = q.filter(model.tenant_id == self.tenant_id)
        return q
```

---

## 🌐 Global Services Architecture

### Global Deployment Components

Each global deployment (`global-dev`, `global-stg`, `global-prod`) includes:

#### **1. Tenant Registry Service** (NEW)
**Purpose**: Central source of truth for all tenants

**Responsibilities**:
- Customer onboarding workflow
- Tenant identifier management
- Tenant-to-region routing
- Subscription/billing status
- Tenant configuration metadata

**APIs**:
- `POST /tenants` - Create new tenant (onboarding)
- `GET /tenants/{id}` - Retrieve tenant details
- `PUT /tenants/{id}` - Update tenant configuration
- `GET /tenants/{id}/regions` - Get tenant's regional deployments

**Events Published** (to global Kafka):
- `tenant.onboarded` → Triggers regional provisioning
- `tenant.updated` → Propagates configuration changes
- `tenant.suspended` → Disables tenant in all regions

#### **2. Master Data Service** (NEW)
**Purpose**: Shared reference data across all regions

**Responsibilities**:
- Financial securities/issuers lookup
- Regulatory body information
- Country/region codes
- Industry classification codes
- Other reference data

**APIs**:
- `GET /securities/{isin}` - Lookup security by ISIN
- `GET /issuers/{id}` - Get issuer information
- `POST /securities` - Add new security (admin only)

**Events Published** (to global Kafka):
- `masterdata.security.created`
- `masterdata.security.updated`
- `masterdata.issuer.updated`

#### **3. File Ingestion/Routing Service** (NEW)
**Purpose**: Global file upload and routing to correct region

**Responsibilities**:
- Accept file uploads
- Validate file formats
- Route to tenant's regional instance
- Track ingestion status

**APIs**:
- `POST /ingest/files` - Upload file
- `GET /ingest/status/{id}` - Check ingestion status

**Events Published** (to global Kafka):
- `file.uploaded` → Regional services process

#### **4. Global API Gateway**
**Purpose**: Single entry point for all APIs

**Responsibilities**:
- Route to global services (tenant registry, master data)
- Route to regional services (based on tenant → region mapping)
- Rate limiting
- Authentication/authorization
- API versioning

---

## 📡 Event Architecture: Global Kafka

### Single Global Kafka Per Layer

Each environment has **one global Kafka** that all regional instances subscribe to:

```
global-dev:
  └─ Azure Event Hubs (Kafka-compatible)
     ├─ tenant-events (partitions: 4)
     ├─ masterdata-events (partitions: 2)
     └─ file-ingestion-events (partitions: 4)

westeu-dev-1 services → Subscribe to global-dev Kafka
eastus-dev-1 services → Subscribe to global-dev Kafka
```

### Rationale: Single Global Kafka
- ✅ **Simpler failure modes**: One source to manage, not N regional Kafkas
- ✅ **Single source of truth**: All events originate from one place
- ✅ **Easier debugging**: Centralized event log
- ✅ **Cost**: Higher than regional, but cleaner architecture
- ⚠️ **Network**: More cross-region traffic, but acceptable

### Event Flow Example: Tenant Onboarding

```
1. Platform Support calls: POST global-dev/tenants
   └─ Tenant Registry creates tenant in global DB
   
2. Tenant Registry publishes: tenant.onboarded event → global-dev Kafka
   
3. Regional services consume from global-dev Kafka:
   ├─ westeu-dev-1 User Service → Creates regional user data structures
   ├─ westeu-dev-1 Form Service → Initializes default forms
   └─ westeu-dev-1 Rule Service → Initializes default rules
   
4. Regional services publish completion: tenant.provisioned.{region} → global-dev Kafka
   
5. Tenant Registry marks tenant as ready in all regions
```

### Regional vs Global Events

**Global Kafka** (from global-dev):
- `tenant.*` - Tenant lifecycle events
- `masterdata.*` - Reference data changes
- `file.ingested` - File routing events

**Regional Kafka** (optional, from westeu-dev-1):
- `user.*` - User actions (regional)
- `declaration.*` - Declaration lifecycle (regional)
- `review.*` - Review workflow (regional)

**Decision**: For MVP, **global Kafka only**. Add regional Kafka if performance requires it.

---

## 🔄 VNet Peering (Future)

### Peering Scenarios

1. **Cross-instance in same region** (e.g., westeu-prod-1 ↔ westeu-prod-2)
   - Use case: Blue/green traffic migration
   - CIDR: Adjacent /16 blocks (10.30.0.0/16 ↔ 10.31.0.0/16)

2. **Cross-region** (e.g., westeu-prod-1 ↔ eastus-prod-1)
   - Use case: Disaster recovery, data replication
   - CIDR: Non-overlapping /16 blocks

### Peering Configuration (Future Story)

```hcl
# Example: Peer westeu-prod-1 with westeu-prod-2
resource "azurerm_virtual_network_peering" "prod1_to_prod2" {
  name                      = "peer-westeu-prod-1-to-prod-2"
  resource_group_name       = azurerm_resource_group.main.name
  virtual_network_name      = module.networking.vnet_name
  remote_virtual_network_id = data.azurerm_virtual_network.prod2.id
  allow_forwarded_traffic   = true
  allow_gateway_transit     = false
}
```

---

## 📊 Cost Management

### Ephemeral Infrastructure Strategy

**Current Phase (Development)**:
- Infrastructure is **ephemeral** - can be torn down and re-deployed on demand
- Minimizes costs during long development periods
- All infrastructure defined in Terraform (Infrastructure as Code)
- State files retained, resources destroyed

**Future Phase (Production)**:
- Infrastructure becomes **persistent** when project goes live
- Continuous operation for paying customers
- Standard backup and DR procedures

### Tear-Down Strategy

**Order of Destruction** (to minimize cost, preserve data):
1. Regional instances first (`westeu-dev-1`, `eastus-dev-1`)
2. Global instances last (`global-dev`)
3. Terraform state files: **KEEP** (enables fast re-deployment)

**What to Destroy**:
- ✅ Container Apps (compute)
- ✅ PostgreSQL servers (after exporting seed data)
- ✅ Redis cache
- ✅ Event Hubs
- ✅ Virtual Networks
- ⚠️ Storage Accounts (after backing up critical data)
- ⚠️ Key Vault (soft-delete protects secrets)

**What to Keep**:
- ✅ Terraform state files (in Azure Blob Storage)
- ✅ GitHub repository (code, configurations)
- ✅ Seed data scripts (for rapid re-deployment)
- ✅ Documentation

**Re-Deployment Time**: ~15-30 minutes per deployment (Infrastructure as Code)

### Data Seeding Requirements

**Every service MUST have**:
1. Seed data script for development
2. Migration script for schema updates
3. Export/import functionality for test data
4. Documentation of seed data structure

**Seed data includes**:
- Sample tenants (Acme Corp, Contoso, etc.)
- Sample users with various roles
- Sample form definitions
- Sample rule configurations
- Sample declarations for testing

**Added to**:
- Each service PRD (new requirement)
- TASKLIST.md (implementation checkpoint)
- Service README (operation guide)

### Per-Deployment Budgets

Each deployment has dedicated cost tracking:

| Deployment | Monthly Budget (USD) | Alert Thresholds | Notes |
|------------|---------------------|------------------|-------|
| `global-dev` | $150 | 50%, 80%, 100% | Tear down last |
| `westeu-dev-1` | $200 | 50%, 80%, 100% | Tear down first |
| `global-stg` | $300 | 50%, 80%, 100% | Future |
| `westeu-stg-1` | $500 | 50%, 80%, 100% | Future |
| `global-prod` | $1,000 | 50%, 80%, 100% | Future - persistent |
| `westeu-prod-1` | $5,000 | 50%, 80%, 100% | Future - persistent |
| `westeu-prod-2` | $5,000 | 50%, 80%, 100% | Future - persistent |
| `eastus-prod-1` | $5,000 | 50%, 80%, 100% | Future - persistent |

### Cost Allocation Tags

All resources tagged with:
```hcl
tags = {
  Deployment    = "westeu-dev-1"
  Environment   = "dev"
  Region        = "westeu"
  Instance      = "1"
  Application   = "ComplianceFlow"
  ManagedBy     = "Terraform"
  CostCenter    = "Platform"
  Owner         = "DevOps"
  Ephemeral     = "true"  # For dev/stg, false for prod
}
```

---

## 🔐 Security & Isolation

### Network Isolation

- **No default cross-deployment communication**
- **VNet peering required** for inter-deployment traffic
- **NSG rules** restrict traffic within deployment
- **Private endpoints** for all Azure PaaS services

### Data Isolation

- **Separate databases** per deployment
- **Row-Level Security (RLS)** for tenant data isolation
- **Separate Key Vaults** per deployment
- **Separate storage accounts** per deployment
- **Tenant data** isolated within each deployment via RLS

### Identity & Access

- **Separate service principals** for CI/CD per deployment
- **RBAC scoped** to deployment resource group
- **Managed identities** scoped to deployment
- **No cross-deployment access** by default

---

## 🛡️ Compliance & Security Requirements

### Target Compliance Frameworks

ComplianceFlow infrastructure must support the following compliance requirements:

#### **SOC 2 Type II**
**System and Organization Controls for Service Organizations**

**Requirements**:
- ✅ Security: Access controls, encryption, monitoring
- ✅ Availability: 99.9% uptime SLA, redundancy, disaster recovery
- ✅ Processing Integrity: Data validation, error handling
- ✅ Confidentiality: Encryption at rest and in transit
- ✅ Privacy: Data retention policies, GDPR compliance

**Infrastructure Support**:
- Audit logging for all infrastructure changes (Terraform)
- Azure Monitor + Application Insights for all services
- Automated backup and retention policies
- Encryption at rest (Azure Storage, PostgreSQL)
- Encryption in transit (TLS 1.2+)
- Access control via RBAC and Azure AD

#### **ISO 27001**
**Information Security Management System (ISMS)**

**Requirements**:
- ✅ Risk assessment and treatment
- ✅ Asset management (infrastructure inventory)
- ✅ Access control (RBAC, least privilege)
- ✅ Cryptography (encryption standards)
- ✅ Physical and environmental security (Azure datacenters)
- ✅ Operations security (change management, patching)
- ✅ Communications security (network segmentation, TLS)
- ✅ System acquisition, development, and maintenance
- ✅ Supplier relationships (Azure, third-party services)
- ✅ Incident management (monitoring, alerting, response)
- ✅ Business continuity (backup, DR, RTO/RPO)
- ✅ Compliance (audit logs, evidence collection)

**Infrastructure Support**:
- Infrastructure as Code (Terraform) for audit trail
- Network Security Groups for segmentation
- Private endpoints for all services
- Automated patching via Azure
- Disaster recovery plan (documented, tested)
- Incident response runbooks

#### **ISO 9001**
**Quality Management System**

**Requirements**:
- ✅ Documentation of processes and procedures
- ✅ Change management procedures
- ✅ Quality assurance testing
- ✅ Continuous improvement
- ✅ Customer satisfaction measurement

**Infrastructure Support**:
- Documented deployment procedures
- Change approval workflow (GitHub PRs)
- Automated testing (CI/CD pipelines)
- Post-incident reviews (blameless postmortems)
- SLA monitoring and reporting

#### **GDPR (General Data Protection Regulation)**
**EU data protection and privacy**

**Requirements**:
- ✅ Data residency (EU data in EU regions)
- ✅ Right to be forgotten (data deletion)
- ✅ Data portability (export capabilities)
- ✅ Breach notification (within 72 hours)
- ✅ Data protection by design and default
- ✅ Data Processing Agreements with processors

**Infrastructure Support**:
- Global deployments in West Europe (GDPR compliance)
- Regional deployments respect data residency
- Tenant data deletion workflows
- Data export APIs
- Azure GDPR commitments (Microsoft as processor)
- Audit logging for data access

### Disaster Recovery & Business Continuity

**RTO/RPO Targets** (to be defined per environment):

| Deployment | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) |
|------------|-------------------------------|--------------------------------|
| `global-dev` | TBD - Not critical | TBD - Daily backups acceptable |
| `global-prod` | < 4 hours | < 15 minutes |
| `westeu-prod-1` | < 2 hours | < 5 minutes |

**DR Requirements** (for production):
1. **Automated Backups**:
   - PostgreSQL: Point-in-time restore, geo-redundant backups
   - Storage Accounts: Geo-redundant storage (GRS)
   - Configuration: Terraform state backup
   
2. **Cross-Region Failover**:
   - Global services replicated to secondary region
   - Regional instances can fail over to alternate region
   - DNS-based traffic routing
   
3. **DR Testing**:
   - Quarterly DR drills
   - Documented runbooks
   - Automated recovery procedures

**Phase 1 (MVP/Current)**:
- ⚠️ **NO DR** - Ephemeral infrastructure, cost optimization
- ⚠️ Backups: Terraform state only, no data retention
- ⚠️ Acceptable for development phase

**Phase 2 (Production)**:
- ✅ Full DR implementation
- ✅ Regular testing
- ✅ SLA commitments

### Security Audit Requirements

**Infrastructure must support**:
1. **Audit Log Retention**: 7 years minimum
2. **Change Tracking**: All infrastructure changes logged
3. **Access Logs**: All data access logged
4. **Compliance Reports**: Automated evidence collection
5. **Penetration Testing**: Infrastructure supports annual pen tests
6. **Vulnerability Scanning**: Automated scanning in CI/CD

**Evidence Collection**:
- Terraform state history (infrastructure changes)
- Azure Activity Logs (resource modifications)
- Application Insights (application behavior)
- Key Vault access logs (secret access)
- PostgreSQL audit logs (data access)
- NSG flow logs (network traffic)

### BYOK (Bring Your Own Key) Support

**Phase 2 (Future)**:
- Customer-managed encryption keys
- Per-tenant database encryption with customer keys
- Azure Key Vault integration for customer keys
- Key rotation procedures
- Compliance with customer key management policies

**Requirements**:
- Customer provides encryption key
- Customer controls key lifecycle
- Platform cannot access data without customer key
- Automated key rotation notifications

---

## 🚀 Deployment Workflow

### Phase 1: MVP (Current Priority)

**Goal**: Prove architecture works with global + regional deployment

#### **Step 1: Deploy Global Dev** (Week 1)
```bash
# Deploy global-dev infrastructure
./scripts/deploy.sh global-dev
```

**Includes**:
- ✅ Tenant Registry Service (NEW)
- ✅ Master Data Service (NEW)
- ✅ File Ingestion Service (NEW)
- ✅ Global API Gateway
- ✅ Global Kafka (Azure Event Hubs)
- ✅ Global PostgreSQL (tenant_registry, master_data, global_config DBs)

#### **Step 2: Deploy Regional Dev** (Week 1)
```bash
# Deploy westeu-dev-1 infrastructure
./scripts/deploy.sh westeu-dev-1
```

**Includes**:
- ✅ All 8 microservices (User, Declaration, Form, Rule, Review, Case, Notification, Analytics)
- ✅ Regional PostgreSQL (8 databases with RLS)
- ✅ Redis cache
- ✅ Container Apps environment
- ✅ Storage Account
- ✅ Monitoring (Application Insights, Log Analytics)

#### **Step 3: Integrate Global ↔ Regional** (Week 2)
- ✅ Regional services subscribe to global-dev Kafka
- ✅ Test tenant onboarding flow
- ✅ Test master data propagation
- ✅ Validate end-to-end workflows

#### **Step 4: Build Out Features** (Weeks 3-12)
- User Service
- Declaration Service
- Form Service
- Rule Engine
- Review Service
- Case Service
- Notification Service
- Analytics Service
- Frontend

**LOTS TO BUILD** - Focus on proving architecture before scaling

#### **Step 5: Tear Down & Re-Deploy Test** (Week 13)
- ✅ Destroy all resources
- ✅ Test rapid re-deployment from Terraform
- ✅ Validate seed data procedures
- ✅ Measure re-deployment time

### Phase 2: Multi-Environment (Future)

When features are complete:

1. **Deploy `global-stg` + `westeu-stg-1`**
   - Staging environment for UAT
   - Pre-production testing

2. **Deploy `global-prod` + `westeu-prod-1`**
   - Production environment
   - Full DR implementation
   - Persistent infrastructure (no tear-down)

### Phase 3: Scale & DR (Future)

When project becomes "real":

1. **Deploy `eastus-prod-1`** (US data residency)
2. **Deploy `westeu-prod-2`** (Customer isolation or scaling)
3. **Enable VNet peering** (cross-region communication)
4. **Implement full DR** (quarterly testing)

---

## 📋 Terraform Variables

### Deployment-Specific Variables

Each `.tfvars` file includes:

```hcl
# deployments/westeu-prod-1.tfvars

# Deployment identification
region_code = "westeu"
environment = "prod"
instance    = 1

# Azure region
location = "West Europe"

# Network configuration (from CIDR allocation table)
vnet_cidr = "10.30.0.0/16"

# Resource sizing (prod tier)
database_sku_name               = "GP_Standard_D4s_v3"
database_storage_mb            = 131072
database_backup_retention_days = 35
database_geo_redundant_backup  = true

redis_sku_name  = "Premium"
redis_family    = "P"
redis_capacity  = 1

# Feature flags
enable_api_management  = true  # Only in production
enable_ddos_protection = true  # Only in production
enable_backup          = true

# Cost management
cost_center = "Production"
owner       = "Platform Team"
```

---

## 🎯 Success Criteria

### Infrastructure

- ✅ **Single deployment** (`westeu-test-1`) fully functional
- ✅ All modules **reusable** across deployments
- ✅ **CIDR allocation** prevents conflicts
- ✅ **Naming convention** allows easy identification
- ✅ **Cost tracking** per deployment
- ✅ **Terraform state** isolated per deployment

### Application

- ✅ All 8 microservices deployed to `westeu-test-1`
- ✅ End-to-end user flows working
- ✅ Integration tests passing
- ✅ CI/CD pipeline deploying successfully

### Documentation

- ✅ Deployment guide for each environment
- ✅ CIDR allocation documented
- ✅ Naming conventions documented
- ✅ Runbooks for common operations

---

## 📖 Related Documentation

- `PRD_ComplianceFlow.md` - Overall product requirements
- `ECS-7_Infrastructure_Stories.md` - Infrastructure user stories
- `Tech_Stack_Definition.md` - Technology choices
- `PROJECT_STRUCTURE.md` - Project layout

---

## 🔄 Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-06 | Initial architecture definition with multi-region support |

---

**Last Updated**: October 6, 2025  
**Next Review**: After `westeu-test-1` deployment validation

