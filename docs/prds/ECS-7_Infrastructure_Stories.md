# ECS-7: Infrastructure Setup - User Stories
## Story Breakdown for Sprint 1

**⚠️ ARCHITECTURE UPDATE (Oct 6, 2025):**  
Infrastructure now supports **multi-region, multi-instance deployments**. Each deployment (e.g., `westeu-test-1`, `westeu-prod-1`, `eastus-prod-1`) is completely isolated with its own state file, CIDR block, and resources. See `docs/Infrastructure_Architecture.md` for full details.

**MVP Priority**: Focus on delivering **one complete deployment** (`westeu-test-1`) with all services working end-to-end before building additional environments.

---

## Story 0 (ECS-46): Prepare Azure Subscription, Budgets, and Policies

**Story Points**: 3  
**Priority**: P0 (Prerequisite for Terraform)  
**Jira**: ECS-46

### User Story
As a **Platform Admin/DevOps engineer**, I want **an Azure subscription prepared with budgets and guardrails**, so that **Terraform work is cost-controlled and compliant from day one**.

### Acceptance Criteria

#### Scenario 1: Subscription and Resource Groups Ready
```gherkin
Given I have Azure tenant access
When I prepare the subscription for ComplianceFlow
Then a subscription is selected/created for dev
And resource groups exist: rg-complianceflow-dev, rg-complianceflow-stg (optional now), rg-complianceflow-prod (placeholder)
And required providers (Microsoft.*) are registered as needed
```

#### Scenario 2: Budgets and Alerts Configured
```gherkin
Given the subscription and RGs exist
When I configure budgets
Then monthly budgets are set with 50/80/100% alerts
And cost anomaly alerts are enabled
```

#### Scenario 3: Baseline Policies Applied (Dev)
```gherkin
Given the dev resource group exists
When I apply baseline policies
Then premium SKUs are denied in dev (except whitelisted)
And required tags (app, env, owner, costCenter) are enforced
And Log Analytics daily cap and retention are configured
```

#### Scenario 4: CI/CD Service Principal Ready
```gherkin
Given GitHub Actions will deploy resources
When I create a service principal
Then least-privilege roles are assigned (Reader on sub, Contributor scoped to RGs)
And credentials are stored securely in GitHub Secrets
```

### Definition of Done
- [ ] Subscription selected/created
- [ ] RGs created for dev (and placeholders for stg/prod)
- [ ] Budgets and anomaly alerts enabled
- [ ] Dev policies/tagging enforced
- [ ] Service principal created with least privilege
- [ ] GitHub secrets populated
- [ ] Documentation updated (Setup_Guide.md)


**Epic**: ECS-7 - Infrastructure Setup  
**Total Stories**: 11  
**Estimated Story Points**: 60-65  
**Sprint Duration**: 1 week (5 working days)

---

## Story 1 (ECS-18): Setup Terraform Backend for Multi-Deployment State Management

**Story Points**: 5 (increased from 3 due to multi-deployment support)  
**Priority**: P0 (Must be first after ECS-46)  
**Jira**: ECS-18

### User Story
As a **DevOps engineer**, I want **Terraform state stored securely in Azure with support for multiple independent deployments**, so that **we can deploy multiple isolated environments (westeu-test-1, westeu-prod-1, eastus-prod-1, etc.) with separate state files**.

### Context
Terraform requires a remote backend to store state files for collaborative infrastructure management. Azure Blob Storage provides secure, versioned storage for Terraform state with locking capabilities to prevent concurrent modifications.

**Multi-Deployment Architecture**: Each deployment (e.g., `westeu-test-1`, `westeu-prod-1`) has its own isolated state file to enable independent deployments, prevent state conflicts, and allow parallel infrastructure work.

### Acceptance Criteria

#### Scenario 1: Azure Storage Account Created
```gherkin
Given I have an Azure subscription
When I run the backend setup script
Then an Azure Storage Account is created with naming convention "stcfterraform"
And a blob container named "tfstate" is created
And versioning is enabled on the container
And encryption at rest is enabled
And lifecycle management is configured for old versions
```

#### Scenario 2: Multi-Deployment Backend Configuration
```gherkin
Given the Azure Storage Account exists
When I initialize Terraform for deployment "westeu-test-1"
Then Terraform successfully connects to the remote backend
And the state file is stored as "westeu-test-1.tfstate"
And state locking is enabled via Azure Blob lease
And workspace "westeu-test-1" is created or selected
```

#### Scenario 3: Parallel Deployment Support
```gherkin
Given multiple deployments exist
When I deploy "westeu-test-1" and "westeu-prod-1" simultaneously
Then each deployment uses its own isolated state file
And state files are: "westeu-test-1.tfstate" and "westeu-prod-1.tfstate"
And locking prevents conflicts within each deployment
And deployments do not interfere with each other
```

#### Scenario 4: Access Control Configured
```gherkin
Given the Terraform backend is configured
When multiple developers attempt to apply changes to the same deployment
Then only one developer can hold the state lock for that deployment at a time
And appropriate RBAC permissions are set on the storage account
And service principal has necessary permissions
And audit logging captures all state access
```

### Technical Implementation Notes

* **Files**: 
  * `infrastructure/backend.tf` - Dynamic backend configuration
  * `infrastructure/locals.tf` - Deployment identification logic
  * `scripts/deploy.sh` - Deployment wrapper script with backend-config
  * `scripts/backend-setup.sh` - One-time backend setup script
  * `docs/Infrastructure_Architecture.md` - Multi-deployment guide
  
* **Azure Resources**:
  * Storage Account: `stcfterraform` (global name, deployment-agnostic)
  * Container: `tfstate`
  * Resource Group: `rg-complianceflow-terraform`
  
* **State File Naming**:
  * Format: `{region-code}-{environment}-{instance}.tfstate`
  * Examples:
    * `westeu-test-1.tfstate`
    * `westeu-stg-1.tfstate`
    * `westeu-prod-1.tfstate`
    * `eastus-prod-1.tfstate`

* **Terraform Backend Config**:
```hcl
# infrastructure/backend.tf
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-complianceflow-terraform"
    storage_account_name = "stcfterraform"
    container_name       = "tfstate"
    # key is specified at init time via -backend-config
    # Example: terraform init -backend-config="key=westeu-test-1.tfstate"
  }
}
```

