variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-manufacturing-hardened-prod"
}

variable "location" {
  description = "Azure region for deployment"
  type        = string
  default     = "centralindia"
}

variable "sql_admin_login" {
  description = "SQL administrator login"
  type        = string
  default     = "sqladmin"
}

variable "sql_admin_password" {
  description = "SQL administrator password"
  type        = string
  sensitive   = true
}
