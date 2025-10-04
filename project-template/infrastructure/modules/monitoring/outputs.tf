# Outputs for Enhanced Monitoring Module

output "log_analytics_workspace_id" {
  description = "The ID of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.id
}

output "log_analytics_workspace_name" {
  description = "The name of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.name
}

output "log_analytics_workspace_key" {
  description = "The primary shared key for the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.primary_shared_key
  sensitive   = true
}

output "application_insights_id" {
  description = "The ID of the main Application Insights instance"
  value       = azurerm_application_insights.main.id
}

output "application_insights_name" {
  description = "The name of the main Application Insights instance"
  value       = azurerm_application_insights.main.name
}

output "application_insights_instrumentation_key" {
  description = "The instrumentation key for the main Application Insights instance"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "application_insights_connection_string" {
  description = "The connection string for the main Application Insights instance"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "service_application_insights" {
  description = "Map of service names to their Application Insights details"
  value = {
    for service, ai in azurerm_application_insights.services : service => {
      id                    = ai.id
      name                  = ai.name
      instrumentation_key   = ai.instrumentation_key
      connection_string     = ai.connection_string
      app_id               = ai.app_id
    }
  }
  sensitive = true
}

output "action_group_ids" {
  description = "Map of action group names to their IDs"
  value = {
    critical = azurerm_monitor_action_group.critical.id
    warning  = azurerm_monitor_action_group.warning.id
  }
}

output "metric_alert_ids" {
  description = "Map of metric alert names to their IDs"
  value = {
    high_error_rate     = { for k, v in azurerm_monitor_metric_alert.high_error_rate : k => v.id }
    high_response_time  = { for k, v in azurerm_monitor_metric_alert.high_response_time : k => v.id }
    service_unavailable = { for k, v in azurerm_monitor_metric_alert.service_unavailable : k => v.id }
  }
}

output "saved_search_ids" {
  description = "Map of saved search names to their IDs"
  value = {
    error_analysis       = azurerm_log_analytics_saved_search.error_analysis.id
    performance_analysis = azurerm_log_analytics_saved_search.performance_analysis.id
    user_activity       = azurerm_log_analytics_saved_search.user_activity.id
  }
}

output "workbook_id" {
  description = "The ID of the main monitoring workbook"
  value       = azurerm_application_insights_workbook.main_dashboard.id
}

output "private_link_scope_id" {
  description = "The ID of the Monitor Private Link Scope"
  value       = azurerm_monitor_private_link_scope.main.id
}

output "monitoring_endpoints" {
  description = "Monitoring endpoints for services"
  value = {
    log_analytics_portal_url = "https://portal.azure.com/#@/resource${azurerm_log_analytics_workspace.main.id}/logs"
    app_insights_portal_url  = "https://portal.azure.com/#@/resource${azurerm_application_insights.main.id}/overview"
    dashboard_url           = "https://portal.azure.com/#@/resource${azurerm_application_insights_workbook.main_dashboard.id}/workbook"
  }
}

# Environment variables for services
output "monitoring_environment_variables" {
  description = "Environment variables to be used by services for monitoring"
  value = {
    # Application Insights
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_application_insights.main.connection_string
    APPINSIGHTS_INSTRUMENTATIONKEY       = azurerm_application_insights.main.instrumentation_key
    
    # Log Analytics
    LOG_ANALYTICS_WORKSPACE_ID  = azurerm_log_analytics_workspace.main.workspace_id
    LOG_ANALYTICS_WORKSPACE_KEY = azurerm_log_analytics_workspace.main.primary_shared_key
    
    # Monitoring Configuration
    MONITORING_ENABLED           = "true"
    MONITORING_SAMPLING_RATE     = tostring(var.sampling_percentage / 100)
    MONITORING_LOG_LEVEL        = "INFO"
    MONITORING_TRACE_ENABLED    = "true"
    MONITORING_METRICS_ENABLED  = "true"
  }
  sensitive = true
}

# Service-specific monitoring configuration
output "service_monitoring_config" {
  description = "Per-service monitoring configuration"
  value = {
    for service in var.services : service => {
      application_insights_connection_string = azurerm_application_insights.services[service].connection_string
      application_insights_instrumentation_key = azurerm_application_insights.services[service].instrumentation_key
      service_name = service
      alerts_enabled = true
      custom_dimensions = {
        service = service
        environment = var.name_prefix
      }
    }
  }
  sensitive = true
}