* **Deployment Script Example**:
```bash
#!/bin/bash
# scripts/deploy.sh

DEPLOYMENT_NAME=$1  # e.g., westeu-test-1

cd infrastructure/

# Initialize with deployment-specific state file
terraform init -backend-config="key=${DEPLOYMENT_NAME}.tfstate"

# Select or create workspace
terraform workspace select ${DEPLOYMENT_NAME} || terraform workspace new ${DEPLOYMENT_NAME}

# Plan and apply with deployment-specific tfvars
terraform plan -var-file="deployments/${DEPLOYMENT_NAME}.tfvars"
terraform apply -var-file="deployments/${DEPLOYMENT_NAME}.tfvars"
```

### Definition of Done
* [ ] Azure Storage Account created for Terraform state
* [ ] Blob container with versioning and lifecycle management enabled
* [ ] Backend configuration supports dynamic state file keys
* [ ] Deployment script handles backend initialization
* [ ] Test with at least 2 deployments (`westeu-test-1` and `westeu-prod-1` simulation)
* [ ] State locking works (tested with concurrent operations on same deployment)
* [ ] Parallel deployments work (tested with different deployments)
* [ ] RBAC permissions configured
* [ ] Documentation includes:
  * [ ] Multi-deployment architecture explanation
  * [ ] Deployment script usage
  * [ ] State file naming convention
  * [ ] How to list all deployments
  * [ ] How to destroy a specific deployment
* [ ] Storage redundancy configured (LRS for dev, GRS for prod consideration)

---

## Story 2 (ECS-19): Create Terraform Networking Module with Multi-Deployment CIDR Support

**Story Points**: 8 (increased from 5 due to CIDR allocation and multi-deployment support)  
**Priority**: P0 (Blocks all services)  
**Jira**: ECS-19

### User Story
As a **DevOps engineer**, I want **network infrastructure defined in Terraform with deployment-specific CIDR allocation**, so that **each deployment has isolated networks and we can enable VNet peering without CIDR conflicts**.

### Context
Azure Virtual Network provides network isolation for the ComplianceFlow platform. We need subnets for different tiers (database, application, management) with Network Security Groups (NSGs) to control traffic flow.

**Multi-Deployment CIDR Strategy**: Each deployment receives a unique /16 CIDR block from a pre-allocated range. This prevents CIDR conflicts and enables future VNet peering for cross-region communication. See `docs/Infrastructure_Architecture.md` for the full CIDR allocation table.

### Acceptance Criteria

#### Scenario 1: Deployment-Specific Virtual Network Created
```gherkin
Given Terraform is initialized for deployment "westeu-test-1"
When I apply the networking module
Then a Virtual Network is created with CIDR 10.10.0.0/16 (from CIDR allocation table)
And the VNet name is "vnet-cf-westeu-test-1"
And the VNet is created in Azure region "West Europe"
And the VNet is tagged with deployment, environment, and region information
```

#### Scenario 2: Consistent Subnets Configured Within Deployment CIDR
```gherkin
Given the Virtual Network exists with CIDR 10.10.0.0/16
When the networking module is applied
Then a container apps subnet (10.10.1.0/24) is created
And a database subnet (10.10.2.0/24) is created
And a redis subnet (10.10.3.0/24) is created
And a storage subnet (10.10.4.0/24) is created
And a management subnet (10.10.10.0/24) is created
And each subnet is associated with appropriate NSGs
And subnet naming follows pattern "snet-cf-{deployment}-{tier}"
```

#### Scenario 3: Network Security Groups Applied
```gherkin
Given subnets are created
When NSG rules are applied
Then database subnet only allows traffic from container apps subnet on PostgreSQL port (5432)
And container apps subnet allows inbound HTTPS traffic (443) from internet
And redis subnet only allows traffic from container apps subnet on port 6379
And storage subnet only allows traffic via service endpoints
And management subnet only allows SSH/RDP from specific IP ranges
And all NSG rules follow priority numbering convention (100-199 for inbound, 1000+ for deny)
```

#### Scenario 4: Service Endpoints and Private DNS Zones
```gherkin
Given the networking infrastructure exists
When services require private connectivity
Then service endpoints are enabled for Microsoft.Storage on container apps and storage subnets
And service endpoints are enabled for Microsoft.KeyVault on container apps subnet
And service endpoints are enabled for Microsoft.Sql on database subnet
And private DNS zones are created for privatelink.postgres.database.azure.com
And private DNS zones are created for privatelink.blob.core.windows.net
And DNS zones are linked to the Virtual Network
```

#### Scenario 5: CIDR Allocation Validated
```gherkin
Given I am deploying multiple environments
When I review CIDR allocations
Then westeu-test-1 uses 10.10.0.0/16
And westeu-stg-1 uses 10.20.0.0/16
And westeu-prod-1 uses 10.30.0.0/16
And westeu-prod-2 uses 10.31.0.0/16 (adjacent for peering)
And eastus-prod-1 uses 10.40.0.0/16
And no CIDR blocks overlap
And all allocations are documented in Infrastructure_Architecture.md
```

#### Scenario 6: Network Monitoring and Diagnostics
```gherkin
Given the networking infrastructure is deployed
When monitoring is configured
Then NSG flow logs are enabled and sent to Log Analytics
And VNet diagnostic logs capture: VMProtectionAlerts, AllMetrics
And alerts are configured for: NSG rule hits (unusual traffic patterns)
And Network Watcher is enabled in the region
And connection monitor tracks connectivity between subnets
```

### Technical Implementation Notes

* **Files**: 
  * `infrastructure/modules/networking/main.tf`
  * `infrastructure/modules/networking/variables.tf`
  * `infrastructure/modules/networking/outputs.tf`
  * `infrastructure/locals.tf` - CIDR allocation map
  * `docs/Infrastructure_Architecture.md` - CIDR table

* **CIDR Allocation Map** (in locals.tf):
```hcl
locals {
  # Centralized CIDR allocation for all deployments
  cidr_allocations = {
    "westeu-test-1"  = "10.10.0.0/16"
    "westeu-stg-1"   = "10.20.0.0/16"
    "westeu-prod-1"  = "10.30.0.0/16"
    "westeu-prod-2"  = "10.31.0.0/16"
    "eastus-test-1"  = "10.11.0.0/16"
    "eastus-stg-1"   = "10.21.0.0/16"
    "eastus-prod-1"  = "10.40.0.0/16"
    "northeu-prod-1" = "10.50.0.0/16"
  }
  
  deployment_name = "${var.region_code}-${var.environment}-${var.instance}"
  vnet_cidr = local.cidr_allocations[local.deployment_name]
}
```

