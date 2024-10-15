# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

output "resource_group_name" {
  description = "The name of the resouce group containing all resources"
  value       = azurerm_resource_group.rg.name
}

output "resource_suffix" {
  value = random_string.suffix.result
}

output "key_vault_name" {
  description = "The name of the shared Key Vault"
  value       = module.shared.key_vault_name
}

output "iot_hub_name" {
  description = "The name of the IoT hub"
  value       = module.iotmngmt.iot_hub_name
}

output "log_analytics_workspace_name" {
  value = module.shared.log_analytics_workspace_name
}

output "log_analytics_workspace_id" {
  value = module.shared.log_analytics_workspace_id
}

output "log_analytics_workspace_sku" {
  value = module.shared.log_analytics_workspace_sku
}

output "app_insights_name" {
  value     = module.shared.app_insights_name
  sensitive = true
}

output "app_insights_instrumentation_key" {
  value     = module.shared.app_insights_instrumentation_key
  sensitive = true
}

output "app_insights_app_id" {
  value = module.shared.app_insights_app_id
}

output "app_insights_connection_string" {
  value     = module.shared.app_insights_connection_string
  sensitive = true
}

output "storage_account_kv_logs_name" {
  value = module.shared.storage_account_kv_logs_name
}

output "key_vault_id" {
  value = module.shared.key_vault_id
}

output "main_service_principal_id" {
  value = data.azurerm_client_config.current.object_id
}

output "vpn_client_cert" {
  value     = module.vnet.client_cert
  sensitive = true
}

output "vpn_client_key" {
  value     = module.vnet.client_key
  sensitive = true
}
