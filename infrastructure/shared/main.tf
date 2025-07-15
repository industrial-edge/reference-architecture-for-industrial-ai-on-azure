# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

module "common" {
  source            = "../common"
  deployment_source = var.deployment_source
  random_suffix     = var.random_suffix
}

# Create the Azure Key Vault
resource "azurerm_key_vault" "kv" {
  name                       = module.common.kv_name
  resource_group_name        = var.rg_name
  sku_name                   = var.kv_sku_name
  location                   = var.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  tags                       = { "Deployment:Source" : var.deployment_source }
  soft_delete_retention_days = var.kv_soft_delete_retention_days
}

resource "azurerm_key_vault_access_policy" "current" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = data.azurerm_client_config.current.object_id

  key_permissions = [
    "Create",
    "Get",
    "List",
    "Recover",
    "Purge"
  ]

    secret_permissions = [
      "Set",
      "Get",
      "Delete",
      "Purge",
      "Recover",
      "List"
    ]

    certificate_permissions = [
      "Create",
      "List",
      "Get",
      "Purge",
      "Recover"
    ]
    storage_permissions = ["Get"]
}

resource "azurerm_key_vault_access_policy" "ModelManagerIdentityPipeline" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = var.model_manager_pipeline_service_principal_id

  secret_permissions = [
    "Set",
    "Get",
    "List"
  ]

  certificate_permissions = [
    "List",
    "Get",
    "Create"
  ]
}

resource "azurerm_key_vault_access_policy" "ModelMonitorIdentityPipeline" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = var.model_monitor_identity_pipeline_principal_id

  secret_permissions = [
    "Set",
    "Get",
    "List"
  ]

  certificate_permissions = [
    "List",
    "Get",
    "Create"
  ]
}

# Create the workspace-based Application Insights shared by all PaaS resources for gathering their specific telemetry
resource "azurerm_log_analytics_workspace" "main" {
  name                = module.common.log_analytics_workspace_name
  location            = var.location
  resource_group_name = var.rg_name
  retention_in_days   = var.log_analytics_workspace_retention
  sku                 = var.log_analytics_workspace_sku
}

resource "azurerm_log_analytics_solution" "sqlvulnerabilityassessment" {
  solution_name         = "SQLVulnerabilityAssessment"
  location              = var.location
  resource_group_name   = var.rg_name
  workspace_resource_id = azurerm_log_analytics_workspace.main.id
  workspace_name        = azurerm_log_analytics_workspace.main.name

  plan {
    publisher = "Microsoft"
    product   = "OMSGallery/SQLVulnerabilityAssessment"
  }
}


resource "azurerm_log_analytics_solution" "sqldvancedthreatprotection" {
  solution_name         = "SQLAdvancedThreatProtection"
  location              = var.location
  resource_group_name   = var.rg_name
  workspace_resource_id = azurerm_log_analytics_workspace.main.id
  workspace_name        = azurerm_log_analytics_workspace.main.name

  plan {
    publisher = "Microsoft"
    product   = "OMSGallery/SQLAdvancedThreatProtection"
  }
}

resource "azurerm_application_insights" "main" {
  name                          = module.common.application_insights_name
  location                      = var.location
  resource_group_name           = var.rg_name
  workspace_id                  = azurerm_log_analytics_workspace.main.id
  application_type              = var.application_insights_app_type
  local_authentication_disabled = var.app_insights_local_auth_disabled
}

resource "azurerm_role_assignment" "model_monitor_identity_pipeline" {

  scope                = azurerm_application_insights.main.id
  role_definition_name = "Owner"
  principal_id         = var.model_monitor_identity_pipeline_principal_id
}

resource "azurerm_monitor_action_group" "failure_anomaly" {
  name                = module.common.monitor_action_group_name
  resource_group_name = var.rg_name
  short_name          = "team"
}

resource "azurerm_monitor_smart_detector_alert_rule" "failure_anomaly" {
  name                = module.common.failure_anomaly_name
  resource_group_name = var.rg_name
  severity            = var.failure_anomaly_severity
  scope_resource_ids  = [azurerm_application_insights.main.id]
  frequency           = var.failure_anomaly_frequency
  detector_type       = "FailureAnomaliesDetector"

  action_group {
    ids = [azurerm_monitor_action_group.failure_anomaly.id]
  }
}

resource "azurerm_key_vault_secret" "ai_connstring_secret" {
  name         = module.common.kv_ai_connection_string_secret_name
  value        = azurerm_application_insights.main.connection_string
  key_vault_id = azurerm_key_vault.kv.id
  depends_on = [ azurerm_key_vault_access_policy.current]
}

resource "azurerm_key_vault_secret" "ai_appid_secret" {
  name         = module.common.kv_ai_application_id_secret_name
  value        = azurerm_application_insights.main.id
  key_vault_id = azurerm_key_vault.kv.id
  depends_on = [ azurerm_key_vault_access_policy.current]
}

resource "azurerm_key_vault_secret" "kv_suffix_secret" {
  name         = module.common.kv_suffix_secret_name
  value        = var.random_suffix
  key_vault_id = azurerm_key_vault.kv.id
  depends_on = [ azurerm_key_vault_access_policy.current]
}


resource "azurerm_storage_account" "main" {
  name                     = module.common.kv_logs_storage_account_name
  resource_group_name      = var.rg_name
  location                 = var.location
  account_tier             = var.storage_account_account_tier
  account_replication_type = var.storage_account_account_replication_type

  min_tls_version = "TLS1_2"
}


resource "azurerm_monitor_diagnostic_setting" "main" {
  name               = module.common.kv_monitor_diagnostic_setting_name
  target_resource_id = azurerm_key_vault.kv.id
  storage_account_id = azurerm_storage_account.main.id

  enabled_log {
    category = "AuditEvent"
  }

  metric {
    category = "AllMetrics"
  }
}

resource "azurerm_storage_management_policy" "main" {
  storage_account_id = azurerm_storage_account.main.id

  rule {
    name    = var.storage_mngmnt_policy_kv_logs_rule_name
    enabled = true
    filters {
      prefix_match = ["insights-logs-auditevent"]
      blob_types   = ["blockBlob", "appendBlob"]
    }
    actions {
      base_blob {
        delete_after_days_since_creation_greater_than = var.storage_mngmnt_policy_kv_logs_delete_after
      }
    }
  }

}
