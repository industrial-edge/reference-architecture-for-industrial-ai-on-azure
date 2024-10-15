# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

locals {
  ampls_dns_zones = {
    "privatelink.monitor.azure.com" : format("monitor-%s-%s", var.deployment_source, var.random_suffix),
    "privatelink.oms.opinsights.azure.com" : format("oms-%s-%s", var.deployment_source, var.random_suffix),
    "privatelink.ods.opinsights.azure.com" : format("ods-%s-%s", var.deployment_source, var.random_suffix),
    "privatelink.agentsvc.azure-automation.net" : format("agentsvc-%s-%s", var.deployment_source, var.random_suffix),
  }
}

##### Key vault #####
resource "azurerm_private_endpoint" "key_vault" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.kv_private_endpoint_name
  location            = var.location
  resource_group_name = var.rg_name
  subnet_id           = var.integration_subnet_id

  private_dns_zone_group {
    name                 = module.common.private_dns_zone_group_name
    private_dns_zone_ids = [var.kv_private_dns_zone_id]
  }

  private_service_connection {
    name                           = module.common.kv_private_service_connection_name
    private_connection_resource_id = azurerm_key_vault.kv.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }
}


##### Azure Monitor Private Link Scope #####
resource "azurerm_monitor_private_link_scope" "ampls" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.ampls_name
  resource_group_name = var.rg_name
}

resource "azurerm_monitor_private_link_scoped_service" "ampls_appinsights" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.ampls_service_name_appinsights
  resource_group_name = var.rg_name
  scope_name          = azurerm_monitor_private_link_scope.ampls[0].name
  linked_resource_id  = azurerm_application_insights.main.id
}

resource "azurerm_monitor_private_link_scoped_service" "ampls_loganalyticsworkspace" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.ampls_service_name_loganalyticsworkspace
  resource_group_name = var.rg_name
  scope_name          = azurerm_monitor_private_link_scope.ampls[0].name
  linked_resource_id  = azurerm_log_analytics_workspace.main.id
}

resource "azurerm_private_dns_zone" "ampls_dns_zones" {
  for_each            = var.vnet_enabled ? local.ampls_dns_zones : {}
  name                = each.key
  resource_group_name = var.rg_name
}

resource "azurerm_private_dns_zone_virtual_network_link" "ampls_dns_zones" {
  for_each              = var.vnet_enabled ? local.ampls_dns_zones : {}
  name                  = each.value
  resource_group_name   = var.rg_name
  private_dns_zone_name = each.key
  virtual_network_id    = var.vnet_id

  depends_on = [azurerm_private_dns_zone.ampls_dns_zones]
}

resource "azurerm_private_endpoint" "ampls" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.ampls_private_endpoint_name
  location            = var.location
  resource_group_name = var.rg_name
  subnet_id           = var.integration_subnet_id

  private_dns_zone_group {
    name                 = module.common.private_dns_zone_group_name
    private_dns_zone_ids = values(azurerm_private_dns_zone.ampls_dns_zones)[*].id
  }

  private_service_connection {
    name                           = module.common.ampls_private_service_connection_name
    private_connection_resource_id = azurerm_monitor_private_link_scope.ampls[0].id
    subresource_names              = ["azuremonitor"]
    is_manual_connection           = false
  }

  depends_on = [
    azurerm_monitor_private_link_scope.ampls,
    azurerm_monitor_private_link_scoped_service.ampls_appinsights,
    azurerm_monitor_private_link_scoped_service.ampls_loganalyticsworkspace
  ]
}
