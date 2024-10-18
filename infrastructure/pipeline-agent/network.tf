# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

resource "azurerm_virtual_network" "agent_vnet" {
  name                = module.common.agent_vnet_name
  address_space       = [var.agent_vnet_address_space]
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "default" {
  name                 = module.common.agent_default_subnet_name
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.agent_vnet.name
  address_prefixes     = [var.agent_subnet_address_space]
}
