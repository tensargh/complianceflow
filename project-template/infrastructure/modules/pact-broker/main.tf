# Pact Broker Infrastructure for Contract Testing

# Container App Environment for Pact Broker
resource "azurerm_container_app" "pact_broker" {
  name                         = "${var.name_prefix}-pact-broker"
  container_app_environment_id = var.container_app_environment_id
  resource_group_name          = var.resource_group_name
  revision_mode               = "Single"
  tags                        = var.tags

  template {
    min_replicas = 1
    max_replicas = 3

    container {
      name   = "pact-broker"
      image  = "pactfoundation/pact-broker:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "PACT_BROKER_DATABASE_URL"
        value = var.database_connection_string
      }

      env {
        name  = "PACT_BROKER_BASIC_AUTH_USERNAME"
        value = var.basic_auth_username
      }

      env {
        name        = "PACT_BROKER_BASIC_AUTH_PASSWORD"
        secret_name = "pact-broker-password"
      }

      env {
        name  = "PACT_BROKER_BASIC_AUTH_READ_ONLY_USERNAME"
        value = var.readonly_username
      }

      env {
        name        = "PACT_BROKER_BASIC_AUTH_READ_ONLY_PASSWORD"
        secret_name = "pact-broker-readonly-password"
      }

      env {
        name  = "PACT_BROKER_PUBLIC_HEARTBEAT"
        value = "true"
      }

      env {
        name  = "PACT_BROKER_WEBHOOK_HTTP_METHOD_WHITELIST"
        value = "POST"
      }

      env {
        name  = "PACT_BROKER_WEBHOOK_SCHEME_WHITELIST"
        value = "https"
      }

      env {
        name  = "PACT_BROKER_WEBHOOK_HOST_WHITELIST"
        value = var.webhook_host_whitelist
      }

      env {
        name  = "PACT_BROKER_FEATURES"
        value = "contracts_requiring_verification_published_results_webhook"
      }

      env {
        name  = "PACT_BROKER_LOG_LEVEL"
        value = var.log_level
      }

      ports {
        port_number = 9292
      }
    }

    # HTTP Scale Rule
    http_scale_rule {
      name                = "http-requests"
      concurrent_requests = 100
    }
  }

  # Secrets for authentication
  secret {
    name  = "pact-broker-password"
    value = var.basic_auth_password
  }

  secret {
    name  = "pact-broker-readonly-password"
    value = var.readonly_password
  }

  ingress {
    external_enabled = true
    target_port      = 9292
    
    traffic_weight {
      percentage = 100
      latest_revision = true
    }
  }
}

# PostgreSQL Database for Pact Broker
resource "azurerm_postgresql_flexible_server_database" "pact_broker" {
  name      = "pact_broker"
  server_id = var.postgresql_server_id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Application Insights for Pact Broker monitoring
resource "azurerm_application_insights" "pact_broker" {
  name                = "${var.name_prefix}-pact-broker-insights"
  location            = var.location
  resource_group_name = var.resource_group_name
  workspace_id        = var.log_analytics_workspace_id
  application_type    = "web"
  tags                = var.tags
}

# Container App with enhanced monitoring
resource "azurerm_monitor_diagnostic_setting" "pact_broker" {
  name                       = "pact-broker-diagnostics"
  target_resource_id         = azurerm_container_app.pact_broker.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "ContainerAppConsoleLogs"
  }

  enabled_log {
    category = "ContainerAppSystemLogs"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

# Health check alert for Pact Broker
resource "azurerm_monitor_metric_alert" "pact_broker_health" {
  name                = "${var.name_prefix}-pact-broker-health"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_container_app.pact_broker.id]
  description         = "Alert when Pact Broker is unhealthy"
  severity            = 1
  frequency           = "PT1M"
  window_size         = "PT5M"
  tags                = var.tags

  criteria {
    metric_namespace = "microsoft.app/containerapps"
    metric_name      = "Requests"
    aggregation      = "Count"
    operator         = "LessThan"
    threshold        = 1
  }

  action {
    action_group_id = var.action_group_id
  }
}

# DNS record for custom domain (optional)
resource "azurerm_dns_cname_record" "pact_broker" {
  count               = var.custom_domain != "" ? 1 : 0
  name                = "pact-broker"
  zone_name           = var.dns_zone_name
  resource_group_name = var.dns_zone_resource_group
  ttl                 = 300
  record              = azurerm_container_app.pact_broker.ingress[0].fqdn
  tags                = var.tags
}
