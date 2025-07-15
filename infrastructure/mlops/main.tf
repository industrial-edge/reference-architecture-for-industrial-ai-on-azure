module "common" {
  source            = "../common"
  deployment_source = var.deployment_source
  random_suffix     = var.random_suffix
}

resource "azurerm_container_registry" "ml" {
  name                          = module.common.ml_container_registry_name
  location                      = var.location
  resource_group_name           = var.rg_name
  sku                           = var.container_registry_sku
  admin_enabled                 = var.container_registry_admin_enabled
  public_network_access_enabled = var.vnet_enabled ? false : true
}

resource "azurerm_key_vault_secret" "ml" {
  name         = module.common.kv_cr_name_secret_name
  value        = azurerm_container_registry.ml.name
  key_vault_id = var.kv_id
}

resource "azurerm_storage_account" "ml" {
  name                          = module.common.ml_storage_account_name
  resource_group_name           = var.rg_name
  location                      = var.location
  account_kind                  = var.sa_account_kind
  account_tier                  = var.sa_account_tier
  account_replication_type      = var.sa_account_replication_type
  access_tier                   = var.sa_access_tier
  public_network_access_enabled = var.vnet_enabled ? false : true

  min_tls_version = "TLS1_2"
}

resource "azurerm_machine_learning_workspace" "ml" {
  name                          = module.common.ml_workspace_name
  location                      = var.location
  resource_group_name           = var.rg_name
  key_vault_id                  = var.kv_id
  storage_account_id            = azurerm_storage_account.ml.id
  container_registry_id         = azurerm_container_registry.ml.id
  application_insights_id       = var.appinsights_id
  public_network_access_enabled = true
  image_build_compute_name = module.common.ml_compute_cluster_name

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_user_assigned_identity" "ml" {
  name = module.common.ml_user_assigned_identity_name
  resource_group_name = var.rg_name
  location = var.location
}

resource "azurerm_role_assignment" "storage_contributor" {
  scope                = azurerm_storage_account.ml.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.ml.principal_id
}

resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.ml.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.ml.principal_id
}

resource "azurerm_role_assignment" "kv_reader" {
  scope                = var.kv_id
  role_definition_name = "Key Vault Reader"
  principal_id         = azurerm_user_assigned_identity.ml.principal_id
}

resource "azurerm_role_assignment" "kv_contributor" {
  scope                = var.kv_id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.ml.principal_id
}

resource "azurerm_role_assignment" "appinsights_contributor" {
  scope                = var.appinsights_id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.ml.principal_id
}

resource "azurerm_role_assignment" "ml_data_scientist" {
  scope                = azurerm_machine_learning_workspace.ml.id
  role_definition_name = "AzureML Data Scientist"
  principal_id         = azurerm_user_assigned_identity.ml.principal_id
}

resource "azurerm_key_vault_access_policy" "current" {
  key_vault_id = var.kv_id
  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = azurerm_user_assigned_identity.ml.principal_id

  key_permissions = [
    "Get",
    "List",
  ]

  secret_permissions = [
    "Get",
    "List"
  ]

  certificate_permissions = [
    "Get",
    "List",
  ]
}

resource "azurerm_machine_learning_compute_cluster" "ml" {
  name                          = module.common.ml_compute_cluster_name
  location                      = var.location
  vm_priority                   = var.compute_cluster_vm_priority
  vm_size                       = var.compute_cluster_vm_size
  machine_learning_workspace_id = azurerm_machine_learning_workspace.ml.id
  subnet_resource_id            = var.vnet_enabled ? azurerm_subnet.training_subnet[0].id : null

  scale_settings {
    min_node_count                       = var.cc_scale_settings_min_node_count
    max_node_count                       = var.cc_scale_settings_max_node_count
    scale_down_nodes_after_idle_duration = var.cc_scale_down_after_idle_duration
  }

  identity {
    type = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.ml.id]
  }

}
