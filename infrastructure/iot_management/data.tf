# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

data "azurerm_iothub_shared_access_policy" "iothub" {
  name                = var.iothub_eventhub_shared_access_policy_name
  resource_group_name = var.rg_name
  iothub_name         = azurerm_iothub.iothub.name
}
