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
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | >= 3.35.0, < 4.0.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_common"></a> [common](#module\_common) | ../common | n/a |

## Resources

| Name | Type |
|------|------|
| [azurerm_subnet.integration_subnet](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subnet) | resource |
| [azurerm_virtual_network.vnet](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/virtual_network) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_deployment_source"></a> [deployment\_source](#input\_deployment\_source) | The deployment source (e.g dev) | `string` | n/a | yes |
| <a name="input_integration_subnet_address_space"></a> [integration\_subnet\_address\_space](#input\_integration\_subnet\_address\_space) | The IP range of the integration subnet | `string` | n/a | yes |
| <a name="input_location"></a> [location](#input\_location) | (Required) Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created. | `string` | n/a | yes |
| <a name="input_rg_name"></a> [rg\_name](#input\_rg\_name) | The name of the resource group | `string` | n/a | yes |
| <a name="input_vnet_address_space"></a> [vnet\_address\_space](#input\_vnet\_address\_space) | The IP range of the virtual network | `string` | n/a | yes |
| <a name="input_vnet_enabled"></a> [vnet\_enabled](#input\_vnet\_enabled) | Specifies whether to deploy resources behind a VNET or not | `bool` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_integration_subnet_id"></a> [integration\_subnet\_id](#output\_integration\_subnet\_id) | n/a |
| <a name="output_integration_subnet_name"></a> [integration\_subnet\_name](#output\_integration\_subnet\_name) | n/a |
| <a name="output_vnet_id"></a> [vnet\_id](#output\_vnet\_id) | n/a |
| <a name="output_vnet_name"></a> [vnet\_name](#output\_vnet\_name) | n/a |
<!-- END_TF_DOCS -->
