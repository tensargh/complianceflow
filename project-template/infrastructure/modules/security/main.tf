# Security Module for Compliance Flow
# Implements comprehensive security controls and monitoring

# Azure Security Center
resource "azurerm_security_center_subscription_pricing" "main" {
  tier          = var.security_center_tier
  resource_type = "VirtualMachines"
}

resource "azurerm_security_center_subscription_pricing" "storage" {
  tier          = var.security_center_tier
  resource_type = "StorageAccounts"
}

resource "azurerm_security_center_subscription_pricing" "sql" {
  tier          = var.security_center_tier
  resource_type = "SqlServers"
}

resource "azurerm_security_center_subscription_pricing" "containers" {
  tier          = var.security_center_tier
  resource_type = "ContainerRegistry"
}

resource "azurerm_security_center_subscription_pricing" "kubernetes" {
  tier          = var.security_center_tier
  resource_type = "KubernetesService"
}

# Security Center Contact
resource "azurerm_security_center_contact" "main" {
  email = var.security_contact_email
  phone = var.security_contact_phone

  alert_notifications = true
  alerts_to_admins   = true
}

# Web Application Firewall Policy
resource "azurerm_web_application_firewall_policy" "main" {
  name                = "${var.name_prefix}-waf-policy"
  resource_group_name = var.resource_group_name
  location            = var.location
  tags                = var.tags

  policy_settings {
    enabled                     = true
    mode                       = var.waf_mode
    request_body_check         = true
    file_upload_limit_in_mb    = var.waf_file_upload_limit_mb
    max_request_body_size_in_kb = var.waf_max_request_body_size_kb
  }

  managed_rules {
    exclusion {
      match_variable          = "RequestHeaderNames"
      selector_match_operator = "Equals"
      selector                = "x-company-secret-header"
    }

    managed_rule_set {
      type    = "OWASP"
      version = var.waf_owasp_version
      
      rule_group_override {
        rule_group_name = "REQUEST-920-PROTOCOL-ENFORCEMENT"
        
        rule {
          id      = "920300"
          enabled = true
          action  = "Log"
        }
      }
    }

    managed_rule_set {
      type    = "Microsoft_BotManagerRuleSet"
      version = "0.1"
    }
  }

  custom_rules {
    name      = "RateLimitRule"
    priority  = 1
    rule_type = "RateLimitRule"

    match_conditions {
      match_variables {
        variable_name = "RemoteAddr"
      }

      operator           = "IPMatch"
      negation_condition = false
      match_values       = ["192.168.1.0/24", "10.0.0.0/8"]
    }

    action = "Block"

    rate_limit_duration_in_minutes = 1
    rate_limit_threshold          = 10
  }

  custom_rules {
    name      = "GeoBlockRule"
    priority  = 2
    rule_type = "MatchRule"

    match_conditions {
      match_variables {
        variable_name = "RemoteAddr"
      }

      operator           = "GeoMatch"
      negation_condition = false
      match_values       = var.waf_blocked_countries
    }

    action = "Block"
  }
}

