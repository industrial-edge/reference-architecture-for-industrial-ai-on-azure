# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

output "rg_name" {
  value = var.rg_name
}

output "container_registry_name" {
  value = azurerm_container_registry.ml.name
}

output "key_vault_secret_cr_name" {
  value     = azurerm_key_vault_secret.ml.value
  sensitive = true
}

output "storage_name" {
  description = "The Azure Storage Account name."
  value       = azurerm_storage_account.ml.name
}

output "storage_account_id" {
  description = "The Azure Storage Account ID."
  value       = azurerm_storage_account.ml.id
}

output "storage_blob_primary_url" {
  description = "The endpoint URL for blob storage in the primary location."
  value       = azurerm_storage_account.ml.primary_blob_endpoint
}

output "storage_primary_access_key" {
  description = "The hostname with port if applicable for blob storage in the secondary location."
  value       = azurerm_storage_account.ml.primary_access_key
  sensitive   = true
}

output "storage_primary_connection_string" {
  description = "The connection string associated with the primary location."
  value       = azurerm_storage_account.ml.primary_connection_string
  sensitive   = true
}

output "compute_cluster_id" {
  value = azurerm_machine_learning_compute_cluster.ml.id
}

output "compute_cluster_name" {
  value = azurerm_machine_learning_compute_cluster.ml.name
}

output "machine_learning_workspace_name" {
  description = "The Azure Machine Learning Workspace name."
  value       = azurerm_machine_learning_workspace.ml.name
}
