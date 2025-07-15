# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

output "key_vault_id" {
  description = "The name of the shared Key Vault"
  value       = azurerm_key_vault.kv.id
}

output "key_vault_name" {
  description = "The name of the shared Key Vault"
  value       = azurerm_key_vault.kv.name
}

output "kv_url" {
  description = "The URL for the logs Key Vault"
  value       = azurerm_key_vault.kv.vault_uri
}

output "log_analytics_workspace_name" {
  value = azurerm_log_analytics_workspace.main.name
}

output "log_analytics_workspace_id" {
  value = azurerm_log_analytics_workspace.main.id
}

output "log_analytics_workspace_sku" {
  value = azurerm_log_analytics_workspace.main.sku
}

output "app_insights_name" {
  value     = azurerm_application_insights.main.name
  sensitive = true
}

output "app_insights_instrumentation_key" {
  value     = azurerm_application_insights.main.instrumentation_key
  sensitive = true
}

output "app_insights_app_id" {
  value = azurerm_application_insights.main.app_id
}

output "app_insights_connection_string" {
  value     = azurerm_application_insights.main.connection_string
  sensitive = true
}

output "app_insights_id" {
  value = azurerm_application_insights.main.id
}

output "storage_account_kv_logs_name" {
  value       = azurerm_storage_account.main.name
  description = "The name of the storage account that contains the logs for the Key Vault"
}

output "monitor_diagnostic_settings_kv_logs_name" {
  value       = azurerm_monitor_diagnostic_setting.main.name
  description = "The name of the Monitor Diagnostic Setting for the Key Vault logs"
}
