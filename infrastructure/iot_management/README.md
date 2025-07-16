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
| [azurerm_iothub.iothub](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/iothub) | resource |
| [azurerm_key_vault_secret.iothub_kv_connstring](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_key_vault_secret.iothub_kv_eventhub_compatible_endpoint](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_key_vault_secret.iothub_kv_eventhubendpoint](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_key_vault_secret.iothub_kv_iothubname](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_secret) | resource |
| [azurerm_iothub_shared_access_policy.iothub](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/iothub_shared_access_policy) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_deployment_source"></a> [deployment\_source](#input\_deployment\_source) | The deployment source (e.g dev) | `string` | n/a | yes |
| <a name="input_iothub_eventhub_shared_access_policy_name"></a> [iothub\_eventhub\_shared\_access\_policy\_name](#input\_iothub\_eventhub\_shared\_access\_policy\_name) | The name of the shared access policy of the IoT Hub | `string` | n/a | yes |
| <a name="input_iothub_sku_capacity"></a> [iothub\_sku\_capacity](#input\_iothub\_sku\_capacity) | The number of provisioned IoT Hub units. | `number` | n/a | yes |
| <a name="input_iothub_sku_name"></a> [iothub\_sku\_name](#input\_iothub\_sku\_name) | The name of the sku. Possible values are B1, B2, B3, F1, S1, S2, and S3. | `string` | n/a | yes |
| <a name="input_kv_id"></a> [kv\_id](#input\_kv\_id) | The id of the keyvault | `string` | n/a | yes |
| <a name="input_location"></a> [location](#input\_location) | Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created. | `string` | n/a | yes |
| <a name="input_rg_name"></a> [rg\_name](#input\_rg\_name) | The name of the resource group | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_iot_hub_name"></a> [iot\_hub\_name](#output\_iot\_hub\_name) | n/a |
| <a name="output_rg_name"></a> [rg\_name](#output\_rg\_name) | n/a |
<!-- END_TF_DOCS -->
