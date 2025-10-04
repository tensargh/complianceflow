# Outputs for Pact Broker Module

output "pact_broker_url" {
  description = "The URL of the Pact Broker"
  value       = "https://${azurerm_container_app.pact_broker.ingress[0].fqdn}"
}

output "pact_broker_fqdn" {
  description = "The FQDN of the Pact Broker"
  value       = azurerm_container_app.pact_broker.ingress[0].fqdn
}

output "pact_broker_container_app_id" {
  description = "The ID of the Pact Broker Container App"
  value       = azurerm_container_app.pact_broker.id
}

output "pact_broker_database_name" {
  description = "The name of the Pact Broker database"
  value       = azurerm_postgresql_flexible_server_database.pact_broker.name
}

output "application_insights_connection_string" {
  description = "Application Insights connection string for Pact Broker"
  value       = azurerm_application_insights.pact_broker.connection_string
  sensitive   = true
}

output "application_insights_instrumentation_key" {
  description = "Application Insights instrumentation key for Pact Broker"
  value       = azurerm_application_insights.pact_broker.instrumentation_key
  sensitive   = true
}

output "basic_auth_credentials" {
  description = "Basic authentication credentials for Pact Broker"
  value = {
    username = var.basic_auth_username
    password = var.basic_auth_password
  }
  sensitive = true
}

output "readonly_credentials" {
  description = "Read-only credentials for Pact Broker"
  value = {
    username = var.readonly_username
    password = var.readonly_password
  }
  sensitive = true
}

output "custom_domain_url" {
  description = "Custom domain URL if configured"
  value       = var.custom_domain != "" ? "https://pact-broker.${var.custom_domain}" : ""
}

output "health_check_url" {
  description = "Health check URL for Pact Broker"
  value       = "https://${azurerm_container_app.pact_broker.ingress[0].fqdn}/diagnostic/status/heartbeat"
}

output "environment_variables" {
  description = "Environment variables for services to connect to Pact Broker"
  value = {
    PACT_BROKER_BASE_URL = "https://${azurerm_container_app.pact_broker.ingress[0].fqdn}"
    PACT_BROKER_USERNAME = var.basic_auth_username
    PACT_BROKER_PASSWORD = var.basic_auth_password
    PACT_BROKER_TOKEN    = base64encode("${var.basic_auth_username}:${var.basic_auth_password}")
  }
  sensitive = true
}
