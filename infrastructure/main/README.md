<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.13 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | >= 3.35.0, < 4.0.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | 3.70.0 |
| <a name="provider_random"></a> [random](#provider\_random) | 3.5.1 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_common"></a> [common](#module\_common) | ../common | n/a |
| <a name="module_iotmngmt"></a> [iotmngmt](#module\_iotmngmt) | ../iot_management | n/a |
| <a name="module_ml"></a> [ml](#module\_ml) | ../mlops | n/a |
| <a name="module_shared"></a> [shared](#module\_shared) | ../shared | n/a |
| <a name="module_vnet"></a> [vnet](#module\_vnet) | ../network | n/a |

## Resources

| Name | Type |
|------|------|
| [azurerm_resource_group.rg](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [random_string.suffix](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/client_config) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_app_insights_local_auth_disabled"></a> [app\_insights\_local\_auth\_disabled](#input\_app\_insights\_local\_auth\_disabled) | Disable Non-Azure AD based Auth. Defaults to false. | `string` | `"true"` | no |
| <a name="input_application_insights_app_type"></a> [application\_insights\_app\_type](#input\_application\_insights\_app\_type) | (Required) Specifies the type of Application Insights to create. Please note these values are case sensitive; unmatched values are treated as ASP.NET by Azure. Changing this forces a new resource to be created | `string` | `"web"` | no |
| <a name="input_deployment_source"></a> [deployment\_source](#input\_deployment\_source) | The deployment source (e.g dev) | `string` | `"dev"` | no |
| <a name="input_failure_anomaly_frequency"></a> [failure\_anomaly\_frequency](#input\_failure\_anomaly\_frequency) | (Required) Specifies the frequency of this Smart Detector Alert Rule in ISO8601 format. | `string` | `"PT1M"` | no |
| <a name="input_failure_anomaly_severity"></a> [failure\_anomaly\_severity](#input\_failure\_anomaly\_severity) | (Required) Specifies the severity of this Smart Detector Alert Rule | `string` | `"Sev3"` | no |
| <a name="input_integration_subnet_address_space"></a> [integration\_subnet\_address\_space](#input\_integration\_subnet\_address\_space) | The IP range of the integration subnet | `string` | `"10.0.2.0/24"` | no |
| <a name="input_iothub_eventhub_shared_access_policy_name"></a> [iothub\_eventhub\_shared\_access\_policy\_name](#input\_iothub\_eventhub\_shared\_access\_policy\_name) | The name of the shared access policy of the IoT Hub | `string` | `"iothubowner"` | no |
| <a name="input_iothub_sku_capacity"></a> [iothub\_sku\_capacity](#input\_iothub\_sku\_capacity) | (Required) The number of provisioned IoT Hub units. | `number` | `1` | no |
| <a name="input_iothub_sku_name"></a> [iothub\_sku\_name](#input\_iothub\_sku\_name) | (Required) The name of the sku. Possible values are B1, B2, B3, F1, S1, S2, and S3. | `string` | `"S1"` | no |
| <a name="input_kv_sku_name"></a> [kv\_sku\_name](#input\_kv\_sku\_name) | Specifies the price of Key Vault Azure resource. 'standard' and 'premium' is available. | `string` | `"standard"` | no |
| <a name="input_kv_soft_delete_retention_days"></a> [kv\_soft\_delete\_retention\_days](#input\_kv\_soft\_delete\_retention\_days) | (Optional) The number of days that items should be retained for, once soft-deleted. This value can be between 7 and 90 (the default) days. | `number` | `7` | no |
| <a name="input_location"></a> [location](#input\_location) | (Required) Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created. | `string` | `"westeurope"` | no |
| <a name="input_log_analytics_workspace_retention"></a> [log\_analytics\_workspace\_retention](#input\_log\_analytics\_workspace\_retention) | (Optional) The workspace data retention in days. Possible values are either 7 (Free Tier only) or range between 30 and 730. The Free SKU has a default daily\_quota\_gb value of 0.5 (GB) | `number` | `30` | no |
| <a name="input_log_analytics_workspace_sku"></a> [log\_analytics\_workspace\_sku](#input\_log\_analytics\_workspace\_sku) | (Optional) Specifies the SKU of the Log Analytics Workspace.  Defaults to PerGB2018 | `string` | `"PerGB2018"` | no |
| <a name="input_ml_cc_scale_down_after_idle_duration"></a> [ml\_cc\_scale\_down\_after\_idle\_duration](#input\_ml\_cc\_scale\_down\_after\_idle\_duration) | (Required) Node Idle Time Before Scale Down: defines the time until the compute is shutdown when it has gone into Idle state. Is defined according to W3C XML schema standard for duration. Changing this forces a new Machine Learning Compute Cluster to be created. | `string` | `"PT20S"` | no |
| <a name="input_ml_cc_scale_settings_max_node_count"></a> [ml\_cc\_scale\_settings\_max\_node\_count](#input\_ml\_cc\_scale\_settings\_max\_node\_count) | (Required) Maximum node count. Changing this forces a new Machine Learning Compute Cluster to be created. | `number` | `2` | no |
| <a name="input_ml_cc_scale_settings_min_node_count"></a> [ml\_cc\_scale\_settings\_min\_node\_count](#input\_ml\_cc\_scale\_settings\_min\_node\_count) | (Required) Minimum node count. Changing this forces a new Machine Learning Compute Cluster to be created. | `number` | `0` | no |
| <a name="input_ml_compute_cluster_identity_type"></a> [ml\_compute\_cluster\_identity\_type](#input\_ml\_compute\_cluster\_identity\_type) | (Optional) Compute cluster identity type. Changing this forces a new Machine Learning Compute Cluster to be created. | `string` | `"SystemAssigned"` | no |
| <a name="input_ml_compute_cluster_vm_priority"></a> [ml\_compute\_cluster\_vm\_priority](#input\_ml\_compute\_cluster\_vm\_priority) | (Required) The priority of the Virtual Machine. Changing this forces a new Machine Learning Compute Cluster to be created. | `string` | `"LowPriority"` | no |
| <a name="input_ml_compute_cluster_vm_size"></a> [ml\_compute\_cluster\_vm\_size](#input\_ml\_compute\_cluster\_vm\_size) | (Required) The size of the Virtual Machine. Changing this forces a new Machine Learning Compute Cluster to be created. | `string` | `"STANDARD_DS2_V2"` | no |
| <a name="input_ml_container_registry_admin_enabled"></a> [ml\_container\_registry\_admin\_enabled](#input\_ml\_container\_registry\_admin\_enabled) | (Optional) Specifies whether the admin user is enabled. Defaults to false | `bool` | `true` | no |
| <a name="input_ml_container_registry_sku"></a> [ml\_container\_registry\_sku](#input\_ml\_container\_registry\_sku) | (Required) The SKU name of the container registry. Possible values are Basic, Standard and Premium. | `string` | `"Premium"` | no |
| <a name="input_ml_sa_access_tier"></a> [ml\_sa\_access\_tier](#input\_ml\_sa\_access\_tier) | (Optional) Defines the access tier for BlobStorage, FileStorage and StorageV2 accounts. | `string` | `"Hot"` | no |
| <a name="input_ml_sa_account_kind"></a> [ml\_sa\_account\_kind](#input\_ml\_sa\_account\_kind) | (Optional) Defines the Kind of account. | `string` | `"StorageV2"` | no |
| <a name="input_ml_sa_account_replication_type"></a> [ml\_sa\_account\_replication\_type](#input\_ml\_sa\_account\_replication\_type) | (Optional) Defines the type of replication to use for this storage account. | `string` | `"LRS"` | no |
| <a name="input_ml_sa_account_tier"></a> [ml\_sa\_account\_tier](#input\_ml\_sa\_account\_tier) | (Optional) Defines the Tier to use for this storage account. | `string` | `"Standard"` | no |
| <a name="input_ml_workspace_identity_type"></a> [ml\_workspace\_identity\_type](#input\_ml\_workspace\_identity\_type) | (Required) Specifies the type of Managed Service Identity that should be configured on this Machine Learning Workspace. | `string` | `"SystemAssigned"` | no |
| <a name="input_storage_mngmnt_policy_kv_logs_delete_after"></a> [storage\_mngmnt\_policy\_kv\_logs\_delete\_after](#input\_storage\_mngmnt\_policy\_kv\_logs\_delete\_after) | The age in days after creation to delete the blob that stores the logs for the Key Vault | `number` | `14` | no |
| <a name="input_storage_mngmnt_policy_kv_logs_rule_name"></a> [storage\_mngmnt\_policy\_kv\_logs\_rule\_name](#input\_storage\_mngmnt\_policy\_kv\_logs\_rule\_name) | (Required) The name of the rule for the storage account management policy used to set the retention policy for the Key Vault logs. | `string` | `"Diagnostic Settings Retention Rule"` | no |
| <a name="input_training_subnet_address_range"></a> [training\_subnet\_address\_range](#input\_training\_subnet\_address\_range) | The IP range of the training subnet | `string` | `"10.0.1.0/24"` | no |
| <a name="input_vnet_address_space"></a> [vnet\_address\_space](#input\_vnet\_address\_space) | The IP range of the virtual network | `string` | `"10.0.0.0/16"` | no |
| <a name="input_vnet_enabled"></a> [vnet\_enabled](#input\_vnet\_enabled) | Specifies whether to deploy resources behind a VNET or not | `bool` | `false` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_app_insights_app_id"></a> [app\_insights\_app\_id](#output\_app\_insights\_app\_id) | n/a |
| <a name="output_app_insights_connection_string"></a> [app\_insights\_connection\_string](#output\_app\_insights\_connection\_string) | n/a |
| <a name="output_app_insights_instrumentation_key"></a> [app\_insights\_instrumentation\_key](#output\_app\_insights\_instrumentation\_key) | n/a |
| <a name="output_app_insights_name"></a> [app\_insights\_name](#output\_app\_insights\_name) | n/a |
| <a name="output_iot_hub_name"></a> [iot\_hub\_name](#output\_iot\_hub\_name) | The name of the IoT hub |
| <a name="output_key_vault_id"></a> [key\_vault\_id](#output\_key\_vault\_id) | n/a |
| <a name="output_key_vault_name"></a> [key\_vault\_name](#output\_key\_vault\_name) | The name of the shared Key Vault |
| <a name="output_log_analytics_workspace_id"></a> [log\_analytics\_workspace\_id](#output\_log\_analytics\_workspace\_id) | n/a |
| <a name="output_log_analytics_workspace_name"></a> [log\_analytics\_workspace\_name](#output\_log\_analytics\_workspace\_name) | n/a |
| <a name="output_log_analytics_workspace_sku"></a> [log\_analytics\_workspace\_sku](#output\_log\_analytics\_workspace\_sku) | n/a |
| <a name="output_resource_group_name"></a> [resource\_group\_name](#output\_resource\_group\_name) | The name of the resouce group containing all resources |
| <a name="output_resource_suffix"></a> [resource\_suffix](#output\_resource\_suffix) | n/a |
| <a name="output_storage_account_kv_logs_name"></a> [storage\_account\_kv\_logs\_name](#output\_storage\_account\_kv\_logs\_name) | n/a |
<!-- END_TF_DOCS -->
