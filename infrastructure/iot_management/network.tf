# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

##### IoT Hub #####
resource "azurerm_private_endpoint" "iot_hub" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.iot_hub_private_endpoint_name
  location            = var.location
  resource_group_name = var.rg_name
  subnet_id           = var.integration_subnet_id

  private_service_connection {
    name                           = module.common.iot_hub_private_service_connection_name
    private_connection_resource_id = azurerm_iothub.iothub.id
    subresource_names              = ["iotHub"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = module.common.private_dns_zone_group_name
    private_dns_zone_ids = [var.iothub_private_dns_zone_id, var.eventhub_private_dns_zone_id]
  }

}