* **Azure Resources** (per deployment):
  * Virtual Network: `vnet-cf-{deployment}` (e.g., `vnet-cf-westeu-test-1`)
  * Subnets:
    * `snet-cf-{deployment}-containeraps` (10.X.1.0/24)
    * `snet-cf-{deployment}-db` (10.X.2.0/24)
    * `snet-cf-{deployment}-redis` (10.X.3.0/24)
    * `snet-cf-{deployment}-storage` (10.X.4.0/24)
    * `snet-cf-{deployment}-apim` (10.X.5.0/24) - prod only
    * `snet-cf-{deployment}-mgmt` (10.X.10.0/24)
  * NSGs: `nsg-cf-{deployment}-{tier}`
  * Private DNS Zones (shared across deployments in same subscription):
    * `privatelink.postgres.database.azure.com`
    * `privatelink.blob.core.windows.net`
    * `privatelink.vaultcore.azure.net`

* **Module Outputs**:
  * `vnet_id`
  * `vnet_name`
  * `vnet_cidr`
  * `container_apps_subnet_id`
  * `database_subnet_id`
  * `redis_subnet_id`
  * `storage_subnet_id`
  * `apim_subnet_id` (if enabled)
  * `management_subnet_id`
  * `database_private_dns_zone_id`
  * `storage_private_dns_zone_id`

### Definition of Done
* [ ] Terraform networking module created with deployment-aware CIDR allocation
* [ ] CIDR allocation map in locals.tf with all planned deployments
* [ ] Virtual Network deployed successfully with deployment-specific CIDR
* [ ] All 6 subnets created with appropriate CIDR blocks within deployment range (container apps, database, redis, storage, APIM for prod, management)
* [ ] NSG rules configured with priority numbering convention (100-199 inbound, 1000+ deny)
* [ ] **Service endpoints enabled** (Microsoft.Storage, Microsoft.KeyVault, Microsoft.Sql) with specific subnets documented
* [ ] **Private DNS zones created** and linked to VNet (postgres, blob, keyvault)
* [ ] Module outputs defined (vnet_id, all subnet IDs, private DNS zone IDs)
* [ ] **NSG flow logs enabled** and streaming to Log Analytics
* [ ] **Network Watcher enabled** in deployment region
* [ ] **VNet diagnostic logs** configured (VMProtectionAlerts, AllMetrics)
* [ ] Test deployment of at least westeu-test-1 successfully
* [ ] **Connectivity validated** between subnets per NSG rules
* [ ] Validate CIDR allocation doesn't overlap with other planned deployments
* [ ] **Multi-deployment tested**: Can deploy westeu-test-1 and westeu-prod-1 in parallel
* [ ] Documentation includes:
  * [ ] Network architecture diagram with subnet layout
  * [ ] CIDR allocation table (reference Infrastructure_Architecture.md)
  * [ ] Subnet layout diagram with CIDR blocks
  * [ ] NSG rule reference table with priorities
  * [ ] Service endpoint configuration per subnet
  * [ ] IPv6 explicitly noted as out of scope
  * [ ] VNet peering preparation notes (for future multi-region)
* [ ] Cross-reference Infrastructure_Architecture.md for complete CIDR allocations

---

## Story 3 (ECS-20): Create Terraform PostgreSQL Database Module

**Story Points**: 8  
**Priority**: P0 (Blocks all services)  
**Jira**: ECS-20

### User Story
As a **DevOps engineer**, I want **PostgreSQL databases provisioned via Terraform with deployment-specific configuration**, so that **each microservice has its own isolated database in each deployment with consistent, secure configuration**.

### Context
Each microservice requires its own PostgreSQL database for data isolation and independent scaling. Azure Database for PostgreSQL Flexible Server provides managed PostgreSQL with automated backups, high availability, and performance optimization.

**Multi-Deployment Architecture**: Each deployment (e.g., `westeu-test-1`, `westeu-prod-1`) gets its own PostgreSQL Flexible Server instance in the deployment-specific database subnet. This enables independent database scaling, backup policies, and cost management per deployment.

**Security**: All connections require SSL/TLS 1.2+, passwords are stored in Key Vault, and Row-Level Security (RLS) support is enabled for multi-tenant data isolation.

### Acceptance Criteria

#### Scenario 1: Deployment-Specific PostgreSQL Flexible Server Created
```gherkin
Given the networking module is deployed for "westeu-test-1"
When I apply the database module
Then an Azure Database for PostgreSQL Flexible Server is created
And the server name is "psql-cf-westeu-test-1"
And the server version is PostgreSQL 15 or higher
And the server is placed in the database subnet (10.10.2.0/24 for westeu-test-1)
And private endpoint connectivity is configured
And public network access is DISABLED
And the server is in Azure region "West Europe"
```

#### Scenario 2: SSL/TLS Security Enforced
```gherkin
Given the PostgreSQL server exists
When SSL configuration is applied
Then require_secure_transport is set to ON
And minimum TLS version is set to 1.2
And connection strings use sslmode=require
And SSL certificate verification is enabled
```

#### Scenario 3: Individual Databases Created with Deployment Naming
```gherkin
Given the PostgreSQL server exists
When the module provisions databases for deployment "westeu-test-1"
Then individual databases are created for each microservice
And database names follow convention: "complianceflow_<service>_<deployment>" (e.g., "complianceflow_user_westeu_test_1")
And appropriate user accounts are created for each service with least privilege
And passwords are generated securely and stored in Azure Key Vault
And each user can only access their specific database
```

#### Scenario 4: PostgreSQL Extensions Enabled
```gherkin
Given databases are created
When extensions are configured
Then pg_stat_statements extension is available (query performance monitoring)
And uuid-ossp extension is available (UUID generation)
And pg_trgm extension is available (text search)
And RLS (Row-Level Security) is enabled at database level for multi-tenancy
```

