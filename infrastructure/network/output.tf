output "vnet_id" {
  value     = var.vnet_enabled ? azurerm_virtual_network.vnet[0].id : null
  sensitive = true
}

output "vnet_name" {
  value = var.vnet_enabled ? azurerm_virtual_network.vnet[0].name : ""
}

output "integration_subnet_id" {
  value     = var.vnet_enabled ? azurerm_subnet.integration_subnet[0].id : null
  sensitive = true
}

output "integration_subnet_name" {
  value = var.vnet_enabled ? azurerm_subnet.integration_subnet[0].name : ""
}

output "private_dns_zone_id_stgacc_blob" {
  value = var.vnet_enabled ? azurerm_private_dns_zone.dns_storageacc_blob[0].id : ""
}

output "kv_private_dns_zone_id" {
  value = var.vnet_enabled ? azurerm_private_dns_zone.key_vault[0].id : ""
}

output "cr_private_dns_zone_id" {
  value = var.vnet_enabled ? azurerm_private_dns_zone.container_registry[0].id : ""
}

output "ml_private_dns_zone_id" {
  value = var.vnet_enabled ? azurerm_private_dns_zone.ml[0].id : ""
}

output "iothub_private_dns_zone_id" {
  value = var.vnet_enabled ? azurerm_private_dns_zone.iot_hub[0].id : ""
}

output "eventhub_private_dns_zone_id" {
  value = var.vnet_enabled ? azurerm_private_dns_zone.event_hub[0].id : ""
}

output "client_cert" {
  value     = var.vnet_enabled ? tls_locally_signed_cert.client_cert[0].cert_pem : ""
  sensitive = true
}

output "client_key" {
  value     = var.vnet_enabled ? tls_private_key.client_cert[0].private_key_pem : ""
  sensitive = true
}
