variable "tfstate_resource_group_name" {
  type        = string
  description = "TF State Resource group name"
}

variable "tfstate_storage_account_name" {
  type        = string
  description = "TF State Storage account name"
}

variable "tfstate_container_name" {
  type        = string
  description = "TF Container name"
}

variable "location" {
  type        = string
  description = "Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created."
}

variable "deployment_source" {
  type        = string
  description = "The deployment source (e.g dev)"
}

variable "peer_with_pipeline" {
  type        = bool
  description = "Specifies whether the infrastructure should be paired with the virtual network of the pipeline"
}

variable "random_suffix" {
  type        = string
  description = "The suffix appended to the resource names"
}

variable "rg_name" {
  type        = string
  description = "The name of the resource group"
}

variable "vnet_address_space" {
  type        = string
  description = "The IP range of the virtual network"
}

variable "integration_subnet_address_space" {
  type        = string
  description = "The IP range of the integration subnet"
}

variable "gateway_subnet_address_space" {
  type        = string
  description = "The IP range of the gateway subnet"
}

variable "dns_resolver_subnet_address_space" {
  type        = string
  description = "The IP range of the subnet for the dns resolver"
}

variable "vpn_client_address_space" {
  type        = string
  description = "The IP range for the vpn clients connecting to the gateway"
}

variable "vnet_gateway_sku" {
  type        = string
  description = "The sku for the virtual network gateway"
}

variable "vnet_enabled" {
  type        = bool
  description = "Specifies whether to deploy resources behind a VNET or not"
}