#### Scenario 5: Backup and High Availability
```gherkin
Given the PostgreSQL server is running
When backup configuration is applied
Then automated daily backups are enabled
And backup retention is set to 7 days minimum (30 days for production)
And point-in-time restore is enabled
And geo-redundant backup is configured for production deployments
And zone redundancy is enabled for production (HA within region)
```

#### Scenario 6: Performance and Connection Pooling
```gherkin
Given databases are created
When performance settings are applied
Then appropriate compute tier is selected (Burstable B1ms for test, General Purpose D2s_v3 for prod)
And built-in connection pooler (PgBouncer) is enabled
And query performance insights are enabled
And slow query logging is configured (queries > 1 second)
And storage auto-grow is enabled for production, disabled for test/dev
```

#### Scenario 7: Monitoring and Diagnostics
```gherkin
Given the PostgreSQL server is operational
When monitoring is configured
Then diagnostic settings send logs to Log Analytics workspace
And metrics include: CPU percentage, memory percentage, storage usage, active connections, replication lag
And alerts are configured for: connection failures, high CPU (>80% for 10 min), storage (>85%)
And slow query logs are streamed to Log Analytics
```

### Technical Implementation Notes

* **Files**: 
  * `infrastructure/modules/database/main.tf` - PostgreSQL server and databases
  * `infrastructure/modules/database/variables.tf` - Deployment-aware variables
  * `infrastructure/modules/database/outputs.tf` - Connection info, FQDNs
  * `infrastructure/modules/database/monitoring.tf` - Diagnostic settings and alerts
  * `infrastructure/modules/database/security.tf` - Private DNS, firewall rules, SSL config
  
* **Deployment-Specific Naming**:
  * Server: `psql-cf-{deployment}` (e.g., `psql-cf-westeu-test-1`)
  * Databases: `complianceflow_{service}_{deployment}` (e.g., `complianceflow_user_westeu_test_1`)
  * Uses deployment variables from locals.tf: `${var.region_code}-${var.environment}-${var.instance}`

* **Databases to Create** (per deployment):
  * `complianceflow_user_{deployment}`
  * `complianceflow_declaration_{deployment}`
  * `complianceflow_form_{deployment}`
  * `complianceflow_ruleengine_{deployment}`
  * `complianceflow_review_{deployment}`
  * `complianceflow_case_{deployment}`
  * `complianceflow_notification_{deployment}`
  * `complianceflow_analytics_{deployment}`

* **SKU Configuration**:
  * Test/Dev: Burstable B1ms (1 vCore, 2 GiB RAM) - ~$12-15/month, can be stopped when not in use
  * Staging: General Purpose D2s_v3 (2 vCores, 8 GiB RAM) - ~$120-150/month
  * Production: General Purpose D4s_v3 (4 vCores, 16 GiB RAM) with HA - ~$300-350/month

* **Connection Pooling**:
  * Azure PostgreSQL Flexible Server includes built-in PgBouncer
  * Mode: Transaction pooling
  * Max connections: 50 for B1ms, 100 for D2s_v3, 200 for D4s_v3

* **Terraform Outputs**:
```hcl
output "server_fqdn" {
  description = "Fully qualified domain name of PostgreSQL server"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "server_id" {
  description = "Azure resource ID of PostgreSQL server"
  value       = azurerm_postgresql_flexible_server.main.id
}

output "database_names" {
  description = "Map of service name to database name"
  value       = { 
    for k, v in azurerm_postgresql_flexible_server_database.databases : 
    k => v.name 
  }
}

output "connection_string_template" {
  description = "Template for service connection strings (password from Key Vault)"
  value       = "postgresql://{user}:{password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/{database}?sslmode=require&sslrootcert=system&connect_timeout=10"
  sensitive   = true
}

output "private_dns_zone_id" {
  description = "Private DNS zone ID for PostgreSQL"
  value       = azurerm_private_dns_zone.postgres.id
}
```

* **Security Configuration**:
  * Private endpoint only (no public access)
  * SSL/TLS 1.2+ enforced
  * Azure AD authentication enabled (emergency admin access)
  * Service accounts use strong passwords (32 characters, stored in Key Vault)
  * Firewall rules: Allow from database subnet only
  * RLS enabled for tenant data isolation (policies managed by service migrations)

* **Schema Management Boundary**:
  * **This module creates EMPTY databases only**
  * Schema migrations are handled by each service using Alembic
  * Services retrieve connection strings from Key Vault on startup
  * Each service's migration tool manages its own schema evolution

* **Row-Level Security (RLS)**:
  * RLS is enabled at the database level
  * Per `Infrastructure_Architecture.md`, Phase 1 uses RLS for tenant isolation in regional databases
  * Each service implements RLS policies via Alembic migrations
  * Pattern: `CREATE POLICY tenant_isolation ON table_name FOR ALL TO app_user USING (tenant_id = current_setting('app.current_tenant_id')::uuid)`

### Definition of Done
* [ ] Terraform database module created with deployment-aware naming
* [ ] PostgreSQL Flexible Server deployed in deployment-specific subnet
* [ ] All 8 microservice databases created with deployment suffix
* [ ] Database users provisioned with least privilege (schema-specific permissions)
* [ ] Passwords generated and stored in Key Vault
* [ ] **SSL/TLS enforcement verified** (require_secure_transport=ON, TLS 1.2+)
* [ ] **Required extensions enabled** (pg_stat_statements, uuid-ossp, pg_trgm)
* [ ] **RLS enabled** at database level
* [ ] Backup configuration validated (7-day retention for test, 30-day for prod)
* [ ] Zone redundancy enabled for production deployments
* [ ] Storage auto-grow configured per environment
* [ ] Built-in connection pooler (PgBouncer) enabled
* [ ] Connection from container apps subnet tested successfully
* [ ] **Monitoring configured**: Diagnostic logs to Log Analytics, alerts for CPU/storage/connections
* [ ] Performance monitoring enabled (query insights, slow query log)
* [ ] **Private DNS zone** created and linked to deployment VNet
* [ ] **Connection string template** documented with all security parameters
* [ ] **Multi-deployment tested**: Can deploy westeu-test-1 and westeu-prod-1 in parallel
* [ ] **Cost optimization documented**: Stop/start procedure for dev environments
* [ ] Documentation includes:
  * [ ] Connection string format with SSL parameters
  * [ ] Database naming convention
  * [ ] Extension usage guidelines
  * [ ] RLS policy examples
  * [ ] Backup/restore procedures
  * [ ] Cost comparison by SKU/environment

