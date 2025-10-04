# Variables for Security Module

variable "resource_group_name" {
  description = "The name of the resource group"
  type        = string
}

variable "location" {
  description = "The Azure region where resources will be created"
  type        = string
}

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "tenant_id" {
  description = "Azure tenant ID"
  type        = string
}

variable "key_vault_id" {
  description = "ID of the Key Vault to secure"
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "ID of the Log Analytics workspace"
  type        = string
}

variable "security_action_group_id" {
  description = "ID of the action group for security alerts"
  type        = string
}

# Security Center Configuration
variable "security_center_tier" {
  description = "Pricing tier for Azure Security Center"
  type        = string
  default     = "Standard"
  validation {
    condition     = contains(["Free", "Standard"], var.security_center_tier)
    error_message = "Security Center tier must be either 'Free' or 'Standard'."
  }
}

variable "security_contact_email" {
  description = "Email for security center notifications"
  type        = string
}

variable "security_contact_phone" {
  description = "Phone number for security center notifications"
  type        = string
  default     = ""
}

# WAF Configuration
variable "waf_mode" {
  description = "WAF mode (Detection or Prevention)"
  type        = string
  default     = "Prevention"
  validation {
    condition     = contains(["Detection", "Prevention"], var.waf_mode)
    error_message = "WAF mode must be either 'Detection' or 'Prevention'."
  }
}

variable "waf_file_upload_limit_mb" {
  description = "File upload limit in MB for WAF"
  type        = number
  default     = 100
}

variable "waf_max_request_body_size_kb" {
  description = "Maximum request body size in KB for WAF"
  type        = number
  default     = 128
}

variable "waf_owasp_version" {
  description = "OWASP ruleset version for WAF"
  type        = string
  default     = "3.2"
}

variable "waf_blocked_countries" {
  description = "List of country codes to block in WAF"
  type        = list(string)
  default     = []
}

# Network Security
variable "enable_ddos_protection" {
  description = "Enable DDoS protection plan"
  type        = bool
  default     = false
}

variable "allowed_ip_ranges" {
  description = "List of allowed IP ranges for management access"
  type        = list(string)
  default     = []
}

# Key Vault Security
variable "security_admin_object_id" {
  description = "Object ID of the security administrator"
  type        = string
}

variable "key_vault_purge_protection" {
  description = "Enable purge protection for Key Vault"
  type        = bool
  default     = true
}

variable "key_vault_soft_delete_retention_days" {
  description = "Soft delete retention days for Key Vault"
  type        = number
  default     = 90
  validation {
    condition     = var.key_vault_soft_delete_retention_days >= 7 && var.key_vault_soft_delete_retention_days <= 90
    error_message = "Key Vault soft delete retention must be between 7 and 90 days."
  }
}

# Backup Configuration
variable "enable_backup" {
  description = "Enable backup vault and policies"
  type        = bool
  default     = true
}

variable "backup_redundancy" {
  description = "Backup redundancy type"
  type        = string
  default     = "GeoRedundant"
  validation {
    condition     = contains(["LocallyRedundant", "GeoRedundant"], var.backup_redundancy)
    error_message = "Backup redundancy must be either 'LocallyRedundant' or 'GeoRedundant'."
  }
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
}

# Microsoft Sentinel
variable "enable_sentinel" {
  description = "Enable Microsoft Sentinel SIEM"
  type        = bool
  default     = false
}

# Monitoring and Alerting
variable "failed_login_threshold" {
  description = "Threshold for failed login attempts alert"
  type        = number
  default     = 5
}

variable "enable_security_scanning" {
  description = "Enable security vulnerability scanning"
  type        = bool
  default     = true
}

variable "security_scan_schedule" {
  description = "Schedule for security scans (cron format)"
  type        = string
  default     = "0 2 * * *"  # Daily at 2 AM
}

# Compliance Settings
variable "compliance_frameworks" {
  description = "List of compliance frameworks to enable"
  type        = list(string)
  default     = ["SOC2", "ISO27001"]
  validation {
    condition = length([
      for framework in var.compliance_frameworks :
      framework if contains(["SOC2", "ISO27001", "GDPR", "HIPAA", "PCI-DSS"], framework)
    ]) == length(var.compliance_frameworks)
    error_message = "Compliance frameworks must be from: SOC2, ISO27001, GDPR, HIPAA, PCI-DSS."
  }
}

variable "data_classification_levels" {
  description = "Data classification levels"
  type        = map(object({
    encryption_required = bool
    access_controls     = list(string)
    retention_days     = number
  }))
  default = {
    public = {
      encryption_required = false
      access_controls     = ["AllUsers"]
      retention_days     = 365
    }
    internal = {
      encryption_required = true
      access_controls     = ["EmployeesOnly"]
      retention_days     = 2555  # 7 years
    }
    confidential = {
      encryption_required = true
      access_controls     = ["RestrictedAccess"]
      retention_days     = 2555  # 7 years
    }
    restricted = {
      encryption_required = true
      access_controls     = ["HighlyRestricted"]
      retention_days     = 3650  # 10 years
    }
  }
}

# Incident Response
variable "incident_response_email" {
  description = "Email for incident response notifications"
  type        = string
  default     = ""
}

variable "incident_response_webhook" {
  description = "Webhook URL for incident response system"
  type        = string
  default     = ""
  sensitive   = true
}

variable "auto_remediation_enabled" {
  description = "Enable automatic remediation for security issues"
  type        = bool
  default     = false
}

# Encryption Settings
variable "encryption_at_rest_cmk" {
  description = "Use customer-managed keys for encryption at rest"
  type        = bool
  default     = true
}

variable "encryption_in_transit_tls_version" {
  description = "Minimum TLS version for encryption in transit"
  type        = string
  default     = "1.2"
  validation {
    condition     = contains(["1.2", "1.3"], var.encryption_in_transit_tls_version)
    error_message = "TLS version must be either '1.2' or '1.3'."
  }
}

# Access Control
variable "privileged_access_management" {
  description = "Enable Privileged Access Management (PAM)"
  type        = bool
  default     = true
}

variable "just_in_time_access" {
  description = "Enable Just-In-Time (JIT) access for VMs"
  type        = bool
  default     = true
}

variable "conditional_access_policies" {
  description = "List of conditional access policies to enforce"
  type        = list(object({
    name        = string
    conditions  = map(any)
    controls    = map(any)
  }))
  default = []
}

# Threat Protection
variable "advanced_threat_protection" {
  description = "Enable Advanced Threat Protection for databases"
  type        = bool
  default     = true
}

variable "threat_intelligence_feeds" {
  description = "List of threat intelligence feeds to subscribe to"
  type        = list(string)
  default     = ["Microsoft", "Community"]
}

# Security Baselines
variable "security_baseline" {
  description = "Security baseline to apply"
  type        = string
  default     = "Azure_Security_Benchmark"
  validation {
    condition = contains([
      "Azure_Security_Benchmark",
      "CIS_Azure_Foundations",
      "NIST_SP_800-53"
    ], var.security_baseline)
    error_message = "Security baseline must be a supported framework."
  }
}

variable "security_baseline_version" {
  description = "Version of the security baseline"
  type        = string
  default     = "latest"
}
