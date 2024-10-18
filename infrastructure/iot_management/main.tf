# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

module "common" {
  source            = "../common"
  deployment_source = var.deployment_source
  random_suffix     = var.random_suffix
}

resource "azurerm_iothub" "iothub" {
  name                = module.common.iothub_name
  resource_group_name = var.rg_name
  location            = var.location

  sku {
    name     = var.iothub_sku_name
    capacity = var.iothub_sku_capacity
  }
  public_network_access_enabled = !var.vnet_enabled
}

resource "azurerm_role_assignment" "ModelManagerPipeline" {
  scope                = azurerm_iothub.iothub.id
  role_definition_name = "Contributor"
  principal_id         = var.model_manager_pipeline_service_principal_id
}

resource "azurerm_key_vault_secret" "iothub_kv_connstring" {
  name         = module.common.kv_iothub_connection_string_secret_name
  value        = data.azurerm_iothub_shared_access_policy.iothub.primary_connection_string
  key_vault_id = var.kv_id
}

resource "azurerm_key_vault_secret" "iothub_kv_iothubname" {
  name         = module.common.kv_iothub_name_secret_name
  value        = azurerm_iothub.iothub.name
  key_vault_id = var.kv_id
}

resource "azurerm_key_vault_secret" "iothub_kv_eventhubendpoint" {
  name         = module.common.kv_iothub_eventhubendpoint_secret_name
  value        = azurerm_iothub.iothub.event_hub_events_endpoint
  key_vault_id = var.kv_id
}

resource "azurerm_key_vault_secret" "iothub_kv_eventhub_compatible_endpoint" {
  name         = module.common.kv_eventhub_compatible_endpoint_secret_name
  value        = format("Endpoint=%s;SharedAccessKeyName=%s;SharedAccessKey=%s;EntityPath=%s", azurerm_iothub.iothub.event_hub_events_endpoint, var.iothub_eventhub_shared_access_policy_name, data.azurerm_iothub_shared_access_policy.iothub.primary_key, azurerm_iothub.iothub.name)
  key_vault_id = var.kv_id
}
