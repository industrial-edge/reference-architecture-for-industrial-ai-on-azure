<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_common"></a> [common](#module\_common) | ../common | n/a |

## Resources

| Name | Type |
|------|------|
| [azurerm_application_insights.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/application_insights) | resource |
| [azurerm_key_vault.kv](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault) | resource |
| [azurerm_key_vault_secret.ai_appid_secret](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_key_vault_secret.ai_connstring_secret](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_key_vault_secret.kv_suffix_secret](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_log_analytics_solution.sqldvancedthreatprotection](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/log_analytics_solution) | resource |
| [azurerm_log_analytics_solution.sqlvulnerabilityassessment](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/log_analytics_solution) | resource |
| [azurerm_log_analytics_workspace.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/log_analytics_workspace) | resource |
| [azurerm_monitor_action_group.failure_anomaly](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/monitor_action_group) | resource |
| [azurerm_monitor_diagnostic_setting.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/monitor_diagnostic_setting) | resource |
| [azurerm_monitor_private_link_scope.ampls](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/monitor_private_link_scope) | resource |
| [azurerm_monitor_smart_detector_alert_rule.failure_anomaly](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/monitor_smart_detector_alert_rule) | resource |
| [azurerm_private_dns_zone.ampls_dns_zones](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone) | resource |
| [azurerm_private_dns_zone.key_vault](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone) | resource |
| [azurerm_private_dns_zone_virtual_network_link.ampls_dns_zones](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone_virtual_network_link) | resource |
| [azurerm_private_dns_zone_virtual_network_link.key_vault](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone_virtual_network_link) | resource |
| [azurerm_private_endpoint.ampls](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_private_endpoint.key_vault](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_storage_account.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account) | resource |
| [azurerm_storage_management_policy.main](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_management_policy) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/client_config) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_app_insights_local_auth_disabled"></a> [app\_insights\_local\_auth\_disabled](#input\_app\_insights\_local\_auth\_disabled) | Disable Non-Azure AD based Auth. Defaults to false. | `string` | n/a | yes |
| <a name="input_application_insights_app_type"></a> [application\_insights\_app\_type](#input\_application\_insights\_app\_type) | Specifies the type of Application Insights to create. Please note these values are case sensitive; unmatched values are treated as ASP.NET by Azure. Changing this forces a new resource to be created | `string` | n/a | yes |
| <a name="input_deployment_source"></a> [deployment\_source](#input\_deployment\_source) | The deployment source (e.g dev) | `string` | n/a | yes |
| <a name="input_failure_anomaly_frequency"></a> [failure\_anomaly\_frequency](#input\_failure\_anomaly\_frequency) | Specifies the frequency of this Smart Detector Alert Rule in ISO8601 format. | `string` | n/a | yes |
| <a name="input_failure_anomaly_severity"></a> [failure\_anomaly\_severity](#input\_failure\_anomaly\_severity) | Specifies the severity of this Smart Detector Alert Rule | `string` | n/a | yes |
| <a name="input_integration_subnet_id"></a> [integration\_subnet\_id](#input\_integration\_subnet\_id) | The id range of the integration subnet for private endpoints | `string` | n/a | yes |
| <a name="input_kv_sku_name"></a> [kv\_sku\_name](#input\_kv\_sku\_name) | Specifies the price of Key Vault Azure resource. 'standard' and 'premium' is available. | `string` | n/a | yes |
| <a name="input_kv_soft_delete_retention_days"></a> [kv\_soft\_delete\_retention\_days](#input\_kv\_soft\_delete\_retention\_days) | The number of days that items should be retained for, once soft-deleted. This value can be between 7 and 90 (the default) days. | `number` | n/a | yes |
| <a name="input_location"></a> [location](#input\_location) | (Required) Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created. | `string` | n/a | yes |
| <a name="input_log_analytics_workspace_retention"></a> [log\_analytics\_workspace\_retention](#input\_log\_analytics\_workspace\_retention) | The workspace data retention in days. Possible values are either 7 (Free Tier only) or range between 30 and 730. The Free SKU has a default daily\_quota\_gb value of 0.5 (GB) | `number` | n/a | yes |
| <a name="input_log_analytics_workspace_sku"></a> [log\_analytics\_workspace\_sku](#input\_log\_analytics\_workspace\_sku) | Specifies the SKU of the Log Analytics Workspace. | `string` | n/a | yes |
| <a name="input_random_suffix"></a> [random\_suffix](#input\_random\_suffix) | The suffix appended to the resource names | `string` | n/a | yes |
| <a name="input_rg_name"></a> [rg\_name](#input\_rg\_name) | The name of the resource group | `string` | n/a | yes |
| <a name="input_storage_account_account_replication_type"></a> [storage\_account\_account\_replication\_type](#input\_storage\_account\_account\_replication\_type) | Defines the type of replication to use for the storage account | `string` | `"LRS"` | no |
| <a name="input_storage_account_account_tier"></a> [storage\_account\_account\_tier](#input\_storage\_account\_account\_tier) | Defines the tier to use for the storage account | `string` | `"Standard"` | no |
| <a name="input_storage_mngmnt_policy_kv_logs_delete_after"></a> [storage\_mngmnt\_policy\_kv\_logs\_delete\_after](#input\_storage\_mngmnt\_policy\_kv\_logs\_delete\_after) | The age in days after creation to delete the blob. | `string` | n/a | yes |
| <a name="input_storage_mngmnt_policy_kv_logs_rule_name"></a> [storage\_mngmnt\_policy\_kv\_logs\_rule\_name](#input\_storage\_mngmnt\_policy\_kv\_logs\_rule\_name) | The name of the rule for the storage account management policy used to set the retention policy for the Key Vault logs. | `string` | n/a | yes |
| <a name="input_vnet_enabled"></a> [vnet\_enabled](#input\_vnet\_enabled) | Specifies whether to deploy resources behind a VNET or not | `bool` | n/a | yes |
| <a name="input_vnet_id"></a> [vnet\_id](#input\_vnet\_id) | The id of the virtual network | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_app_insights_app_id"></a> [app\_insights\_app\_id](#output\_app\_insights\_app\_id) | n/a |
| <a name="output_app_insights_connection_string"></a> [app\_insights\_connection\_string](#output\_app\_insights\_connection\_string) | n/a |
| <a name="output_app_insights_id"></a> [app\_insights\_id](#output\_app\_insights\_id) | n/a |
| <a name="output_app_insights_instrumentation_key"></a> [app\_insights\_instrumentation\_key](#output\_app\_insights\_instrumentation\_key) | n/a |
| <a name="output_app_insights_name"></a> [app\_insights\_name](#output\_app\_insights\_name) | n/a |
| <a name="output_key_vault_id"></a> [key\_vault\_id](#output\_key\_vault\_id) | The name of the shared Key Vault |
| <a name="output_key_vault_name"></a> [key\_vault\_name](#output\_key\_vault\_name) | The name of the shared Key Vault |
| <a name="output_kv_url"></a> [kv\_url](#output\_kv\_url) | The URL for the logs Key Vault |
| <a name="output_log_analytics_workspace_id"></a> [log\_analytics\_workspace\_id](#output\_log\_analytics\_workspace\_id) | n/a |
| <a name="output_log_analytics_workspace_name"></a> [log\_analytics\_workspace\_name](#output\_log\_analytics\_workspace\_name) | n/a |
| <a name="output_log_analytics_workspace_sku"></a> [log\_analytics\_workspace\_sku](#output\_log\_analytics\_workspace\_sku) | n/a |
| <a name="output_monitor_diagnostic_settings_kv_logs_name"></a> [monitor\_diagnostic\_settings\_kv\_logs\_name](#output\_monitor\_diagnostic\_settings\_kv\_logs\_name) | The name of the Monitor Diagnostic Setting for the Key Vault logs |
| <a name="output_storage_account_kv_logs_name"></a> [storage\_account\_kv\_logs\_name](#output\_storage\_account\_kv\_logs\_name) | The name of the storage account that contains the logs for the Key Vault |
<!-- END_TF_DOCS -->
