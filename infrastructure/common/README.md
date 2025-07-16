<!--
SPDX-FileCopyrightText: 2025 Siemens AG

SPDX-License-Identifier: MIT
-->

<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

No providers.

## Modules

No modules.

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_deployment_source"></a> [deployment\_source](#input\_deployment\_source) | The deployment source (e.g dev) | `string` | n/a | yes |
| <a name="input_random_suffix"></a> [random\_suffix](#input\_random\_suffix) | The suffix appended to the resource names | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_ampls_name"></a> [ampls\_name](#output\_ampls\_name) | n/a |
| <a name="output_ampls_private_endpoint_name"></a> [ampls\_private\_endpoint\_name](#output\_ampls\_private\_endpoint\_name) | n/a |
| <a name="output_ampls_private_service_connection_name"></a> [ampls\_private\_service\_connection\_name](#output\_ampls\_private\_service\_connection\_name) | n/a |
| <a name="output_application_insights_name"></a> [application\_insights\_name](#output\_application\_insights\_name) | n/a |
| <a name="output_failure_anomaly_name"></a> [failure\_anomaly\_name](#output\_failure\_anomaly\_name) | n/a |
| <a name="output_integration_subnet_name"></a> [integration\_subnet\_name](#output\_integration\_subnet\_name) | n/a |
| <a name="output_iothub_name"></a> [iothub\_name](#output\_iothub\_name) | # IoT Management ## |
| <a name="output_kv_ai_application_id_secret_name"></a> [kv\_ai\_application\_id\_secret\_name](#output\_kv\_ai\_application\_id\_secret\_name) | The name of the secret stored in Key Vault containing the Application Insights Id |
| <a name="output_kv_ai_connection_string_secret_name"></a> [kv\_ai\_connection\_string\_secret\_name](#output\_kv\_ai\_connection\_string\_secret\_name) | The name of the secret stored in Key Vault containing the Application Insights connection string |
| <a name="output_kv_cr_name_secret_name"></a> [kv\_cr\_name\_secret\_name](#output\_kv\_cr\_name\_secret\_name) | The name of the secret stored in Key Vault containing the name of the ML container registry |
| <a name="output_kv_dns_vnet_link_name"></a> [kv\_dns\_vnet\_link\_name](#output\_kv\_dns\_vnet\_link\_name) | n/a |
| <a name="output_kv_eventhub_compatible_endpoint_secret_name"></a> [kv\_eventhub\_compatible\_endpoint\_secret\_name](#output\_kv\_eventhub\_compatible\_endpoint\_secret\_name) | The name of the secret stored in Key Vault containing the Event Hub compatible endpoint |
| <a name="output_kv_iothub_connection_string_secret_name"></a> [kv\_iothub\_connection\_string\_secret\_name](#output\_kv\_iothub\_connection\_string\_secret\_name) | The name of the secret stored in Key Vault containing the IoT Hub connection string |
| <a name="output_kv_iothub_eventhubendpoint_secret_name"></a> [kv\_iothub\_eventhubendpoint\_secret\_name](#output\_kv\_iothub\_eventhubendpoint\_secret\_name) | The name of the secret stored in Key Vault containing the IoT Hub Event Hub Endpoint |
| <a name="output_kv_iothub_name_secret_name"></a> [kv\_iothub\_name\_secret\_name](#output\_kv\_iothub\_name\_secret\_name) | The name of the secret stored in Key Vault containing the IoT Hub name |
| <a name="output_kv_logs_storage_account_name"></a> [kv\_logs\_storage\_account\_name](#output\_kv\_logs\_storage\_account\_name) | n/a |
| <a name="output_kv_monitor_diagnostic_setting_name"></a> [kv\_monitor\_diagnostic\_setting\_name](#output\_kv\_monitor\_diagnostic\_setting\_name) | n/a |
| <a name="output_kv_name"></a> [kv\_name](#output\_kv\_name) | n/a |
| <a name="output_kv_private_endpoint_name"></a> [kv\_private\_endpoint\_name](#output\_kv\_private\_endpoint\_name) | n/a |
| <a name="output_kv_private_service_connection_name"></a> [kv\_private\_service\_connection\_name](#output\_kv\_private\_service\_connection\_name) | n/a |
| <a name="output_kv_suffix_secret_name"></a> [kv\_suffix\_secret\_name](#output\_kv\_suffix\_secret\_name) | The name of the secret stored in Key Vault containing the random suffix |
| <a name="output_log_analytics_workspace_name"></a> [log\_analytics\_workspace\_name](#output\_log\_analytics\_workspace\_name) | n/a |
| <a name="output_ml_blobstorage_dnszone_vnetlink_name"></a> [ml\_blobstorage\_dnszone\_vnetlink\_name](#output\_ml\_blobstorage\_dnszone\_vnetlink\_name) | n/a |
| <a name="output_ml_blobstorage_private_endpoint_name"></a> [ml\_blobstorage\_private\_endpoint\_name](#output\_ml\_blobstorage\_private\_endpoint\_name) | #MLOps VNET## |
| <a name="output_ml_blobstorage_private_service_connection_name"></a> [ml\_blobstorage\_private\_service\_connection\_name](#output\_ml\_blobstorage\_private\_service\_connection\_name) | n/a |
| <a name="output_ml_compute_cluster_name"></a> [ml\_compute\_cluster\_name](#output\_ml\_compute\_cluster\_name) | n/a |
| <a name="output_ml_compute_cluster_subnet_name"></a> [ml\_compute\_cluster\_subnet\_name](#output\_ml\_compute\_cluster\_subnet\_name) | # MLOps ## |
| <a name="output_ml_container_registry_dns_vnet_link_name"></a> [ml\_container\_registry\_dns\_vnet\_link\_name](#output\_ml\_container\_registry\_dns\_vnet\_link\_name) | n/a |
| <a name="output_ml_container_registry_name"></a> [ml\_container\_registry\_name](#output\_ml\_container\_registry\_name) | n/a |
| <a name="output_ml_container_registry_private_endpoint_name"></a> [ml\_container\_registry\_private\_endpoint\_name](#output\_ml\_container\_registry\_private\_endpoint\_name) | n/a |
| <a name="output_ml_container_registry_private_service_connection_name"></a> [ml\_container\_registry\_private\_service\_connection\_name](#output\_ml\_container\_registry\_private\_service\_connection\_name) | n/a |
| <a name="output_ml_dns_vnet_link_name"></a> [ml\_dns\_vnet\_link\_name](#output\_ml\_dns\_vnet\_link\_name) | n/a |
| <a name="output_ml_storage_account_name"></a> [ml\_storage\_account\_name](#output\_ml\_storage\_account\_name) | n/a |
| <a name="output_ml_training_subnet_nsg_name"></a> [ml\_training\_subnet\_nsg\_name](#output\_ml\_training\_subnet\_nsg\_name) | n/a |
| <a name="output_ml_workspace_name"></a> [ml\_workspace\_name](#output\_ml\_workspace\_name) | n/a |
| <a name="output_ml_workspace_private_endpoint_name"></a> [ml\_workspace\_private\_endpoint\_name](#output\_ml\_workspace\_private\_endpoint\_name) | n/a |
| <a name="output_ml_workspace_private_service_connection_name"></a> [ml\_workspace\_private\_service\_connection\_name](#output\_ml\_workspace\_private\_service\_connection\_name) | n/a |
| <a name="output_monitor_action_group_name"></a> [monitor\_action\_group\_name](#output\_monitor\_action\_group\_name) | n/a |
| <a name="output_private_dns_zone_group_name"></a> [private\_dns\_zone\_group\_name](#output\_private\_dns\_zone\_group\_name) | n/a |
| <a name="output_rg_name"></a> [rg\_name](#output\_rg\_name) | n/a |
| <a name="output_vnet_name"></a> [vnet\_name](#output\_vnet\_name) | n/a |
<!-- END_TF_DOCS -->
