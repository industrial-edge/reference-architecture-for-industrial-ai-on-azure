##################################
# Common variables #
##################################

variable "location" {
  type        = string
  description = "Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created."
}

variable "rg_name" {
  type        = string
  description = "The name of the resource group"
}

variable "kv_id" {
  type        = string
  description = "The id of the keyvault"
}

variable "vnet_id" {
  type        = string
  description = "The id of the virtual network"
}

variable "vnet_name" {
  type        = string
  description = "The name of the virtual network"
}

variable "integration_subnet_id" {
  type        = string
  description = "The id range of the integration subnet for private endpoints"
}

variable "deployment_source" {
  type        = string
  description = "The deployment source (e.g dev)"
}

variable "random_suffix" {
  type        = string
  description = "The suffix appended to the resource names"
}

variable "vnet_enabled" {
  type        = bool
  description = "Specifies whether to deploy resources behind a VNET or not"
}

variable "appinsights_id" {
  type        = string
  description = "The id of the application insights"
}

##################################
# MLOps variables #
##################################

variable "container_registry_sku" {
  type        = string
  description = "(Required)The SKU name of the container registry. Possible values are Basic, Standard and Premium."
}

variable "container_registry_admin_enabled" {
  type        = bool
  description = "Specifies whether the admin user is enabled. Defaults to false"
}

variable "sa_account_kind" {
  type        = string
  description = "Defines the Kind of account."
}

variable "sa_account_tier" {
  type        = string
  description = "Defines the Tier to use for this storage account."
}

variable "sa_account_replication_type" {
  type        = string
  description = "Defines the type of replication to use for this storage account."
}

variable "sa_access_tier" {
  type        = string
  description = "Defines the access tier for BlobStorage, FileStorage and StorageV2 accounts."
}

variable "compute_cluster_vm_priority" {
  type        = string
  description = "The priority of the Virtual Machine. Changing this forces a new Machine Learning Compute Cluster to be created."
}

variable "compute_cluster_vm_size" {
  type        = string
  description = "The size of the Virtual Machine. Changing this forces a new Machine Learning Compute Cluster to be created."
}

variable "cc_scale_settings_min_node_count" {
  type        = number
  description = "Minimum node count. Changing this forces a new Machine Learning Compute Cluster to be created."
}

variable "cc_scale_settings_max_node_count" {
  type        = number
  description = "Maximum node count. Changing this forces a new Machine Learning Compute Cluster to be created."
}

variable "cc_scale_down_after_idle_duration" {
  type        = string
  description = "Node Idle Time Before Scale Down: defines the time until the compute is shutdown when it has gone into Idle state. Is defined according to W3C XML schema standard for duration. Changing this forces a new Machine Learning Compute Cluster to be created."
}

variable "training_subnet_address_range" {
  type        = string
  description = "The IP range of the training subnet"
}

##MLOps VNET##
variable "private_dns_zone_id_stg_blob" {
  type = string
  description = "The private dns zone Id for the blob storage"
}

variable "cr_private_dns_zone_id" {
  type = string
  description = "The private dns zone Id for the container registry"
}

variable "ml_private_dns_zone_id" {
  type = string
  description = "The private dns zone Id for the ml workspace"
}