---

## Story 4: Create Terraform Redis Cache Module

**Story Points**: 5  
**Priority**: P0 (Blocks all services)

### User Story
As a **DevOps engineer**, I want **Redis cache provisioned via Terraform**, so that **services can cache data and manage sessions with high performance**.

### Context
Redis provides in-memory caching for session management, token validation, and frequently accessed data. Azure Cache for Redis offers managed Redis with automatic scaling and high availability.

### Acceptance Criteria

#### Scenario 1: Redis Cache Created
```gherkin
Given the networking module is deployed
When I apply the Redis module
Then an Azure Cache for Redis instance is created
And Redis version 6.0 or higher is deployed
And the cache is placed in the application subnet via private endpoint
And SSL/TLS connections are enforced
```

#### Scenario 2: Cache Configuration
```gherkin
Given the Redis cache exists
When configuration is applied
Then appropriate cache size is set (1 GB for dev, 6 GB for prod)
And maxmemory policy is set to "allkeys-lru"
And persistence is enabled (AOF for prod, RDB for dev)
And connection timeout is set to 30 seconds
```

#### Scenario 3: Access Control
```gherkin
Given the Redis cache is running
When access configuration is applied
Then access keys are stored in Azure Key Vault
And firewall rules restrict access to application subnet only
And Redis AUTH is enabled with strong password
And client certificates are configured for production
```

#### Scenario 4: High Availability for Production
```gherkin
Given the Redis cache is in production environment
When HA configuration is applied
Then clustering is enabled for Standard tier or higher
And zone redundancy is enabled
And automatic failover is configured
```

### Technical Implementation Notes

* **Files**: 
  * `infrastructure/modules/redis/main.tf`
  * `infrastructure/modules/redis/variables.tf`
  * `infrastructure/modules/redis/outputs.tf`
* **SKU Configuration**:
  * Dev: Basic C1 (1 GB, single node)
  * Prod: Standard C3 (6 GB, clustered with replica)
* **Use Cases**:
  * JWT token validation cache
  * User session storage
  * Form definition caching
  * Rule evaluation caching
  * Rate limiting

### Definition of Done
* [ ] Terraform Redis module created
* [ ] Azure Cache for Redis deployed
* [ ] SSL/TLS enforced
* [ ] Access keys stored in Key Vault
* [ ] Firewall rules configured
* [ ] Persistence enabled
* [ ] Connection tested from application subnet
* [ ] Monitoring and alerts configured
* [ ] Documentation includes connection examples

---

## Story 5: Create Terraform Kafka/Event Hub Module

**Story Points**: 8  
**Priority**: P0 (Blocks all services)

### User Story
As a **DevOps engineer**, I want **Kafka event streaming infrastructure provisioned via Terraform**, so that **microservices can communicate asynchronously through events**.

### Context
Event-driven architecture requires a message broker for service-to-service communication. Using Azure Event Hubs (Kafka-compatible) for cost efficiency while maintaining Kafka compatibility.

### Acceptance Criteria

#### Scenario 1: Event Hub Namespace Created
```gherkin
Given the networking module is deployed
When I apply the Kafka module
Then an Azure Event Hubs namespace is created
And the namespace tier is Standard (supports consumer groups)
And throughput units are set appropriately (1 for dev, auto-inflate enabled for prod)
And zone redundancy is enabled for production
```

#### Scenario 2: Event Hub Topics Created
```gherkin
Given the Event Hubs namespace exists
When topics are provisioned
Then `user-events` Event Hub is created (2 partitions)
And `declaration-events` Event Hub is created (4 partitions)
And `review-events` Event Hub is created (2 partitions)
And `case-events` Event Hub is created (2 partitions)
And `notification-events` Event Hub is created (4 partitions)
And `analytics-events` Event Hub is created (2 partitions)
```

#### Scenario 3: Consumer Groups Configured
```gherkin
Given Event Hubs are created
When consumer groups are provisioned
Then default consumer group exists for each Event Hub
And service-specific consumer groups are created
And consumer groups follow naming convention: `<service-name>-consumer`
```

#### Scenario 4: Access Policies and Security
```gherkin
Given Event Hubs are operational
When security configuration is applied
Then Shared Access Policies are created with least privilege
And connection strings are stored in Azure Key Vault
And network rules restrict access to application subnet
And managed identities are configured for services
```

### Technical Implementation Notes

* **Files**: 
  * `infrastructure/modules/messaging/main.tf`
  * `infrastructure/modules/messaging/variables.tf`
  * `infrastructure/modules/messaging/outputs.tf`
* **Event Hubs**:
  * `user-events` (2 partitions)
  * `declaration-events` (4 partitions)
  * `review-events` (2 partitions)
  * `case-events` (2 partitions)
  * `notification-events` (4 partitions)
  * `analytics-events` (2 partitions)
* **SKU Configuration**:
  * Dev: Standard tier, 1 TU
  * Prod: Standard tier, 2 TU with auto-inflate to 10

### Definition of Done
* [ ] Terraform messaging module created
* [ ] Event Hubs namespace deployed
* [ ] All 6 Event Hubs created with appropriate partition counts
* [ ] Consumer groups created for each service
* [ ] Access policies configured
* [ ] Connection strings stored in Key Vault
* [ ] Network rules configured
* [ ] Kafka compatibility tested
* [ ] Documentation includes event schema references

---

## Story 6: Create Terraform Key Vault Module

**Story Points**: 5  
**Priority**: P0 (Blocks all services - needed for secrets)

### User Story
As a **DevOps engineer**, I want **Azure Key Vault provisioned via Terraform**, so that **secrets, connection strings, and certificates are stored securely**.

### Context
Azure Key Vault provides centralized secrets management with access control, auditing, and encryption. All sensitive configuration must be stored in Key Vault, never in code or plain text configuration files.

### Acceptance Criteria

#### Scenario 1: Key Vault Created
```gherkin
Given the networking module is deployed
When I apply the Key Vault module
Then an Azure Key Vault is created
And the vault name follows convention: `kv-complianceflow-<env>-<random>`
And soft-delete is enabled with 90-day retention
And purge protection is enabled for production
And the vault is accessible via private endpoint
```