# Network Security Groups with Enhanced Rules
resource "azurerm_network_security_group" "web_tier" {
  name                = "${var.name_prefix}-web-nsg"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "DenyDirectDBAccess"
    priority                   = 4000
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "DenyRDP"
    priority                   = 4001
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3389"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "DenySSH"
    priority                   = 4002
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# DDoS Protection Plan
resource "azurerm_network_ddos_protection_plan" "main" {
  count               = var.enable_ddos_protection ? 1 : 0
  name                = "${var.name_prefix}-ddos-protection"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

# Private DNS Zones for secure internal communication
resource "azurerm_private_dns_zone" "internal" {
  name                = "${var.name_prefix}.internal"
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

# Key Vault Advanced Access Policies
resource "azurerm_key_vault_access_policy" "security_admin" {
  key_vault_id = var.key_vault_id
  tenant_id    = var.tenant_id
  object_id    = var.security_admin_object_id

  key_permissions = [
    "Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import",
    "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", "Update",
    "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "SetRotationPolicy"
  ]

  secret_permissions = [
    "Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"
  ]

  certificate_permissions = [
    "Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers",
    "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers",
    "Purge", "Recover", "Restore", "SetIssuers", "Update"
  ]
}

# Diagnostic Settings for Security Monitoring
resource "azurerm_monitor_diagnostic_setting" "key_vault" {
  name               = "${var.name_prefix}-kv-diagnostics"
  target_resource_id = var.key_vault_id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "AuditEvent"
  }

  enabled_log {
    category = "AzurePolicyEvaluationDetails"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

# Security Alerts
resource "azurerm_monitor_activity_log_alert" "key_vault_access" {
  name                = "${var.name_prefix}-kv-access-alert"
  resource_group_name = var.resource_group_name
  scopes              = [var.key_vault_id]
  description         = "Alert on Key Vault access outside business hours"
  tags                = var.tags

  criteria {
    resource_id    = var.key_vault_id
    operation_name = "Microsoft.KeyVault/vaults/secrets/read"
    category       = "Security"
    level         = "Warning"
  }

  action {
    action_group_id = var.security_action_group_id
  }
}

resource "azurerm_monitor_activity_log_alert" "admin_activity" {
  name                = "${var.name_prefix}-admin-activity-alert"
  resource_group_name = var.resource_group_name
  scopes              = ["/subscriptions/${var.subscription_id}"]
  description         = "Alert on administrative activities"
  tags                = var.tags

  criteria {
    category = "Administrative"
    level   = "Critical"
  }

  action {
    action_group_id = var.security_action_group_id
  }
}

# Backup Vault for Critical Data
resource "azurerm_data_protection_backup_vault" "main" {
  count               = var.enable_backup ? 1 : 0
  name                = "${var.name_prefix}-backup-vault"
  resource_group_name = var.resource_group_name
  location            = var.location
  datastore_type      = "VaultStore"
  redundancy          = var.backup_redundancy
  tags                = var.tags

  identity {
    type = "SystemAssigned"
  }
}

# Backup Policy for Databases
resource "azurerm_data_protection_backup_policy_postgresql" "main" {
  count              = var.enable_backup ? 1 : 0
  name               = "${var.name_prefix}-db-backup-policy"
  resource_group_name = var.resource_group_name
  vault_name         = azurerm_data_protection_backup_vault.main[0].name

  backup_repeating_time_intervals = ["R/2024-01-01T02:00:00+00:00/P1D"]
  default_retention_duration      = "P${var.backup_retention_days}D"

  retention_rule {
    name     = "weekly"
    duration = "P4W"
    priority = 20

    criteria {
      absolute_criteria = "FirstOfWeek"
    }
  }

  retention_rule {
    name     = "monthly"
    duration = "P12M"
    priority = 15

    criteria {
      absolute_criteria = "FirstOfMonth"
    }
  }
}

# Log Analytics Queries for Security Monitoring
resource "azurerm_log_analytics_saved_search" "failed_logins" {
  name                       = "FailedLogins"
  log_analytics_workspace_id = var.log_analytics_workspace_id
  category                   = "Security"
  display_name              = "Failed Login Attempts"
  query                     = <<QUERY
SigninLogs
| where TimeGenerated > ago(1h)
| where Status.errorCode != 0
| summarize count() by UserPrincipalName, IPAddress
| where count_ > ${var.failed_login_threshold}
| order by count_ desc
QUERY
  tags                      = var.tags
}

resource "azurerm_log_analytics_saved_search" "privileged_operations" {
  name                       = "PrivilegedOperations"
  log_analytics_workspace_id = var.log_analytics_workspace_id
  category                   = "Security"
  display_name              = "Privileged Operations"
  query                     = <<QUERY
AzureActivity
| where TimeGenerated > ago(1h)
| where CategoryValue == "Administrative"
| where ActivityStatusValue == "Success"
| where CallerIpAddress !startswith "10."
| summarize count() by Caller, CallerIpAddress, OperationNameValue
| order by count_ desc
QUERY
  tags                      = var.tags
}

# Microsoft Sentinel (if enabled)
resource "azurerm_sentinel_data_connector_azure_active_directory" "main" {
  count                      = var.enable_sentinel ? 1 : 0
  name                       = "${var.name_prefix}-aad-connector"
  log_analytics_workspace_id = var.log_analytics_workspace_id
}

resource "azurerm_sentinel_data_connector_azure_security_center" "main" {
  count                      = var.enable_sentinel ? 1 : 0
  name                       = "${var.name_prefix}-asc-connector"
  log_analytics_workspace_id = var.log_analytics_workspace_id
}

# Custom Security Policies
resource "azurerm_policy_definition" "require_encryption" {
  name         = "${var.name_prefix}-require-encryption"
  policy_type  = "Custom"
  mode         = "Indexed"
  display_name = "Require encryption for storage accounts"

  policy_rule = jsonencode({
    if = {
      field = "type"
      equals = "Microsoft.Storage/storageAccounts"
    }
    then = {
      effect = "audit"
      details = {
        type = "Microsoft.Storage/storageAccounts/encryptionSettings"
        existenceCondition = {
          field = "Microsoft.Storage/storageAccounts/encryptionSettings.enabled"
          equals = "true"
        }
      }
    }
  })

  metadata = jsonencode({
    category = "Storage"
  })
}

resource "azurerm_policy_assignment" "require_encryption" {
  name                 = "${var.name_prefix}-require-encryption-assignment"
  scope                = "/subscriptions/${var.subscription_id}/resourceGroups/${var.resource_group_name}"
  policy_definition_id = azurerm_policy_definition.require_encryption.id
  display_name         = "Require encryption for storage accounts"
  description          = "This policy audits storage accounts that do not have encryption enabled"
}
