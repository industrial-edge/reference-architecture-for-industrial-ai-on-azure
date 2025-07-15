# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

output "rg_name" {
  value = var.rg_name
}

output "iot_hub_name" {
  value = azurerm_iothub.iothub.name
}