#### Scenario 2: Access Policies Configured
```gherkin
Given the Key Vault exists
When access policies are applied
Then service principals have appropriate secret read permissions
And admin user has secret management permissions
And managed identities for services are granted secret read access
And least privilege principle is enforced
```

#### Scenario 3: Initial Secrets Provisioned
```gherkin
Given the Key Vault is configured
When initial secrets are created
Then PostgreSQL connection strings are stored as secrets
And Redis access keys are stored as secrets
And Event Hubs connection strings are stored as secrets
And JWT signing keys are generated and stored
And Azure AD SSO client secrets are stored
And all secrets have appropriate metadata and tags
```

#### Scenario 4: Monitoring and Auditing
```gherkin
Given secrets are stored
When access occurs
Then all Key Vault operations are logged to Azure Monitor
And alerts are configured for suspicious access patterns
And secret expiration alerts are enabled
And compliance requirements for audit logs are met
```

### Technical Implementation Notes

* **Files**: 
  * `infrastructure/modules/security/main.tf`
  * `infrastructure/modules/security/variables.tf`
  * `infrastructure/modules/security/outputs.tf`
* **Secrets to Store**:
  * `postgresql-admin-password`
  * `postgresql-<service>-password` (8 services)
  * `redis-primary-key`
  * `eventhub-<event>-connection-string` (6 event types)
  * `jwt-signing-key`
  * `jwt-refresh-signing-key`
  * `azuread-client-secret`

### Definition of Done
* [ ] Terraform Key Vault module created
* [ ] Key Vault deployed with soft-delete and purge protection
* [ ] Access policies configured for all services
* [ ] Initial secrets created and populated
* [ ] Private endpoint configured
* [ ] Diagnostic logs enabled
* [ ] Secret expiration alerts configured
* [ ] Documentation includes secret naming conventions
* [ ] Example code for retrieving secrets from services

---

## Story 7: Create Terraform Monitoring and Observability Module

**Story Points**: 5  
**Priority**: P1 (Important but can be parallel)

### User Story
As a **DevOps engineer**, I want **monitoring and logging infrastructure provisioned via Terraform**, so that **we can observe system health, debug issues, and receive alerts**.

### Context
Azure Application Insights and Log Analytics provide comprehensive monitoring, logging, and alerting. All services should send logs, metrics, and traces to centralized monitoring infrastructure.

### Acceptance Criteria

#### Scenario 1: Log Analytics Workspace Created
```gherkin
Given infrastructure is being deployed
When I apply the monitoring module
Then a Log Analytics Workspace is created
And the workspace retention is set to 90 days
And the workspace is in the same region as services
And appropriate pricing tier is selected (Per GB for production)
```

#### Scenario 2: Application Insights Configured
```gherkin
Given the Log Analytics Workspace exists
When Application Insights is provisioned
Then an Application Insights resource is created
And it's linked to the Log Analytics Workspace
And instrumentation key is stored in Key Vault
And connection string is available for services
And sampling is configured appropriately (100% for dev, adaptive for prod)
```

#### Scenario 3: Diagnostic Settings Enabled
```gherkin
Given monitoring resources exist
When diagnostic settings are applied
Then all Azure resources send logs to Log Analytics
And PostgreSQL slow query logs are enabled
And Redis cache performance logs are enabled
And Event Hubs operational logs are enabled
And Key Vault audit logs are enabled
And NSG flow logs are enabled
```

#### Scenario 4: Alert Rules Configured
```gherkin
Given logs are flowing to monitoring
When alert rules are created
Then high error rate alerts (>5% errors in 5 minutes) are configured
And database connection failure alerts are enabled
And Event Hub throttling alerts are enabled
And Key Vault unauthorized access alerts are enabled
And high memory/CPU usage alerts (>80% for 10 minutes) are enabled
And alert action groups notify appropriate channels
```

### Technical Implementation Notes

* **Files**: 
  * `infrastructure/modules/monitoring/main.tf`
  * `infrastructure/modules/monitoring/variables.tf`
  * `infrastructure/modules/monitoring/outputs.tf`
* **Alert Rules**:
  * High error rate (>5% in 5 min)
  * Service unavailability
  * Database connection failures
  * High latency (>2s p95)
  * Resource exhaustion (CPU/Memory >80%)

### Definition of Done
* [ ] Terraform monitoring module created
* [ ] Log Analytics Workspace deployed
* [ ] Application Insights configured and linked
* [ ] Diagnostic settings enabled for all resources
* [ ] Alert rules created and tested
* [ ] Action groups configured with notification channels
* [ ] Instrumentation key stored in Key Vault
* [ ] Dashboard templates created
* [ ] Documentation includes alert runbook

---

## Story 8: Create Docker Compose for Local Development Environment

**Story Points**: 8  
**Priority**: P0 (Blocks local development)

### User Story
As a **developer**, I want **a local development environment using Docker Compose**, so that **I can develop and test services locally without Azure resources**.

### Context
Developers need a local environment that mirrors production infrastructure without incurring cloud costs. Docker Compose provides PostgreSQL, Redis, and Kafka locally with hot-reload for fast development iteration.

### Acceptance Criteria

#### Scenario 1: Docker Compose File Created
```gherkin
Given I have Docker Desktop installed
When I run `docker-compose up`
Then all infrastructure containers start successfully
And PostgreSQL container is running on port 5432
And Redis container is running on port 6379
And Kafka container is running on port 9092
And all services are healthy within 60 seconds
```

#### Scenario 2: Databases Initialized
```gherkin
Given containers are running
When I connect to PostgreSQL
Then individual databases exist for each microservice
And database schemas are initialized via init scripts
And test data is seeded for development
And database users are created with appropriate permissions
```

#### Scenario 3: Hot Reload Development
```gherkin
Given the local environment is running
When I modify service code
Then changes are detected automatically
And the service reloads without full container restart
And logs are visible in terminal output
And breakpoints work with debugger
```

#### Scenario 4: Environment Configuration
```gherkin
Given Docker Compose is configured
When services read configuration
Then environment variables are loaded from `.env` file
And sensible defaults are provided for local development
And connection strings point to local containers
And API ports don't conflict with other services
```

### Technical Implementation Notes

* **Files**: 
  * `docker-compose.yml`
  * `docker-compose.override.yml`
  * `.env.example`
  * `scripts/init-databases.sh`
  * `scripts/seed-test-data.sh`
