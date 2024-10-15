# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

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

variable "deployment_source" {
  type        = string
  description = "The deployment source (e.g dev)"
}

variable "random_suffix" {
  type        = string
  description = "The suffix appended to the resource names"
}

variable "model_manager_pipeline_service_principal_id" {
  type        = string
  description = "The name ObjectId of the service principal used in the Create Model Manager Identity Pipeline"
}

variable "vnet_id" {
  type        = string
  description = "The id of the virtual network"
}

variable "integration_subnet_id" {
  type        = string
  description = "The id range of the integration subnet for private endpoints"
}

variable "vnet_enabled" {
  type        = bool
  description = "Specifies whether to deploy resources behind a VNET or not"
}

variable "iothub_private_dns_zone_id" {
  type        = string
  description = "The private dns zone Id for the iothub"
}

variable "eventhub_private_dns_zone_id" {
  type        = string
  description = "The private dns zone Id for the eventhub"
}

##########################################
# IoT Management variables #
##########################################
variable "iothub_sku_name" {
  type        = string
  description = "The name of the sku. Possible values are B1, B2, B3, F1, S1, S2, and S3."
}

variable "iothub_sku_capacity" {
  type        = number
  description = "The number of provisioned IoT Hub units."
}

variable "iothub_eventhub_shared_access_policy_name" {
  type        = string
  description = "The name of the shared access policy of the IoT Hub"
}
