# Enhanced Monitoring Module for Compliance Flow
# Includes Application Insights, Log Analytics, Dashboards, and Alerting

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.name_prefix}-logs"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.retention_in_days
  daily_quota_gb      = var.daily_quota_gb
  tags                = var.tags
}

# Application Insights
resource "azurerm_application_insights" "main" {
  name                = "${var.name_prefix}-insights"
  location            = var.location
  resource_group_name = var.resource_group_name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = var.application_type
  retention_in_days   = var.retention_in_days
  sampling_percentage = var.sampling_percentage
  tags                = var.tags
}

# Service-specific Application Insights instances for detailed monitoring
resource "azurerm_application_insights" "services" {
  for_each = toset(var.services)
  
  name                = "${var.name_prefix}-${each.key}-insights"
  location            = var.location
  resource_group_name = var.resource_group_name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  retention_in_days   = var.retention_in_days
  sampling_percentage = var.sampling_percentage
  tags                = merge(var.tags, {
    Service = each.key
  })
}

# Action Groups for Alerting
resource "azurerm_monitor_action_group" "critical" {
  name                = "${var.name_prefix}-critical-alerts"
  resource_group_name = var.resource_group_name
  short_name          = "crit-alert"
  tags                = var.tags

  email_receiver {
    name          = "admin"
    email_address = var.admin_email
  }

  sms_receiver {
    name         = "admin-sms"
    country_code = var.sms_country_code
    phone_number = var.admin_phone
  }

  webhook_receiver {
    name        = "teams"
    service_uri = var.teams_webhook_url
  }
}

resource "azurerm_monitor_action_group" "warning" {
  name                = "${var.name_prefix}-warning-alerts"
  resource_group_name = var.resource_group_name
  short_name          = "warn-alert"
  tags                = var.tags

  email_receiver {
    name          = "team"
    email_address = var.team_email
  }

  webhook_receiver {
    name        = "teams"
    service_uri = var.teams_webhook_url
  }
}

# Metric Alerts
resource "azurerm_monitor_metric_alert" "high_error_rate" {
  for_each = toset(var.services)
  
  name                = "${var.name_prefix}-${each.key}-high-error-rate"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_application_insights.services[each.key].id]
  description         = "Alert when error rate is high for ${each.key}"
  severity            = 2
  frequency           = "PT1M"
  window_size         = "PT5M"
  tags                = var.tags

  criteria {
    metric_namespace = "microsoft.insights/components"
    metric_name      = "requests/failed"
    aggregation      = "Count"
    operator         = "GreaterThan"
    threshold        = 10
  }

  action {
    action_group_id = azurerm_monitor_action_group.warning.id
  }
}

resource "azurerm_monitor_metric_alert" "high_response_time" {
  for_each = toset(var.services)
  
  name                = "${var.name_prefix}-${each.key}-high-response-time"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_application_insights.services[each.key].id]
  description         = "Alert when response time is high for ${each.key}"
  severity            = 2
  frequency           = "PT1M"
  window_size         = "PT5M"
  tags                = var.tags

  criteria {
    metric_namespace = "microsoft.insights/components"
    metric_name      = "requests/duration"
    aggregation      = "Average"
    operator         = "GreaterThan"
    threshold        = 2000  # 2 seconds
  }

  action {
    action_group_id = azurerm_monitor_action_group.warning.id
  }
}

resource "azurerm_monitor_metric_alert" "service_unavailable" {
  for_each = toset(var.services)
  
  name                = "${var.name_prefix}-${each.key}-unavailable"
  resource_group_name = var.resource_group_name
  scopes              = [azurerm_application_insights.services[each.key].id]
  description         = "Critical alert when ${each.key} is unavailable"
  severity            = 0
  frequency           = "PT1M"
  window_size         = "PT5M"
  tags                = var.tags

  criteria {
    metric_namespace = "microsoft.insights/components"
    metric_name      = "requests/count"
    aggregation      = "Count"
    operator         = "LessThan"
    threshold        = 1
  }

  action {
    action_group_id = azurerm_monitor_action_group.critical.id
  }
}

# Log Analytics Queries for Common Scenarios
resource "azurerm_log_analytics_saved_search" "error_analysis" {
  name                       = "ErrorAnalysis"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  category                   = "Application"
  display_name              = "Error Analysis"
  query                     = <<QUERY
exceptions
| where timestamp > ago(1h)
| summarize count() by problemId, outerMessage
| order by count_ desc
QUERY
  tags                      = var.tags
}

