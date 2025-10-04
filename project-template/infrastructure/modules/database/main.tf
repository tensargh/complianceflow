# PostgreSQL Database Module

# Generate random password
resource "random_password" "admin_password" {
  length  = 16
  special = true
}

# Store password in Key Vault
resource "azurerm_key_vault_secret" "admin_password" {
  name         = "database-admin-password"
  value        = random_password.admin_password.result
  key_vault_id = var.key_vault_id
}

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.name_prefix}-postgres"
  resource_group_name    = var.resource_group_name
  location              = var.location
  version               = "15"
  delegated_subnet_id   = var.subnet_id
  private_dns_zone_id   = var.private_dns_zone_id
  administrator_login   = var.administrator_login
  administrator_password = random_password.admin_password.result
  zone                  = "1"

  storage_mb            = var.storage_mb
  sku_name             = var.sku_name
  backup_retention_days = var.backup_retention_days
  geo_redundant_backup_enabled = var.geo_redundant_backup

  tags = var.tags

  depends_on = [var.private_dns_zone_id]
}

# PostgreSQL Configuration
resource "azurerm_postgresql_flexible_server_configuration" "log_statement" {
  name      = "log_statement"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "all"
}

resource "azurerm_postgresql_flexible_server_configuration" "log_min_duration_statement" {
  name      = "log_min_duration_statement"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "1000"
}

# Databases for each microservice
locals {
  databases = [
    "user_service",
    "declaration_service", 
    "form_service",
    "rule_engine_service",
    "review_service",
    "case_service",
    "notification_service",
    "analytics_service"
  ]
}

resource "azurerm_postgresql_flexible_server_database" "databases" {
  for_each = toset(local.databases)
  
  name      = each.value
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Store connection strings in Key Vault
resource "azurerm_key_vault_secret" "connection_strings" {
  for_each = toset(local.databases)
  
  name         = "${each.value}-connection-string"
  value        = "postgresql://${var.administrator_login}:${random_password.admin_password.result}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${each.value}?sslmode=require"
  key_vault_id = var.key_vault_id
}



