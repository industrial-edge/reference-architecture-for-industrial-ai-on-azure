
variable "resource_group_name" {
  type        = string
  description = "TF State Resource group name"
}

variable "storage_account_name" {
  type        = string
  description = "TF State Storage account name"
}

variable "container_name" {
  type        = string
  description = "TF Container name"
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "deployment_source" {
  type    = string
  default = "test"
}

variable "vnet_address_space" {
  type    = string
  default = "10.0.0.0/16"
}

variable "integration_subnet_address_space" {
  type    = string
  default = "10.0.2.0/24"
}

variable "vnet_enabled" {
  type    = bool
  default = false
}

variable "kv_sku_name" {
  type    = string
  default = "standard"
}

variable "application_insights_app_type" {
  type    = string
  default = "web"

  validation {
    condition     = contains(["ios", "java", "MobileCenter", "Node.js", "other", "phone", "store", "web"], var.application_insights_app_type)
    error_message = "Application Insights Application Type is not set to a valid option."
  }
}

variable "log_analytics_workspace_sku" {
  type        = string
  description = "(Optional) Specifies the SKU of the Log Analytics Workspace.  Defaults to PerGB2018"
  default     = "PerGB2018"

  validation {
    condition     = contains(["Free", "PerNode", "Standard", "Standalone", "Unlimited", "CapacityReservation", "PerGB2018"], var.log_analytics_workspace_sku)
    error_message = "Log Anlytics Workspace SKU is not set to a valid option."
  }
}

variable "log_analytics_workspace_retention" {
  type        = number
  description = " (Optional) The workspace data retention in days. Possible values are either 7 (Free Tier only) or range between 30 and 730. The Free SKU has a default daily_quota_gb value of 0.5 (GB)"
  default     = 30
}

variable "failure_anomaly_severity" {
  type    = string
  default = "Sev3"
}

variable "failure_anomaly_frequency" {
  type    = string
  default = "PT1M"
}

variable "kv_soft_delete_retention_days" {
  type    = number
  default = 7
}

variable "storage_mngmnt_policy_kv_logs_rule_name" {
  type    = string
  default = "Diagnostic Settings Retention Rule"
}

variable "storage_mngmnt_policy_kv_logs_delete_after" {
  type    = number
  default = 14
}

variable "app_insights_local_auth_disabled" {
  type        = string
  description = "Disable Non-Azure AD based Auth. Defaults to false."
  default     = "true"
}

variable "peer_with_pipeline" {
  type        = bool
  description = "Specifies whether the infrastructure should be paired with the virtual network of the pipeline"
  default     = false
}

###############################
##  Virtual Network Gateway  ##
###############################

variable "gateway_subnet_address_space" {
  type        = string
  description = "The IP range of the gateway subnet"
  default     = "10.0.3.0/24"
}

variable "dns_resolver_subnet_address_space" {
  type        = string
  description = "The IP range of the subnet for the dns resolver"
  default     = "10.0.4.0/24"
}

variable "vpn_client_address_space" {
  type        = string
  description = "The IP range for the vpn clients connecting to the gateway"
  default     = "10.10.0.0/16"
}

variable "vnet_gateway_sku" {
  type        = string
  description = "The sku for the virtual network gateway"
  default     = "VpnGw2"
}

##################################
# MLOps Variables #
##################################

variable "training_subnet_address_range" {
  type    = string
  default = "10.0.1.0/24"
}

variable "ml_container_registry_sku" {
  type    = string
  default = "Premium"
}

variable "ml_container_registry_admin_enabled" {
  type    = bool
  default = true
}

variable "ml_sa_account_kind" {
  type    = string
  default = "StorageV2"

  validation {
    condition     = contains(["BlobStorage", "BlockBlobStorage", "FileStorage", "Storage", "StorageV2"], var.ml_sa_account_kind)
    error_message = "Account Kind is not set to a valid option."
  }
}

variable "ml_sa_account_tier" {
  type    = string
  default = "Standard"

  validation {
    condition     = contains(["Standard", "Premium"], var.ml_sa_account_tier)
    error_message = "Account Tier is not set to a valid option."
  }
}

variable "ml_sa_account_replication_type" {
  type    = string
  default = "LRS"

  validation {
    condition     = contains(["LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"], var.ml_sa_account_replication_type)
    error_message = "Account replication type is not set to a valid option."
  }
}

variable "ml_sa_access_tier" {
  type    = string
  default = "Hot"

  validation {
    condition     = contains(["Hot", "Cool"], var.ml_sa_access_tier)
    error_message = "Account access tier is not set to a valid option."
  }
}

variable "ml_compute_cluster_vm_priority" {
  type    = string
  default = "LowPriority"
  validation {
    condition     = contains(["LowPriority", "Dedicated"], var.ml_compute_cluster_vm_priority)
    error_message = "Virtual Machine Priority is not set to a valid option"
  }

}

variable "ml_compute_cluster_vm_size" {
  type    = string
  default = "STANDARD_DS2_V2"
}

variable "ml_cc_scale_settings_min_node_count" {
  type    = number
  default = 0
}

variable "ml_cc_scale_settings_max_node_count" {
  type    = number
  default = 2
}

variable "ml_cc_scale_down_after_idle_duration" {
  type    = string
  default = "PT20S"
}

##################################
# IoT Management Variables #
##################################
variable "iothub_sku_name" {
  type = string
  validation {
    condition     = contains(["B1", "B2", "B3", "F1", "S1", "S2", "S3"], var.iothub_sku_name)
    error_message = "IoT Hub sku is not set to a valid option."
  }
  default = "S1"
}

variable "iothub_sku_capacity" {
  type    = number
  default = 1
}

variable "iothub_eventhub_shared_access_policy_name" {
  type        = string
  default     = "iothubowner"
  description = "The name of the shared access policy of the IoT Hub"
}

variable "model_manager_pipeline_service_principal_id" {
  type        = string
  description = "The name ObjectId of the Service Principal used in the Create Model Monitor Identity Pipeline"
  default = "699f8419-c718-45a1-b344-ebac3c7ac74b"
}

variable "model_monitor_identity_pipeline_principal_id" {
  type = string
  description = "The Id of the Principal for the Model Monitor pipeline"
  default = "1b31493e-c397-48e6-9d03-6e78a5b03f64"
}
