resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

module "common" {
  source            = "../../common"
  deployment_source = var.deployment_source
  random_suffix     = random_string.suffix.result
}

resource "azurerm_resource_group" "rg" {
  name     = module.common.rg_name
  location = var.location
  tags     = { "Deployment:Source" : var.deployment_source }
}

### Virtual Network ###

module "vnet" {
  source                           = "../../network"
  location                         = var.location
  rg_name                          = azurerm_resource_group.rg.name
  deployment_source                = var.deployment_source
  random_suffix                    = random_string.suffix.result
  vnet_enabled                     = var.vnet_enabled
  vnet_address_space               = var.vnet_address_space
  gateway_subnet_address_space      = var.gateway_subnet_address_space
  integration_subnet_address_space = var.integration_subnet_address_space
  dns_resolver_subnet_address_space = var.dns_resolver_subnet_address_space
  vpn_client_address_space          = var.vpn_client_address_space
  vnet_gateway_sku                  = var.vnet_gateway_sku
  peer_with_pipeline               = var.peer_with_pipeline

  tfstate_resource_group_name  = var.resource_group_name
  tfstate_storage_account_name = var.storage_account_name
  tfstate_container_name       = var.container_name
}

### Shared Resources ###
module "shared" {
  source                                     = "../../shared"
  location                                   = var.location
  rg_name                                    = azurerm_resource_group.rg.name
  deployment_source                          = var.deployment_source
  random_suffix                              = random_string.suffix.result
  failure_anomaly_frequency                  = var.failure_anomaly_frequency
  failure_anomaly_severity                   = var.failure_anomaly_severity
  vnet_enabled                               = var.vnet_enabled
  vnet_id                                    = module.vnet.vnet_id
  integration_subnet_id                      = module.vnet.integration_subnet_id
  kv_private_dns_zone_id                     = module.vnet.kv_private_dns_zone_id
  storage_mngmnt_policy_kv_logs_rule_name    = var.storage_mngmnt_policy_kv_logs_rule_name
  storage_mngmnt_policy_kv_logs_delete_after = var.storage_mngmnt_policy_kv_logs_delete_after
  kv_sku_name                                = var.kv_sku_name
  kv_soft_delete_retention_days              = var.kv_soft_delete_retention_days
  log_analytics_workspace_sku                = var.log_analytics_workspace_sku
  log_analytics_workspace_retention          = var.log_analytics_workspace_retention
  application_insights_app_type              = var.application_insights_app_type
  app_insights_local_auth_disabled           = var.app_insights_local_auth_disabled
  model_manager_pipeline_service_principal_id = var.model_manager_pipeline_service_principal_id
  model_monitor_identity_pipeline_principal_id = var.model_monitor_identity_pipeline_principal_id
}

### MLOps Resources ###
module "mlops" {
  source                            = "../../mlops"
  vnet_enabled                      = var.vnet_enabled
  location                          = var.location
  rg_name                           = azurerm_resource_group.rg.name
  vnet_id                           = module.vnet.vnet_id
  vnet_name                         = module.vnet.vnet_name
  integration_subnet_id             = module.vnet.integration_subnet_id
  training_subnet_address_range     = var.training_subnet_address_range
  kv_id                             = module.shared.key_vault_id
  appinsights_id                    = module.shared.app_insights_id
  private_dns_zone_id_stg_blob      = module.vnet.private_dns_zone_id_stgacc_blob
  cr_private_dns_zone_id            = module.vnet.cr_private_dns_zone_id
  ml_private_dns_zone_id            = module.vnet.ml_private_dns_zone_id
  deployment_source                 = var.deployment_source
  random_suffix                     = random_string.suffix.result
  container_registry_sku            = var.ml_container_registry_sku
  container_registry_admin_enabled  = var.ml_container_registry_admin_enabled
  sa_account_kind                   = var.ml_sa_account_kind
  sa_access_tier                    = var.ml_sa_access_tier
  sa_account_tier                   = var.ml_sa_account_tier
  sa_account_replication_type       = var.ml_sa_account_replication_type
  compute_cluster_vm_priority       = var.ml_compute_cluster_vm_priority
  compute_cluster_vm_size           = var.ml_compute_cluster_vm_size
  cc_scale_down_after_idle_duration = var.ml_cc_scale_down_after_idle_duration
  cc_scale_settings_max_node_count  = var.ml_cc_scale_settings_max_node_count
  cc_scale_settings_min_node_count  = var.ml_cc_scale_settings_min_node_count
  depends_on = [ module.shared ]
}

module "iotmngmt" {
  source                                    = "../../iot_management"
  location                                  = var.location
  rg_name                                   = azurerm_resource_group.rg.name
  kv_id                                     = module.shared.key_vault_id
  deployment_source                         = var.deployment_source
  random_suffix                             = random_string.suffix.result
  iothub_sku_name                           = var.iothub_sku_name
  iothub_sku_capacity                       = var.iothub_sku_capacity
  iothub_eventhub_shared_access_policy_name = var.iothub_eventhub_shared_access_policy_name
  model_manager_pipeline_service_principal_id = var.model_manager_pipeline_service_principal_id
  depends_on = [ module.shared ]
  vnet_enabled                                = var.vnet_enabled
  vnet_id                                     = module.vnet.vnet_id
  integration_subnet_id                       = module.vnet.integration_subnet_id
  iothub_private_dns_zone_id                  = module.vnet.iothub_private_dns_zone_id
  eventhub_private_dns_zone_id                = module.vnet.eventhub_private_dns_zone_id
}
