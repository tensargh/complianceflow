# Outputs for Compliance Flow Infrastructure

# Resource Group
output "resource_group_name" {
  description = "Name of the main resource group"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Location of the main resource group"
  value       = azurerm_resource_group.main.location
}

# Networking
output "vnet_id" {
  description = "Virtual Network ID"
  value       = module.networking.vnet_id
}

output "vnet_name" {
  description = "Virtual Network name"
  value       = module.networking.vnet_name
}

output "subnet_ids" {
  description = "Map of subnet names to IDs"
  value       = module.networking.subnet_ids
}

# Key Vault
output "key_vault_id" {
  description = "Key Vault ID"
  value       = module.key_vault.key_vault_id
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = module.key_vault.key_vault_uri
}

# Database
output "database_server_name" {
  description = "PostgreSQL server name"
  value       = module.database.server_name
}

output "database_server_fqdn" {
  description = "PostgreSQL server FQDN"
  value       = module.database.server_fqdn
}

output "database_connection_strings" {
  description = "Database connection strings for each service"
  value       = module.database.connection_strings
  sensitive   = true
}

# Redis
output "redis_hostname" {
  description = "Redis hostname"
  value       = module.redis.hostname
}

output "redis_port" {
  description = "Redis port"
  value       = module.redis.port
}

output "redis_primary_access_key" {
  description = "Redis primary access key"
  value       = module.redis.primary_access_key
  sensitive   = true
}

# Kafka
output "kafka_bootstrap_servers" {
  description = "Kafka bootstrap servers"
  value       = module.kafka.bootstrap_servers
  sensitive   = true
}

output "kafka_api_key" {
  description = "Kafka API key"
  value       = module.kafka.api_key
  sensitive   = true
}

output "kafka_api_secret" {
  description = "Kafka API secret"
  value       = module.kafka.api_secret
  sensitive   = true
}

# Container Registry
output "container_registry_name" {
  description = "Container Registry name"
  value       = module.container_registry.registry_name
}

output "container_registry_login_server" {
  description = "Container Registry login server"
  value       = module.container_registry.login_server
}

# Container Apps
output "container_apps_environment_id" {
  description = "Container Apps Environment ID"
  value       = module.container_apps.environment_id
}

output "container_apps_environment_domain" {
  description = "Container Apps Environment default domain"
  value       = module.container_apps.default_domain
}

# Storage
output "storage_account_name" {
  description = "Storage Account name"
  value       = module.storage.account_name
}

output "storage_account_primary_endpoint" {
  description = "Storage Account primary blob endpoint"
  value       = module.storage.primary_blob_endpoint
}

output "storage_account_connection_string" {
  description = "Storage Account connection string"
  value       = module.storage.connection_string
  sensitive   = true
}

# Monitoring
output "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID"
  value       = module.monitoring.log_analytics_workspace_id
}

output "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = module.monitoring.application_insights_instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "Application Insights connection string"
  value       = module.monitoring.application_insights_connection_string
  sensitive   = true
}

# API Management (if deployed)
output "api_management_gateway_url" {
  description = "API Management gateway URL"
  value       = var.environment == "prod" ? module.api_management[0].gateway_url : null
}

output "api_management_management_api_url" {
  description = "API Management management API URL"
  value       = var.environment == "prod" ? module.api_management[0].management_api_url : null
}

# Service URLs (for development and testing)
output "service_urls" {
  description = "Internal service URLs for inter-service communication"
  value = {
    user_service         = "http://user-service.${module.container_apps.default_domain}"
    declaration_service  = "http://declaration-service.${module.container_apps.default_domain}"
    form_service        = "http://form-service.${module.container_apps.default_domain}"
    rule_engine_service = "http://rule-engine-service.${module.container_apps.default_domain}"
    review_service      = "http://review-service.${module.container_apps.default_domain}"
    case_service        = "http://case-service.${module.container_apps.default_domain}"
    notification_service = "http://notification-service.${module.container_apps.default_domain}"
    analytics_service   = "http://analytics-service.${module.container_apps.default_domain}"
  }
}

# Environment Configuration Summary
output "environment_config" {
  description = "Environment configuration summary"
  value = {
    environment     = var.environment
    location       = var.location
    resource_prefix = local.name_prefix
    database_sku   = var.database_sku_name
    redis_sku      = var.redis_sku_name
    storage_tier   = var.storage_account_tier
  }
}

