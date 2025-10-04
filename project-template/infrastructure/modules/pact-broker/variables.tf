# Variables for Pact Broker Module

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

variable "container_app_environment_id" {
  description = "The ID of the Container App Environment"
  type        = string
}

variable "database_connection_string" {
  description = "PostgreSQL connection string for Pact Broker"
  type        = string
  sensitive   = true
}

variable "postgresql_server_id" {
  description = "The ID of the PostgreSQL server"
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "The ID of the Log Analytics workspace"
  type        = string
}

variable "action_group_id" {
  description = "The ID of the action group for alerts"
  type        = string
}

variable "basic_auth_username" {
  description = "Username for Pact Broker basic authentication"
  type        = string
  default     = "pact_broker"
}

variable "basic_auth_password" {
  description = "Password for Pact Broker basic authentication"
  type        = string
  sensitive   = true
}

variable "readonly_username" {
  description = "Read-only username for Pact Broker"
  type        = string
  default     = "readonly"
}

variable "readonly_password" {
  description = "Read-only password for Pact Broker"
  type        = string
  sensitive   = true
}

variable "webhook_host_whitelist" {
  description = "Whitelist of hosts that can receive webhooks"
  type        = string
  default     = "github.com,api.github.com"
}

variable "log_level" {
  description = "Log level for Pact Broker"
  type        = string
  default     = "INFO"
  validation {
    condition = contains([
      "DEBUG", "INFO", "WARN", "ERROR"
    ], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARN, ERROR."
  }
}

variable "custom_domain" {
  description = "Custom domain for Pact Broker (optional)"
  type        = string
  default     = ""
}

variable "dns_zone_name" {
  description = "DNS zone name for custom domain"
  type        = string
  default     = ""
}

variable "dns_zone_resource_group" {
  description = "Resource group containing the DNS zone"
  type        = string
  default     = ""
}

variable "enable_ssl" {
  description = "Enable SSL/TLS for Pact Broker"
  type        = bool
  default     = true
}

variable "cpu_limit" {
  description = "CPU limit for Pact Broker container"
  type        = number
  default     = 0.5
  validation {
    condition     = var.cpu_limit >= 0.25 && var.cpu_limit <= 4
    error_message = "CPU limit must be between 0.25 and 4."
  }
}

variable "memory_limit" {
  description = "Memory limit for Pact Broker container"
  type        = string
  default     = "1Gi"
}

variable "min_replicas" {
  description = "Minimum number of replicas"
  type        = number
  default     = 1
  validation {
    condition     = var.min_replicas >= 0 && var.min_replicas <= 10
    error_message = "Minimum replicas must be between 0 and 10."
  }
}

variable "max_replicas" {
  description = "Maximum number of replicas"
  type        = number
  default     = 3
  validation {
    condition     = var.max_replicas >= 1 && var.max_replicas <= 10
    error_message = "Maximum replicas must be between 1 and 10."
  }
}

variable "scale_concurrent_requests" {
  description = "Number of concurrent requests to trigger scaling"
  type        = number
  default     = 100
}
