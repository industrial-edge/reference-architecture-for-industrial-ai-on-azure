variable "location" {
  type        = string
  description = "(Required) Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created."
}

variable "deployment_source" {
  type        = string
  description = "The deployment source (e.g dev)"
}

variable "random_suffix" {
  type        = string
  description = "The suffix appended to the resource names"
}

variable "rg_name" {
  type        = string
  description = "The name of the resource group"
}

variable "vnet_enabled" {
  type        = bool
  description = "Specifies whether to deploy resources behind a VNET or not"
}

variable "vnet_id" {
  type        = string
  description = "The id of the virtual network"
}

variable "integration_subnet_id" {
  type        = string
  description = "The id range of the integration subnet for private endpoints"
}

variable "kv_private_dns_zone_id" {
  type = string
  description = "The private dns zone Id for the key vault"
}

variable "kv_sku_name" {
  type        = string
  description = "Specifies the price of Key Vault Azure resource. 'standard' and 'premium' is available."
}

variable "log_analytics_workspace_retention" {
  type        = number
  description = "The workspace data retention in days. Possible values are either 7 (Free Tier only) or range between 30 and 730. The Free SKU has a default daily_quota_gb value of 0.5 (GB)"
}

variable "log_analytics_workspace_sku" {
  type        = string
  description = "Specifies the SKU of the Log Analytics Workspace."
}

variable "application_insights_app_type" {
  type        = string
  description = "Specifies the type of Application Insights to create. Please note these values are case sensitive; unmatched values are treated as ASP.NET by Azure. Changing this forces a new resource to be created"
}

variable "failure_anomaly_severity" {
  type        = string
  description = "Specifies the severity of this Smart Detector Alert Rule"
}

variable "failure_anomaly_frequency" {
  type        = string
  description = "Specifies the frequency of this Smart Detector Alert Rule in ISO8601 format."
}

variable "storage_account_account_tier" {
  type        = string
  description = "Defines the tier to use for the storage account"
  default     = "Standard"
}

variable "storage_account_account_replication_type" {
  type        = string
  description = "Defines the type of replication to use for the storage account"
  default     = "LRS"
}

variable "storage_mngmnt_policy_kv_logs_rule_name" {
  type        = string
  description = "The name of the rule for the storage account management policy used to set the retention policy for the Key Vault logs."
}

variable "storage_mngmnt_policy_kv_logs_delete_after" {
  type        = string
  description = "The age in days after creation to delete the blob."
}

variable "kv_soft_delete_retention_days" {
  type        = number
  description = "The number of days that items should be retained for, once soft-deleted. This value can be between 7 and 90 (the default) days."
}

variable "app_insights_local_auth_disabled" {
  type        = string
  description = "Disable Non-Azure AD based Auth. Defaults to false."
}
variable "model_manager_pipeline_service_principal_id" {
  type        = string
  description = "The name ObjectId of the service principal used in the Create Model Manager Identity Pipeline"
}

variable "model_monitor_identity_pipeline_principal_id" {
  type = string
  description = "The Id of the Principal for the Model Monitor pipeline"
}
