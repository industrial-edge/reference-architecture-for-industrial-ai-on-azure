# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

output "rg_name" {
  value = azurerm_resource_group.rg.name
}

output "vnet_id" {
  value = azurerm_virtual_network.agent_vnet.id
}

output "vnet_name" {
  value = azurerm_virtual_network.agent_vnet.name
}

output "agent_subnet_id" {
  value = azurerm_subnet.default.id
}

output "agent_subnet_name" {
  value = azurerm_subnet.default.name
}
