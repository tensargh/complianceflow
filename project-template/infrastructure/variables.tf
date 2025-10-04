# Variables for Compliance Flow Infrastructure

# General Configuration
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "East US"
}

variable "cost_center" {
  description = "Cost center for resource tagging"
  type        = string
  default     = "Engineering"
}

variable "owner" {
  description = "Owner for resource tagging"
  type        = string
  default     = "ComplianceFlow Team"
}

# Network Configuration
variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = list(string)
  default     = ["10.0.0.0/16"]
}

variable "subnet_configurations" {
  description = "Subnet configurations"
  type = map(object({
    address_prefixes = list(string)
    service_endpoints = list(string)
    delegation = optional(object({
      name = string
      service_delegation = object({
        name    = string
        actions = list(string)
      })
    }))
  }))
  default = {
    container_apps = {
      address_prefixes = ["10.0.1.0/24"]
      service_endpoints = ["Microsoft.Storage", "Microsoft.KeyVault"]
      delegation = {
        name = "container-apps-delegation"
        service_delegation = {
          name = "Microsoft.App/environments"
          actions = [
            "Microsoft.Network/virtualNetworks/subnets/join/action"
          ]
        }
      }
    }
    database = {
      address_prefixes = ["10.0.2.0/24"]
      service_endpoints = ["Microsoft.Storage"]
    }
    redis = {
      address_prefixes = ["10.0.3.0/24"]
      service_endpoints = []
    }
    storage = {
      address_prefixes = ["10.0.4.0/24"]
      service_endpoints = ["Microsoft.Storage"]
    }
    apim = {
      address_prefixes = ["10.0.5.0/24"]
      service_endpoints = []
    }
  }
}

# Database Configuration
variable "database_sku_name" {
  description = "PostgreSQL SKU name"
  type        = string
  default     = "GP_Standard_D2s_v3"
}

variable "database_storage_mb" {
  description = "PostgreSQL storage in MB"
  type        = number
  default     = 32768
}

variable "database_backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}

variable "database_geo_redundant_backup" {
  description = "Enable geo-redundant backup"
  type        = bool
  default     = false
}

variable "database_admin_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "cfadmin"
}

# Redis Configuration
variable "redis_sku_name" {
  description = "Redis SKU name"
  type        = string
  default     = "Standard"
}

variable "redis_family" {
  description = "Redis family"
  type        = string
  default     = "C"
}

variable "redis_capacity" {
  description = "Redis capacity"
  type        = number
  default     = 1
}

# Kafka Configuration
variable "kafka_environment_name" {
  description = "Confluent Cloud environment name"
  type        = string
  default     = "compliance-flow"
}

variable "kafka_cluster_name" {
  description = "Kafka cluster name"
  type        = string
  default     = "compliance-flow-cluster"
}

variable "kafka_availability" {
  description = "Kafka availability zone configuration"
  type        = string
  default     = "SINGLE_ZONE"
}

variable "kafka_region" {
  description = "Kafka region"
  type        = string
  default     = "eastus"
}

# Container Registry Configuration
variable "container_registry_sku" {
  description = "Container Registry SKU"
  type        = string
  default     = "Standard"
}

# Container Apps Configuration
variable "container_apps_internal_lb" {
  description = "Enable internal load balancer for Container Apps"
  type        = bool
  default     = true
}

# Storage Configuration
variable "storage_account_tier" {
  description = "Storage account tier"
  type        = string
  default     = "Standard"
}

variable "storage_replication_type" {
  description = "Storage replication type"
  type        = string
  default     = "LRS"
}

# Monitoring Configuration
variable "log_analytics_retention_days" {
  description = "Log Analytics retention period in days"
  type        = number
  default     = 30
}

# API Management Configuration (Production only)
variable "apim_sku_name" {
  description = "API Management SKU name"
  type        = string
  default     = "Developer_1"
}

variable "apim_publisher_name" {
  description = "API Management publisher name"
  type        = string
  default     = "Compliance Flow"
}

variable "apim_publisher_email" {
  description = "API Management publisher email"
  type        = string
  default     = "admin@complianceflow.com"
}

