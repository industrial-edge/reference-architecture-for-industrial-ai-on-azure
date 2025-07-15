
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
  type        = string
  description = "(Required) Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created."
  default     = "westeurope"
}

variable "deployment_source" {
  type        = string
  description = "The deployment source (e.g dev)"
  default     = "dev"
}

variable "peer_with_pipeline" {
  type        = bool
  description = "Specifies whether the infrastructure should be paired with the virtual network of the pipeline"
  default     = false
}

variable "vnet_address_space" {
  type        = string
  description = "The IP range of the virtual network"
  default     = "10.0.0.0/16"
}

variable "integration_subnet_address_space" {
  type        = string
  description = "The IP range of the integration subnet"
  default     = "10.0.2.0/24"
}

variable "vnet_enabled" {
  type        = bool
  description = "Specifies whether to deploy resources behind a VNET or not"
  default     = false
}

variable "kv_sku_name" {
  type        = string
  description = "Specifies the price of Key Vault Azure resource. 'standard' and 'premium' is available."
  default     = "standard"
}

variable "application_insights_app_type" {
  type        = string
  description = " (Required) Specifies the type of Application Insights to create. Please note these values are case sensitive; unmatched values are treated as ASP.NET by Azure. Changing this forces a new resource to be created"
  default     = "web"

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
  type        = string
  description = "(Required) Specifies the severity of this Smart Detector Alert Rule"
  default     = "Sev3"
}

variable "failure_anomaly_frequency" {
  type        = string
  description = "(Required) Specifies the frequency of this Smart Detector Alert Rule in ISO8601 format."
  default     = "PT1M"
}

variable "kv_soft_delete_retention_days" {
  type        = number
  description = "(Optional) The number of days that items should be retained for, once soft-deleted. This value can be between 7 and 90 (the default) days."
  default     = 7
}

variable "storage_mngmnt_policy_kv_logs_rule_name" {
  type        = string
  description = "(Required) The name of the rule for the storage account management policy used to set the retention policy for the Key Vault logs."
  default     = "Diagnostic Settings Retention Rule"
}

variable "storage_mngmnt_policy_kv_logs_delete_after" {
  type        = number
  description = "The age in days after creation to delete the blob that stores the logs for the Key Vault"
  default     = 14
}

variable "app_insights_local_auth_disabled" {
  type        = string
  description = "Disable Non-Azure AD based Auth. Defaults to false."
  default     = "true"
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
  type        = string
  description = "The IP range of the training subnet"
  default     = "10.0.1.0/24"
}

variable "ml_container_registry_sku" {
  type        = string
  description = "(Required) The SKU name of the container registry. Possible values are Basic, Standard and Premium."
  default     = "Premium"
}

variable "ml_container_registry_admin_enabled" {
  type        = bool
  description = "(Optional) Specifies whether the admin user is enabled. Defaults to false"
  default     = true
}

variable "ml_sa_account_kind" {
  type        = string
  description = "(Optional) Defines the Kind of account."
  default     = "StorageV2"

  validation {
    condition     = contains(["BlobStorage", "BlockBlobStorage", "FileStorage", "Storage", "StorageV2"], var.ml_sa_account_kind)
    error_message = "Account Kind is not set to a valid option."
  }
}

variable "ml_sa_account_tier" {
  type        = string
  description = "(Optional) Defines the Tier to use for this storage account."
  default     = "Standard"

  validation {
    condition     = contains(["Standard", "Premium"], var.ml_sa_account_tier)
    error_message = "Account Tier is not set to a valid option."
  }
}

variable "ml_sa_account_replication_type" {
  type        = string
  description = "(Optional) Defines the type of replication to use for this storage account."
  default     = "LRS"

  validation {
    condition     = contains(["LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"], var.ml_sa_account_replication_type)
    error_message = "Account replication type is not set to a valid option."
  }
}

variable "ml_sa_access_tier" {
  type        = string
  description = "(Optional) Defines the access tier for BlobStorage, FileStorage and StorageV2 accounts."
  default     = "Hot"

  validation {
    condition     = contains(["Hot", "Cool"], var.ml_sa_access_tier)
    error_message = "Account access tier is not set to a valid option."
  }
}

variable "ml_compute_cluster_vm_priority" {
  type        = string
  description = "(Required) The priority of the Virtual Machine. Changing this forces a new Machine Learning Compute Cluster to be created."
  default     = "LowPriority"
  validation {
    condition     = contains(["LowPriority", "Dedicated"], var.ml_compute_cluster_vm_priority)
    error_message = "Virtual Machine Priority is not set to a valid option"
  }

}

variable "ml_compute_cluster_vm_size" {
  type        = string
  description = "(Required) The size of the Virtual Machine. Changing this forces a new Machine Learning Compute Cluster to be created."
  default     = "STANDARD_DS11_V2"
}

variable "ml_cc_scale_settings_min_node_count" {
  type        = number
  description = "(Required) Minimum node count. Changing this forces a new Machine Learning Compute Cluster to be created."
  default     = 0
}

variable "ml_cc_scale_settings_max_node_count" {
  type        = number
  description = "(Required) Maximum node count. Changing this forces a new Machine Learning Compute Cluster to be created."
  default     = 2
}

variable "ml_cc_scale_down_after_idle_duration" {
  type        = string
  description = "(Required) Node Idle Time Before Scale Down: defines the time until the compute is shutdown when it has gone into Idle state. Is defined according to W3C XML schema standard for duration. Changing this forces a new Machine Learning Compute Cluster to be created."
  default     = "PT30M"
}

##################################
# IoT Management Variables #
##################################
variable "iothub_sku_name" {
  type        = string
  description = "(Required) The name of the sku. Possible values are B1, B2, B3, F1, S1, S2, and S3."
  validation {
    condition     = contains(["B1", "B2", "B3", "F1", "S1", "S2", "S3"], var.iothub_sku_name)
    error_message = "IoT Hub sku is not set to a valid option."
  }
  default = "S1"
}

variable "iothub_sku_capacity" {
  type        = number
  description = "(Required) The number of provisioned IoT Hub units."
  default     = 1
}

variable "iothub_eventhub_shared_access_policy_name" {
  type        = string
  default     = "iothubowner"
  description = "The name of the shared access policy of the IoT Hub"
}

variable "model_manager_pipeline_service_principal_id" {
  type        = string
  description = "The name ObjectId of the Service Principal used in the Create Model Monitor Identity Pipeline"
  default     = "699f8419-c718-45a1-b344-ebac3c7ac74b"
}

variable "model_monitor_identity_pipeline_principal_id" {
  type        = string
  description = "The Id of the Principal for the Model Monitor pipeline"
  default     = "1b31493e-c397-48e6-9d03-6e78a5b03f64"
}
