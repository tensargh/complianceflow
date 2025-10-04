# Compliance Flow Infrastructure
# Main Terraform configuration for multi-environment deployment

terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
  }

  # Backend configuration - uncomment and configure for production
  # backend "azurerm" {
  #   resource_group_name  = "compliance-flow-tfstate"
  #   storage_account_name = "complianceflowstate"
  #   container_name       = "tfstate"
  #   key                  = "terraform.tfstate"
  # }
}

# Configure the Azure Provider
provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

# Data sources
data "azurerm_client_config" "current" {}

# Local values for consistent naming
locals {
  environment = var.environment
  location    = var.location
  
  # Consistent naming convention
  name_prefix = "cf-${local.environment}"
  
  # Common tags applied to all resources
  common_tags = {
    Environment   = local.environment
    Project      = "ComplianceFlow"
    ManagedBy    = "Terraform"
    CostCenter   = var.cost_center
    Owner        = var.owner
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "${local.name_prefix}-rg"
  location = local.location
  tags     = local.common_tags
}

# Virtual Network and Subnets
module "networking" {
  source = "./modules/networking"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  # Network configuration
  vnet_address_space     = var.vnet_address_space
  subnet_configurations  = var.subnet_configurations
}

# Key Vault for secrets management
module "key_vault" {
  source = "./modules/key_vault"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = data.azurerm_client_config.current.object_id
}

# PostgreSQL Database
module "database" {
  source = "./modules/database"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  # Database configuration
  sku_name                = var.database_sku_name
  storage_mb             = var.database_storage_mb
  backup_retention_days  = var.database_backup_retention_days
  geo_redundant_backup   = var.database_geo_redundant_backup
  
  # Network integration
  subnet_id              = module.networking.database_subnet_id
  private_dns_zone_id    = module.networking.database_private_dns_zone_id
  
  # Credentials
  administrator_login    = var.database_admin_username
  key_vault_id          = module.key_vault.key_vault_id
}

# Redis Cache
module "redis" {
  source = "./modules/redis"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  # Redis configuration
  sku_name           = var.redis_sku_name
  family             = var.redis_family
  capacity           = var.redis_capacity
  
  # Network integration
  subnet_id          = module.networking.redis_subnet_id
  key_vault_id       = module.key_vault.key_vault_id
}

# Kafka (Confluent Cloud)
module "kafka" {
  source = "./modules/kafka"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  # Kafka configuration
  environment_name   = var.kafka_environment_name
  cluster_name      = var.kafka_cluster_name
  availability      = var.kafka_availability
  cloud_provider    = "AZURE"
  region            = var.kafka_region
  
  key_vault_id      = module.key_vault.key_vault_id
}

# Container Registry
module "container_registry" {
  source = "./modules/container_registry"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  sku = var.container_registry_sku
}

# Container Apps Environment
module "container_apps" {
  source = "./modules/container_apps"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  # Network integration
  subnet_id                    = module.networking.container_apps_subnet_id
  internal_load_balancer_enabled = var.container_apps_internal_lb
  
  # Dependencies
  key_vault_id                = module.key_vault.key_vault_id
  container_registry_id       = module.container_registry.registry_id
  log_analytics_workspace_id  = module.monitoring.log_analytics_workspace_id
}

# Storage Account for file uploads
module "storage" {
  source = "./modules/storage"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  # Storage configuration
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_replication_type
  
  # Network integration
  subnet_id           = module.networking.storage_subnet_id
  private_dns_zone_id = module.networking.storage_private_dns_zone_id
  
  # Containers
  containers = [
    "declarations",
    "cases",
    "reports"
  ]
  
  key_vault_id = module.key_vault.key_vault_id
}

# Monitoring and Logging
module "monitoring" {
  source = "./modules/monitoring"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  # Log Analytics configuration
  retention_in_days = var.log_analytics_retention_days
  daily_quota_gb    = var.log_analytics_daily_quota_gb
  
  # Application Insights configuration
  application_type     = "web"
  sampling_percentage  = var.app_insights_sampling_percentage
  
  # Alert configuration
  admin_email          = var.admin_email
  team_email          = var.team_email
  admin_phone         = var.admin_phone
  teams_webhook_url   = var.teams_webhook_url
  
  # Service configuration
  services = var.services
  container_app_ids = module.container_apps.container_app_ids
}

# Security Module
module "security" {
  source = "./modules/security"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  # Azure configuration
  subscription_id = data.azurerm_client_config.current.subscription_id
  tenant_id      = data.azurerm_client_config.current.tenant_id
  
  # Security configuration
  security_center_tier    = var.security_center_tier
  security_contact_email  = var.security_contact_email
  security_contact_phone  = var.security_contact_phone
  
  # WAF configuration
  waf_mode                    = var.waf_mode
  waf_blocked_countries      = var.waf_blocked_countries
  
  # Resource dependencies
  key_vault_id                = module.key_vault.key_vault_id
  log_analytics_workspace_id  = module.monitoring.log_analytics_workspace_id
  security_action_group_id    = module.monitoring.action_group_ids.critical
  security_admin_object_id    = data.azurerm_client_config.current.object_id
  
  # Feature flags
  enable_ddos_protection = var.enable_ddos_protection
  enable_backup         = var.enable_backup
  enable_sentinel       = var.enable_sentinel
  
  # Compliance
  compliance_frameworks = var.compliance_frameworks
}

# Pact Broker for Contract Testing
module "pact_broker" {
  source = "./modules/pact-broker"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  # Dependencies
  container_app_environment_id   = module.container_apps.container_app_environment_id
  postgresql_server_id          = module.database.postgresql_server_id
  log_analytics_workspace_id    = module.monitoring.log_analytics_workspace_id
  action_group_id              = module.monitoring.action_group_ids.warning
  
  # Configuration
  database_connection_string = "postgresql://${var.database_admin_username}:${random_password.pact_broker_password.result}@${module.database.postgresql_server_fqdn}:5432/pact_broker?sslmode=require"
  basic_auth_username       = "pact_broker"
  basic_auth_password       = random_password.pact_broker_auth.result
  readonly_username         = "readonly"
  readonly_password         = random_password.pact_broker_readonly.result
}

# Random passwords for Pact Broker
resource "random_password" "pact_broker_password" {
  length  = 32
  special = true
}

resource "random_password" "pact_broker_auth" {
  length  = 24
  special = true
}

resource "random_password" "pact_broker_readonly" {
  length  = 24
  special = true
}

# API Management (for production environments)
module "api_management" {
  count  = var.environment == "prod" ? 1 : 0
  source = "./modules/api_management"
  
  resource_group_name = azurerm_resource_group.main.name
  location           = azurerm_resource_group.main.location
  name_prefix        = local.name_prefix
  tags               = local.common_tags
  
  # APIM configuration
  sku_name          = var.apim_sku_name
  publisher_name    = var.apim_publisher_name
  publisher_email   = var.apim_publisher_email
  
  # Network integration
  subnet_id         = module.networking.apim_subnet_id
  
  # SSL configuration
  key_vault_id      = module.key_vault.key_vault_id
  
  # WAF integration
  waf_policy_id     = module.security.waf_policy_id
}
