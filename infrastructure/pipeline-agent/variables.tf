# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

variable "location" {
  type        = string
  description = "Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created."
  default     = "westeurope"
}

variable "deployment_source" {
  type        = string
  description = "The deployment source (e.g dev)"
  default     = "agent"
}

variable "sku" {
  type        = string
  description = "The Virtual Machine SKU for the Scale Set"
  default     = "Standard_F2"
}

variable "agent_vnet_address_space" {
  type        = string
  description = "The IP range of the virtual network for the build agents"
  default     = "10.1.0.0/16"
}

variable "agent_subnet_address_space" {
  type        = string
  description = "The IP range of the default subnet for the build agents"
  default     = "10.1.1.0/24"
}

variable "agent_name" {
  type        = string
  description = "The name of the self-hosted agent"
  default     = "agent_user"
}

variable "azdo_pat" {
  type        = string
  description = "Personal access token generated for the agent administration"
  default     = ""
}

variable "agent_pool" {
  type        = string
  description = "The name of the agent pool"
  default     = "sp_azure_enablement_pool"
}

variable "azdo_org_service_url" {
  type        = string
  description = "The url of the organization on Azure DevOps"
  default     = "https://dev.azure.com/siemens-microsoft-iai"
}

variable "number_of_agents" {
  type        = number
  description = "The number of agents to create"
  default     = 4
}
