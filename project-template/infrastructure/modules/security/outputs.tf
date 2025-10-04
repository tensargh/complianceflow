# Outputs for Security Module

output "waf_policy_id" {
  description = "ID of the Web Application Firewall policy"
  value       = azurerm_web_application_firewall_policy.main.id
}

output "network_security_group_id" {
  description = "ID of the web tier network security group"
  value       = azurerm_network_security_group.web_tier.id
}

output "ddos_protection_plan_id" {
  description = "ID of the DDoS protection plan"
  value       = var.enable_ddos_protection ? azurerm_network_ddos_protection_plan.main[0].id : null
}

output "private_dns_zone_id" {
  description = "ID of the internal private DNS zone"
  value       = azurerm_private_dns_zone.internal.id
}

output "backup_vault_id" {
  description = "ID of the backup vault"
  value       = var.enable_backup ? azurerm_data_protection_backup_vault.main[0].id : null
}

output "backup_policy_id" {
  description = "ID of the database backup policy"
  value       = var.enable_backup ? azurerm_data_protection_backup_policy_postgresql.main[0].id : null
}

output "security_center_pricing_tiers" {
  description = "Security Center pricing tiers configuration"
  value = {
    virtual_machines    = azurerm_security_center_subscription_pricing.main.tier
    storage_accounts   = azurerm_security_center_subscription_pricing.storage.tier
    sql_servers        = azurerm_security_center_subscription_pricing.sql.tier
    container_registry = azurerm_security_center_subscription_pricing.containers.tier
    kubernetes_service = azurerm_security_center_subscription_pricing.kubernetes.tier
  }
}

output "security_alerts" {
  description = "Security monitoring alerts configuration"
  value = {
    key_vault_access_alert_id = azurerm_monitor_activity_log_alert.key_vault_access.id
    admin_activity_alert_id   = azurerm_monitor_activity_log_alert.admin_activity.id
  }
}

output "security_policies" {
  description = "Custom security policies"
  value = {
    require_encryption_policy_id    = azurerm_policy_definition.require_encryption.id
    require_encryption_assignment_id = azurerm_policy_assignment.require_encryption.id
  }
}

output "log_analytics_queries" {
  description = "Security monitoring queries"
  value = {
    failed_logins_query_id        = azurerm_log_analytics_saved_search.failed_logins.id
    privileged_operations_query_id = azurerm_log_analytics_saved_search.privileged_operations.id
  }
}

output "sentinel_connectors" {
  description = "Microsoft Sentinel data connectors"
  value = var.enable_sentinel ? {
    aad_connector_id = azurerm_sentinel_data_connector_azure_active_directory.main[0].id
    asc_connector_id = azurerm_sentinel_data_connector_azure_security_center.main[0].id
  } : null
}

output "security_configuration" {
  description = "Security configuration summary"
  value = {
    waf_mode                    = var.waf_mode
    ddos_protection_enabled     = var.enable_ddos_protection
    backup_enabled              = var.enable_backup
    sentinel_enabled            = var.enable_sentinel
    security_center_tier        = var.security_center_tier
    backup_retention_days       = var.backup_retention_days
    compliance_frameworks       = var.compliance_frameworks
    encryption_at_rest_cmk      = var.encryption_at_rest_cmk
    tls_version                = var.encryption_in_transit_tls_version
  }
}

output "security_endpoints" {
  description = "Security monitoring endpoints"
  value = {
    security_center_url = "https://portal.azure.com/#blade/Microsoft_Azure_Security/SecurityMenuBlade/0"
    sentinel_url       = var.enable_sentinel ? "https://portal.azure.com/#blade/Microsoft_Azure_Security_Insights/MainMenuBlade" : null
    backup_vault_url   = var.enable_backup ? "https://portal.azure.com/#@/resource${azurerm_data_protection_backup_vault.main[0].id}" : null
  }
}

output "security_contact_info" {
  description = "Security contact information"
  value = {
    email = var.security_contact_email
    phone = var.security_contact_phone
  }
  sensitive = true
}

output "waf_configuration" {
  description = "WAF configuration details"
  value = {
    policy_name              = azurerm_web_application_firewall_policy.main.name
    mode                    = var.waf_mode
    owasp_version          = var.waf_owasp_version
    file_upload_limit_mb   = var.waf_file_upload_limit_mb
    max_request_body_size_kb = var.waf_max_request_body_size_kb
    blocked_countries      = var.waf_blocked_countries
  }
}

output "network_security_rules" {
  description = "Network security rules summary"
  value = {
    web_tier_nsg_name = azurerm_network_security_group.web_tier.name
    security_rules = [
      {
        name        = "AllowHTTPS"
        port        = "443"
        protocol    = "TCP"
        direction   = "Inbound"
        access      = "Allow"
      },
      {
        name        = "AllowHTTP"
        port        = "80"
        protocol    = "TCP"
        direction   = "Inbound"
        access      = "Allow"
      },
      {
        name        = "DenyDirectDBAccess"
        port        = "5432"
        protocol    = "TCP"
        direction   = "Inbound"
        access      = "Deny"
      }
    ]
  }
}

output "compliance_status" {
  description = "Compliance framework status"
  value = {
    enabled_frameworks = var.compliance_frameworks
    data_classification = var.data_classification_levels
    security_baseline  = var.security_baseline
    baseline_version   = var.security_baseline_version
  }
}

output "threat_protection_config" {
  description = "Threat protection configuration"
  value = {
    advanced_threat_protection = var.advanced_threat_protection
    threat_intelligence_feeds  = var.threat_intelligence_feeds
    auto_remediation_enabled   = var.auto_remediation_enabled
  }
}

# Environment variables for services to use security features
output "security_environment_variables" {
  description = "Environment variables for services to integrate with security features"
  value = {
    # WAF
    WAF_POLICY_ID = azurerm_web_application_firewall_policy.main.id
    
    # Security monitoring
    SECURITY_MONITORING_ENABLED = "true"
    FAILED_LOGIN_THRESHOLD      = tostring(var.failed_login_threshold)
    
    # Compliance
    COMPLIANCE_FRAMEWORKS = join(",", var.compliance_frameworks)
    DATA_ENCRYPTION_REQUIRED = tostring(var.encryption_at_rest_cmk)
    MIN_TLS_VERSION         = var.encryption_in_transit_tls_version
    
    # Backup
    BACKUP_ENABLED = tostring(var.enable_backup)
    BACKUP_RETENTION_DAYS = tostring(var.backup_retention_days)
    
    # Security features
    ADVANCED_THREAT_PROTECTION = tostring(var.advanced_threat_protection)
    SECURITY_BASELINE         = var.security_baseline
  }
}

output "security_monitoring_queries" {
  description = "KQL queries for security monitoring"
  value = {
    failed_logins = azurerm_log_analytics_saved_search.failed_logins.query
    privileged_operations = azurerm_log_analytics_saved_search.privileged_operations.query
  }
}