* **Containers**:
  * PostgreSQL 15 (`postgres:15-alpine`)
  * Redis 7 (`redis:7-alpine`)
  * Kafka (`confluentinc/cp-kafka:latest`)
  * Zookeeper (`confluentinc/cp-zookeeper:latest`)
  * Redpanda Console (Kafka UI)
* **Port Mappings**:
  * PostgreSQL: 5432:5432
  * Redis: 6379:6379
  * Kafka: 9092:9092
  * Redpanda Console: 8080:8080

### Definition of Done
* [ ] Docker Compose file created
* [ ] All containers start successfully
* [ ] Database initialization scripts working
* [ ] Hot reload configured for service development
* [ ] Environment variable template (.env.example) created
* [ ] Network configuration allows inter-service communication
* [ ] Documentation includes setup instructions
* [ ] Troubleshooting guide for common issues
* [ ] Scripts for starting/stopping environment

---

## Story 9: Setup GitHub Actions CI/CD Pipeline Foundation

**Story Points**: 8  
**Priority**: P1 (Enables automation)

### User Story
As a **DevOps engineer**, I want **GitHub Actions pipelines configured**, so that **code is automatically tested and deployed when pushed to the repository**.

### Context
GitHub Actions provides free CI/CD for public repositories. We need baseline workflows for linting, testing, building Docker images, and deploying to Azure. Path-based filters will be added later as services are implemented.

### Acceptance Criteria

#### Scenario 1: Workflow Templates Created
```gherkin
Given the GitHub repository exists
When I create workflow files
Then a reusable workflow template exists for Python services
And a reusable workflow template exists for TypeScript frontend
And a workflow exists for Terraform infrastructure validation
And all workflows follow naming convention: `<service>-ci-cd.yml`
```

#### Scenario 2: CI Pipeline Functional
```gherkin
Given code is pushed to a feature branch
When the CI workflow runs
Then code is checked out successfully
And linting runs (flake8, black, mypy for Python)
And unit tests run with coverage reporting
And coverage report is uploaded to Codecov
And workflow fails if tests fail or coverage drops below 80%
```

#### Scenario 3: Docker Image Build
```gherkin
Given CI tests pass
When the build stage runs
Then Docker images are built for each service
And images are tagged with commit SHA and branch name
And images are pushed to Azure Container Registry
And multi-stage builds are used for optimization
```

#### Scenario 4: Deployment to Development
```gherkin
Given Docker images are built
When code is merged to main branch
Then development environment deployment is triggered
And Terraform changes are applied (if infrastructure changed)
And new container images are deployed to Azure Container Apps
And deployment health checks verify successful deployment
And rollback occurs automatically if health checks fail
```

### Technical Implementation Notes

* **Files**: 
  * `.github/workflows/reusable-python-service.yml`
  * `.github/workflows/reusable-frontend.yml`
  * `.github/workflows/terraform-validate.yml`
  * `.github/workflows/deploy-dev.yml`
* **GitHub Secrets Required**:
  * `AZURE_CREDENTIALS`
  * `ACR_LOGIN_SERVER`
  * `ACR_USERNAME`
  * `ACR_PASSWORD`
* **Path Filters**: Deferred until services are implemented

### Definition of Done
* [ ] Reusable workflow templates created
* [ ] CI pipeline runs successfully on sample service
* [ ] Docker images build and push to Azure Container Registry
* [ ] Terraform validation workflow functional
* [ ] Development deployment workflow functional
* [ ] GitHub secrets configured
* [ ] Branch protection rules configured
* [ ] Documentation includes workflow architecture diagram
* [ ] Note added about path filters for future implementation

---

## Story 10: Deploy Development Environment to Azure

**Story Points**: 5  
**Priority**: P0 (Culmination of infrastructure work)

### User Story
As a **DevOps engineer**, I want **the development environment deployed to Azure**, so that **we can begin service development with real cloud infrastructure**.

### Context
All Terraform modules are ready. This story applies those modules to create the actual development environment in Azure. This is the culmination of all infrastructure work and enables service development to begin.

### Acceptance Criteria

#### Scenario 1: Terraform Workspace Initialized
```gherkin
Given all Terraform modules are complete
When I initialize the dev workspace
Then Terraform connects to the remote backend successfully
And all module dependencies are resolved
And provider plugins are downloaded
And workspace is ready for planning
```

#### Scenario 2: Infrastructure Plan Validated
```gherkin
Given Terraform is initialized
When I run `terraform plan -var-file=environments/dev.tfvars`
Then Terraform generates a valid execution plan
And no errors are reported
And plan shows all expected resources
And plan passes cost estimation review (<$200/month for dev)
```

#### Scenario 3: Development Environment Deployed
```gherkin
Given the Terraform plan is validated
When I run `terraform apply`
Then networking module creates VNet and subnets
And Key Vault is created and accessible
And PostgreSQL Flexible Server is created with all databases
And Redis cache is operational
And Event Hubs namespace and topics are created
And monitoring workspace and Application Insights are configured
And all resources are tagged appropriately
```

#### Scenario 4: Infrastructure Validation
```gherkin
Given deployment is complete
When I run validation tests
Then PostgreSQL accepts connections from application subnet
And Redis cache responds to ping commands
And Event Hubs accept and return test messages
And Key Vault secrets are readable by service principal
And monitoring receives test telemetry
And all health checks pass
```

### Technical Implementation Notes

* **Files**: 
  * `infrastructure/main.tf`
  * `infrastructure/environments/dev.tfvars`
  * `infrastructure/outputs.tf`
  * `scripts/validate-infrastructure.sh`
* **Environment Configuration**:
  * Environment: `dev`
  * Region: `East US` or `West Europe`
  * PostgreSQL SKU: `B_Standard_B1ms`
  * Redis SKU: `Basic_C1`
  * Event Hubs SKU: `Standard` (1 TU)

### Definition of Done
* [ ] Dev environment variables file (dev.tfvars) configured
* [ ] Terraform plan reviewed and approved
* [ ] Terraform apply successful (all resources created)
* [ ] All infrastructure validation tests pass
* [ ] Connection strings documented securely
* [ ] Resource inventory documented
* [ ] Cost monitoring enabled and reviewed
* [ ] Terraform outputs captured for service configuration
* [ ] Documentation updated with actual resource names
* [ ] Team notified that dev environment is ready

