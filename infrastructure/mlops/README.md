<!--
SPDX-FileCopyrightText: 2025 Siemens AG

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
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | >= 3.35.0, < 4.0.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_common"></a> [common](#module\_common) | ../common | n/a |

## Resources

| Name | Type |
|------|------|
| [azurerm_container_registry.ml](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/container_registry) | resource |
| [azurerm_key_vault_secret.ml](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_machine_learning_compute_cluster.ml](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/machine_learning_compute_cluster) | resource |
| [azurerm_machine_learning_workspace.ml](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/machine_learning_workspace) | resource |
| [azurerm_private_dns_zone.container_registry](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone) | resource |
| [azurerm_private_dns_zone.ml](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone) | resource |
| [azurerm_private_dns_zone_virtual_network_link.container_registry](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone_virtual_network_link) | resource |
| [azurerm_private_dns_zone_virtual_network_link.ml](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_dns_zone_virtual_network_link) | resource |
| [azurerm_private_endpoint.container_registry](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_private_endpoint.ml](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_storage_account.ml](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account) | resource |
| [azurerm_subnet.training_subnet](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subnet) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_appinsights_id"></a> [appinsights\_id](#input\_appinsights\_id) | The id of the application insights | `string` | n/a | yes |
| <a name="input_cc_scale_down_after_idle_duration"></a> [cc\_scale\_down\_after\_idle\_duration](#input\_cc\_scale\_down\_after\_idle\_duration) | Node Idle Time Before Scale Down: defines the time until the compute is shutdown when it has gone into Idle state. Is defined according to W3C XML schema standard for duration. Changing this forces a new Machine Learning Compute Cluster to be created. | `string` | n/a | yes |
| <a name="input_cc_scale_settings_max_node_count"></a> [cc\_scale\_settings\_max\_node\_count](#input\_cc\_scale\_settings\_max\_node\_count) | Maximum node count. Changing this forces a new Machine Learning Compute Cluster to be created. | `number` | n/a | yes |
| <a name="input_cc_scale_settings_min_node_count"></a> [cc\_scale\_settings\_min\_node\_count](#input\_cc\_scale\_settings\_min\_node\_count) | Minimum node count. Changing this forces a new Machine Learning Compute Cluster to be created. | `number` | n/a | yes |
| <a name="input_compute_cluster_identity_type"></a> [compute\_cluster\_identity\_type](#input\_compute\_cluster\_identity\_type) | Compute cluster identity type. Changing this forces a new Machine Learning Compute Cluster to be created. | `string` | n/a | yes |
| <a name="input_compute_cluster_vm_priority"></a> [compute\_cluster\_vm\_priority](#input\_compute\_cluster\_vm\_priority) | The priority of the Virtual Machine. Changing this forces a new Machine Learning Compute Cluster to be created. | `string` | n/a | yes |
| <a name="input_compute_cluster_vm_size"></a> [compute\_cluster\_vm\_size](#input\_compute\_cluster\_vm\_size) | The size of the Virtual Machine. Changing this forces a new Machine Learning Compute Cluster to be created. | `string` | n/a | yes |
| <a name="input_container_registry_admin_enabled"></a> [container\_registry\_admin\_enabled](#input\_container\_registry\_admin\_enabled) | Specifies whether the admin user is enabled. Defaults to false | `bool` | n/a | yes |
| <a name="input_container_registry_sku"></a> [container\_registry\_sku](#input\_container\_registry\_sku) | (Required)The SKU name of the container registry. Possible values are Basic, Standard and Premium. | `string` | n/a | yes |
| <a name="input_deployment_source"></a> [deployment\_source](#input\_deployment\_source) | The deployment source (e.g dev) | `string` | n/a | yes |
| <a name="input_integration_subnet_id"></a> [integration\_subnet\_id](#input\_integration\_subnet\_id) | The id range of the integration subnet for private endpoints | `string` | n/a | yes |
| <a name="input_kv_id"></a> [kv\_id](#input\_kv\_id) | The id of the keyvault | `string` | n/a | yes |
| <a name="input_location"></a> [location](#input\_location) | Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created. | `string` | n/a | yes |
| <a name="input_ml_workspace_identity_type"></a> [ml\_workspace\_identity\_type](#input\_ml\_workspace\_identity\_type) | Specifies the type of Managed Service Identity that should be configured on this Machine Learning Workspace. | `string` | n/a | yes |
| <a name="input_rg_name"></a> [rg\_name](#input\_rg\_name) | The name of the resource group | `string` | n/a | yes |
| <a name="input_sa_access_tier"></a> [sa\_access\_tier](#input\_sa\_access\_tier) | Defines the access tier for BlobStorage, FileStorage and StorageV2 accounts. | `string` | n/a | yes |
| <a name="input_sa_account_kind"></a> [sa\_account\_kind](#input\_sa\_account\_kind) | Defines the Kind of account. | `string` | n/a | yes |
| <a name="input_sa_account_replication_type"></a> [sa\_account\_replication\_type](#input\_sa\_account\_replication\_type) | Defines the type of replication to use for this storage account. | `string` | n/a | yes |
| <a name="input_sa_account_tier"></a> [sa\_account\_tier](#input\_sa\_account\_tier) | Defines the Tier to use for this storage account. | `string` | n/a | yes |
| <a name="input_training_subnet_address_range"></a> [training\_subnet\_address\_range](#input\_training\_subnet\_address\_range) | The IP range of the training subnet | `string` | n/a | yes |
| <a name="input_vnet_enabled"></a> [vnet\_enabled](#input\_vnet\_enabled) | Specifies whether to deploy resources behind a VNET or not | `bool` | n/a | yes |
| <a name="input_vnet_id"></a> [vnet\_id](#input\_vnet\_id) | The id of the virtual network | `string` | n/a | yes |
| <a name="input_vnet_name"></a> [vnet\_name](#input\_vnet\_name) | The name of the virtual network | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_compute_cluster_id"></a> [compute\_cluster\_id](#output\_compute\_cluster\_id) | n/a |
| <a name="output_compute_cluster_name"></a> [compute\_cluster\_name](#output\_compute\_cluster\_name) | n/a |
| <a name="output_container_registry_name"></a> [container\_registry\_name](#output\_container\_registry\_name) | n/a |
| <a name="output_key_vault_secret_cr_name"></a> [key\_vault\_secret\_cr\_name](#output\_key\_vault\_secret\_cr\_name) | n/a |
| <a name="output_machine_learning_workspace_name"></a> [machine\_learning\_workspace\_name](#output\_machine\_learning\_workspace\_name) | The Azure Machine Learning Workspace name. |
| <a name="output_rg_name"></a> [rg\_name](#output\_rg\_name) | n/a |
| <a name="output_storage_account_id"></a> [storage\_account\_id](#output\_storage\_account\_id) | The Azure Storage Account ID. |
| <a name="output_storage_blob_primary_url"></a> [storage\_blob\_primary\_url](#output\_storage\_blob\_primary\_url) | The endpoint URL for blob storage in the primary location. |
| <a name="output_storage_name"></a> [storage\_name](#output\_storage\_name) | The Azure Storage Account name. |
| <a name="output_storage_primary_access_key"></a> [storage\_primary\_access\_key](#output\_storage\_primary\_access\_key) | The hostname with port if applicable for blob storage in the secondary location. |
| <a name="output_storage_primary_connection_string"></a> [storage\_primary\_connection\_string](#output\_storage\_primary\_connection\_string) | The connection string associated with the primary location. |
<!-- END_TF_DOCS -->
