# Variables for Enhanced Monitoring Module

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

variable "retention_in_days" {
  description = "Number of days to retain logs and metrics"
  type        = number
  default     = 90
}

variable "daily_quota_gb" {
  description = "Daily quota for Log Analytics workspace in GB"
  type        = number
  default     = 10
}

variable "application_type" {
  description = "Type of Application Insights application"
  type        = string
  default     = "web"
  validation {
    condition = contains([
      "web", "java", "HockeyAppBridge", "other", "ios", "phone", "store", "universal", "Node.JS"
    ], var.application_type)
    error_message = "Application type must be one of the supported types."
  }
}

variable "sampling_percentage" {
  description = "Sampling percentage for Application Insights"
  type        = number
  default     = 100
  validation {
    condition     = var.sampling_percentage >= 0 && var.sampling_percentage <= 100
    error_message = "Sampling percentage must be between 0 and 100."
  }
}

variable "services" {
  description = "List of microservices to create Application Insights instances for"
  type        = list(string)
  default = [
    "user-service",
    "declaration-service", 
    "form-service",
    "rule-engine-service",
    "review-service",
    "case-service",
    "notification-service",
    "analytics-service"
  ]
}

variable "container_app_ids" {
  description = "Map of service names to Container App resource IDs for diagnostic settings"
  type        = map(string)
  default     = {}
}

variable "admin_email" {
  description = "Email address for critical alerts"
  type        = string
}

variable "team_email" {
  description = "Email address for team notifications"
  type        = string
  default     = ""
}

variable "admin_phone" {
  description = "Phone number for critical SMS alerts"
  type        = string
  default     = ""
}

variable "sms_country_code" {
  description = "Country code for SMS alerts"
  type        = string
  default     = "1"
}

variable "teams_webhook_url" {
  description = "Microsoft Teams webhook URL for notifications"
  type        = string
  default     = ""
  sensitive   = true
}

variable "enable_custom_logs" {
  description = "Enable custom log collection"
  type        = bool
  default     = false
}

variable "alert_frequency" {
  description = "Frequency for metric alerts"
  type        = string
  default     = "PT1M"
  validation {
    condition = contains([
      "PT1M", "PT5M", "PT15M", "PT30M", "PT1H"
    ], var.alert_frequency)
    error_message = "Alert frequency must be a valid ISO 8601 duration."
  }
}

variable "alert_window_size" {
  description = "Window size for metric alerts"
  type        = string
  default     = "PT5M"
  validation {
    condition = contains([
      "PT1M", "PT5M", "PT15M", "PT30M", "PT1H", "PT6H", "PT12H", "P1D"
    ], var.alert_window_size)
    error_message = "Alert window size must be a valid ISO 8601 duration."
  }
}

variable "error_threshold" {
  description = "Threshold for error rate alerts"
  type        = number
  default     = 10
}

variable "response_time_threshold_ms" {
  description = "Response time threshold in milliseconds"
  type        = number
  default     = 2000
}

variable "availability_threshold" {
  description = "Availability threshold percentage"
  type        = number
  default     = 95
  validation {
    condition     = var.availability_threshold >= 0 && var.availability_threshold <= 100
    error_message = "Availability threshold must be between 0 and 100."
  }
}

variable "enable_smart_detection" {
  description = "Enable Application Insights smart detection"
  type        = bool
  default     = true
}

variable "enable_private_link" {
  description = "Enable private link for monitoring resources"
  type        = bool
  default     = true
}

variable "custom_queries" {
  description = "Map of custom Log Analytics queries"
  type        = map(object({
    display_name = string
    category     = string
    query        = string
  }))
  default = {}
}

variable "dashboard_config" {
  description = "Configuration for monitoring dashboard"
  type = object({
    time_range_hours = optional(number, 24)
    refresh_interval = optional(string, "5m")
    chart_types      = optional(list(string), ["timechart", "table", "piechart"])
  })
  default = {}
}