resource "azurerm_log_analytics_saved_search" "performance_analysis" {
  name                       = "PerformanceAnalysis"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  category                   = "Application"
  display_name              = "Performance Analysis"
  query                     = <<QUERY
requests
| where timestamp > ago(1h)
| summarize avg(duration), percentile(duration, 95), count() by operation_Name
| order by avg_duration desc
QUERY
  tags                      = var.tags
}

resource "azurerm_log_analytics_saved_search" "user_activity" {
  name                       = "UserActivity"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  category                   = "Usage"
  display_name              = "User Activity Analysis"
  query                     = <<QUERY
pageViews
| where timestamp > ago(24h)
| summarize count() by user_Id
| summarize active_users = count()
QUERY
  tags                      = var.tags
}

# Workbook for Comprehensive Monitoring Dashboard
resource "azurerm_application_insights_workbook" "main_dashboard" {
  name                = "${var.name_prefix}-dashboard"
  resource_group_name = var.resource_group_name
  location            = var.location
  display_name        = "Compliance Flow Dashboard"
  data_json = jsonencode({
    version = "Notebook/1.0"
    items = [
      {
        type = 1
        content = {
          json = "# Compliance Flow - System Overview\n\nThis dashboard provides a comprehensive view of the Compliance Flow platform health and performance."
        }
      },
      {
        type = 3
        content = {
          version = "KqlItem/1.0"
          query = "requests | where timestamp > ago(1h) | summarize requests = count() by bin(timestamp, 5m) | render timechart"
          size = 0
          title = "Request Volume (Last Hour)"
          timeContext = {
            durationMs = 3600000
          }
        }
      },
      {
        type = 3
        content = {
          version = "KqlItem/1.0"
          query = "requests | where timestamp > ago(1h) | summarize avg_duration = avg(duration) by bin(timestamp, 5m) | render timechart"
          size = 0
          title = "Average Response Time (Last Hour)"
          timeContext = {
            durationMs = 3600000
          }
        }
      },
      {
        type = 3
        content = {
          version = "KqlItem/1.0"
          query = "exceptions | where timestamp > ago(24h) | summarize exceptions = count() by bin(timestamp, 1h) | render timechart"
          size = 0
          title = "Exceptions (Last 24 Hours)"
          timeContext = {
            durationMs = 86400000
          }
        }
      }
    ]
  })
  tags = var.tags
}

# Smart Detection Rules
resource "azurerm_application_insights_smart_detection_rule" "failure_anomalies" {
  name                    = "Failure Anomalies"
  application_insights_id = azurerm_application_insights.main.id
  enabled                 = true
  send_emails_to_subscription_owners = true
  additional_email_recipients = [var.admin_email]
}

resource "azurerm_application_insights_smart_detection_rule" "performance_anomalies" {
  name                    = "Performance Anomalies"
  application_insights_id = azurerm_application_insights.main.id
  enabled                 = true
  send_emails_to_subscription_owners = true
  additional_email_recipients = [var.admin_email]
}

# Diagnostic Settings for Container Apps
resource "azurerm_monitor_diagnostic_setting" "container_apps" {
  for_each = toset(var.services)
  
  name                       = "${each.key}-diagnostics"
  target_resource_id         = var.container_app_ids[each.key]
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

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

# Custom Log Tables for Structured Logging
resource "azurerm_log_analytics_datasource_windows_performance_counter" "cpu_usage" {
  count                   = var.enable_custom_logs ? 1 : 0
  name                    = "CPU Usage"
  resource_group_name     = var.resource_group_name
  workspace_name          = azurerm_log_analytics_workspace.main.name
  object_name            = "Processor"
  instance_name          = "*"
  counter_name           = "% Processor Time"
  interval_seconds       = 60
}

# Azure Monitor Private Link Scope for secure monitoring
resource "azurerm_monitor_private_link_scope" "main" {
  name                = "${var.name_prefix}-monitor-pls"
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_monitor_private_link_scoped_service" "app_insights" {
  name                = "${var.name_prefix}-insights-pls"
  resource_group_name = var.resource_group_name
  scope_name          = azurerm_monitor_private_link_scope.main.name
  linked_resource_id  = azurerm_application_insights.main.id
}

resource "azurerm_monitor_private_link_scoped_service" "log_analytics" {
  name                = "${var.name_prefix}-logs-pls"
  resource_group_name = var.resource_group_name
  scope_name          = azurerm_monitor_private_link_scope.main.name
  linked_resource_id  = azurerm_log_analytics_workspace.main.id
}