---

## Story 11: Create Infrastructure Documentation and Runbooks

**Story Points**: 5  
**Priority**: P1 (Important for maintainability)

### User Story
As a **developer or operator**, I want **comprehensive infrastructure documentation**, so that **I can understand, troubleshoot, and maintain the infrastructure independently**.

### Context
Infrastructure is only valuable if the team can understand and operate it. Documentation should cover architecture, setup instructions, troubleshooting, and operational procedures.

### Acceptance Criteria

#### Scenario 1: Architecture Documentation Created
```gherkin
Given infrastructure is deployed
When developers review architecture documentation
Then a high-level architecture diagram exists
And network topology is documented with subnet CIDR blocks
And data flow diagrams show service communication patterns
And infrastructure components are explained with rationale
And cost breakdown by service is documented
```

#### Scenario 2: Setup Instructions Documented
```gherkin
Given a new developer joins the project
When they follow setup documentation
Then they can set up local environment from scratch in < 30 minutes
And they can deploy to dev environment with clear instructions
And all prerequisites are listed with installation links
And troubleshooting tips address common issues
And setup validation steps confirm everything works
```

#### Scenario 3: Operational Runbooks Created
```gherkin
Given an operational issue occurs
When operators consult runbooks
Then runbooks exist for common scenarios:
And "How to add a new microservice database"
And "How to scale resources up/down"
And "How to rotate secrets in Key Vault"
And "How to investigate high error rates"
And "How to restore from backup"
And "How to add monitoring alerts"
```

#### Scenario 4: Troubleshooting Guide Available
```gherkin
Given something goes wrong
When developers check troubleshooting guide
Then common problems have documented solutions:
And "PostgreSQL connection refused" → Check NSG rules
And "Redis timeout" → Check subnet configuration
And "Event Hub throttling" → Check throughput units
And "Terraform state lock" → How to break lease safely
And "High infrastructure costs" → Cost optimization steps
```

### Technical Implementation Notes

* **Files**: 
  * `docs/infrastructure/Architecture.md`
  * `docs/infrastructure/Setup_Guide.md`
  * `docs/infrastructure/Operational_Runbooks.md`
  * `docs/infrastructure/Troubleshooting.md`
  * `docs/infrastructure/Cost_Optimization.md`
  * `docs/infrastructure/diagrams/`
  * `infrastructure/README.md`
* **Documentation Includes**:
  * Architecture overview with Mermaid diagrams
  * Network topology diagram
  * Resource naming conventions
  * Local development setup
  * Azure deployment steps
  * CI/CD pipeline explanation
  * Monitoring and alerting guide
  * Cost management strategies
  * Security best practices
  * Disaster recovery procedures

### Definition of Done
* [ ] Architecture documentation complete with diagrams
* [ ] Setup guide tested by someone unfamiliar with project
* [ ] Operational runbooks created for top 10 scenarios
* [ ] Troubleshooting guide covers common issues
* [ ] All documentation uses markdown and renders in GitHub
* [ ] Diagrams use version-controllable formats (Mermaid)
* [ ] Links verified and not broken
* [ ] Documentation indexed in main README
* [ ] Feedback gathered from team and incorporated

---

## Sprint Summary

**Total Story Points**: 68-73 (updated to reflect multi-deployment complexity)  
**Total Stories**: 11  
**Estimated Duration**: 1 week (5 working days)

**Story Point Changes**:
- ECS-18 (Terraform Backend): 3 → 5 points (multi-deployment backend)
- ECS-19 (Networking): 5 → 8 points (CIDR allocation map + multi-deployment)
- Total increase: +5 points

### Multi-Deployment Architecture

This sprint now supports **multi-region, multi-instance deployments**:
- Each deployment (e.g., `westeu-test-1`, `westeu-prod-1`) is completely isolated
- Unique CIDR block per deployment from pre-allocated ranges
- Separate Terraform state file per deployment
- Enables parallel infrastructure work across deployments

**MVP Focus**: Deploy **westeu-test-1** only in this sprint. Prove one complete deployment works end-to-end before expanding to staging/production.

### Implementation Order

1. **Story 0 (ECS-46)**: Azure Subscription Preparation (prerequisite for all Terraform)
2. **Story 1 (ECS-18)**: Terraform Backend with multi-deployment support
3. **Story 2 (ECS-19)**: Networking Module with CIDR allocation map
4. **Stories 3-7**: Can be worked in parallel (Database, Redis, Event Hubs, Key Vault, Monitoring)
5. **Story 8**: Docker Compose (parallel with Terraform work)
6. **Story 9**: GitHub Actions (parallel with Terraform work)
7. **Story 10**: Deploy westeu-test-1 to Azure (after stories 1-7 complete)
8. **Story 11**: Documentation including Infrastructure_Architecture.md (ongoing)

### Critical Path
ECS-46 → ECS-18 → ECS-19 → Stories 3-6 → Story 10

### Risk Items
* **CIDR allocation conflicts** - Mitigated by pre-allocated CIDR map in locals.tf
* **Multi-deployment complexity** - Mitigated by focusing on westeu-test-1 only for MVP
* Azure quota limits
* Service principal permission issues
* Terraform state locking conflicts (per-deployment isolation helps)
* Event Hub throughput settings

### Success Criteria for Sprint
* ✅ **westeu-test-1** deployment fully operational in Azure (West Europe)
* ✅ Multi-deployment architecture proven (can deploy additional envs later)
* ✅ CIDR allocation prevents conflicts across future deployments
* ✅ Local development environment functional (Docker Compose)
* ✅ CI/CD pipeline running for westeu-test-1
* ✅ Infrastructure_Architecture.md documents multi-deployment strategy
* ✅ All infrastructure documentation complete
* ✅ Ready to deploy services to westeu-test-1 (begin ECS-8: User Service)

### Future Deployments (Post-Sprint)
After proving westeu-test-1 works:
- Deploy **westeu-stg-1** for staging/UAT
- Deploy **westeu-prod-1** for production (Europe)
- Deploy **eastus-prod-1** for US data residency
- Enable VNet peering for cross-region communication

### New Documentation Requirements
* `docs/Infrastructure_Architecture.md` - **Created in this sprint**
  - Multi-deployment strategy
  - CIDR allocation table
  - Naming conventions
  - Deployment workflow
  - Cost management per deployment
