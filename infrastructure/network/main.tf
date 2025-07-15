module "common" {
  source            = "../common"
  deployment_source = var.deployment_source
  random_suffix     = var.random_suffix
}

module "agents_tfstate" {
  source = "../pipeline-agent/remote-tfstate"

  tfstate_resource_group_name  = var.tfstate_resource_group_name
  tfstate_storage_account_name = var.tfstate_storage_account_name
  tfstate_container_name       = var.tfstate_container_name
}

locals {
  pipeline_agent_vnet_id   = module.agents_tfstate.outputs.vnet_id
  pipeline_agent_vnet_name = module.agents_tfstate.outputs.vnet_name
  pipeline_agent_subnet_id = module.agents_tfstate.outputs.agent_subnet_id
  pipeline_agent_rg_name   = module.agents_tfstate.outputs.rg_name
}

locals {
  peer_with_pipeline_vnet = var.vnet_enabled && var.peer_with_pipeline && local.pipeline_agent_subnet_id != null
}

resource "azurerm_virtual_network" "vnet" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.vnet_name
  address_space       = [var.vnet_address_space]
  location            = var.location
  resource_group_name = var.rg_name
}

resource "azurerm_subnet" "integration_subnet" {
  count                = var.vnet_enabled ? 1 : 0
  name                 = module.common.integration_subnet_name
  resource_group_name  = var.rg_name
  virtual_network_name = azurerm_virtual_network.vnet[0].name
  address_prefixes     = [var.integration_subnet_address_space]
}

resource "azurerm_virtual_network_peering" "agent_main" {
  count                        = local.peer_with_pipeline_vnet ? 1 : 0
  name                         = module.common.vnet_peering_agent_to_main
  resource_group_name          = local.pipeline_agent_rg_name
  virtual_network_name         = local.pipeline_agent_vnet_name
  remote_virtual_network_id    = azurerm_virtual_network.vnet[0].id
  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
}

resource "azurerm_virtual_network_peering" "main_agent" {
  count                        = local.peer_with_pipeline_vnet ? 1 : 0
  name                         = module.common.vnet_peering_main_to_agent
  resource_group_name          = var.rg_name
  virtual_network_name         = azurerm_virtual_network.vnet[0].name
  remote_virtual_network_id    = local.pipeline_agent_vnet_id
  allow_virtual_network_access = true
  allow_forwarded_traffic      = true
}

### Virtual Network Gateway ###

resource "azurerm_subnet" "gateway" {
  count                = var.vnet_enabled ? 1 : 0
  name                 = "GatewaySubnet"
  resource_group_name  = var.rg_name
  virtual_network_name = azurerm_virtual_network.vnet[0].name
  address_prefixes     = [var.gateway_subnet_address_space]
}

resource "azurerm_public_ip" "gateway" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.vnet_gateway_ip_name
  location            = var.location
  resource_group_name = var.rg_name
  allocation_method   = "Dynamic"
}

resource "azurerm_virtual_network_gateway" "gateway" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.vnet_gateway_name
  location            = var.location
  resource_group_name = var.rg_name
  type                = "Vpn"
  vpn_type            = "RouteBased"
  sku                 = var.vnet_gateway_sku

  ip_configuration {
    public_ip_address_id          = azurerm_public_ip.gateway[0].id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway[0].id
  }

  vpn_client_configuration {
    address_space        = [var.vpn_client_address_space]
    vpn_client_protocols = ["IkeV2", "OpenVPN"]
    root_certificate {
      name             = "terraformselfsignedcert"
      public_cert_data = data.local_file.ca_der[0].content
    }
  }

  depends_on = [data.local_file.ca_der]
}


### Azure Private DNS Zones ###

resource "azurerm_subnet" "dns_resolver" {
  count                = var.vnet_enabled ? 1 : 0
  name                 = module.common.dns_resolver_subnet_name
  resource_group_name  = var.rg_name
  virtual_network_name = azurerm_virtual_network.vnet[0].name
  address_prefixes     = [var.dns_resolver_subnet_address_space]

  delegation {
    name = "Microsoft.Network.dnsResolvers"
    service_delegation {
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
      name    = "Microsoft.Network/dnsResolvers"
    }
  }
}

resource "azurerm_private_dns_resolver" "gateway" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.private_dns_resolver_name
  resource_group_name = var.rg_name
  location            = var.location
  virtual_network_id  = azurerm_virtual_network.vnet[0].id
}

resource "azurerm_private_dns_resolver_inbound_endpoint" "gateway" {
  count                   = var.vnet_enabled ? 1 : 0
  name                    = module.common.dns_resolver_inbound_endpoint_name
  private_dns_resolver_id = azurerm_private_dns_resolver.gateway[0].id
  location                = var.location
  ip_configurations {
    private_ip_allocation_method = "Dynamic"
    subnet_id                    = azurerm_subnet.dns_resolver[0].id
  }
}

resource "azurerm_private_dns_zone" "dns_storageacc_blob" {
  count               = var.vnet_enabled ? 1 : 0
  name                = "privatelink.blob.core.windows.net"
  resource_group_name = var.rg_name
}

resource "azurerm_private_dns_zone" "ml" {
  count               = var.vnet_enabled ? 1 : 0
  name                = "privatelink.api.azureml.ms"
  resource_group_name = var.rg_name
}

resource "azurerm_private_dns_zone" "container_registry" {
  count               = var.vnet_enabled ? 1 : 0
  name                = "privatelink.azurecr.io"
  resource_group_name = var.rg_name
}

resource "azurerm_private_dns_zone" "key_vault" {
  count               = var.vnet_enabled ? 1 : 0
  name                = "privatelink.vaultcore.azure.net"
  resource_group_name = var.rg_name
}

resource "azurerm_private_dns_zone" "iot_hub" {
  count               = var.vnet_enabled ? 1 : 0
  name                = "privatelink.azure-devices.net"
  resource_group_name = var.rg_name
}

resource "azurerm_private_dns_zone" "event_hub" {
  count               = var.vnet_enabled ? 1 : 0
  name                = "privatelink.servicebus.windows.net"
  resource_group_name = var.rg_name
}


### DNS Zones to VNET Links ###
resource "azurerm_private_dns_zone_virtual_network_link" "vnet_link_kv" {
  count                 = var.vnet_enabled ? 1 : 0
  name                  = module.common.kv_dns_vnet_link_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.key_vault[0].name
  virtual_network_id    = azurerm_virtual_network.vnet[0].id
}

resource "azurerm_private_dns_zone_virtual_network_link" "vnet_link_cr" {
  count                 = var.vnet_enabled ? 1 : 0
  name                  = module.common.ml_container_registry_dns_vnet_link_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.container_registry[0].name
  virtual_network_id    = azurerm_virtual_network.vnet[0].id
}

resource "azurerm_private_dns_zone_virtual_network_link" "vnet_link_blob" {
  count                 = var.vnet_enabled ? 1 : 0
  name                  = module.common.ml_blobstorage_dnszone_vnetlink_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.dns_storageacc_blob[0].name
  virtual_network_id    = azurerm_virtual_network.vnet[0].id
}

resource "azurerm_private_dns_zone_virtual_network_link" "vnet_link_ml" {
  count                 = var.vnet_enabled ? 1 : 0
  name                  = module.common.ml_dns_vnet_link_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.ml[0].name
  virtual_network_id    = azurerm_virtual_network.vnet[0].id
}

resource "azurerm_private_dns_zone_virtual_network_link" "vnet_link_iot_hub" {
  count                 = var.vnet_enabled ? 1 : 0
  name                  = module.common.iothub_dns_vnet_link_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.iot_hub[0].name
  virtual_network_id    = azurerm_virtual_network.vnet[0].id
}

resource "azurerm_private_dns_zone_virtual_network_link" "vnet_link_event_hub" {
  count                 = var.vnet_enabled ? 1 : 0
  name                  = module.common.eventhub_dns_vnet_link_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.event_hub[0].name
  virtual_network_id    = azurerm_virtual_network.vnet[0].id
}

resource "azurerm_private_dns_zone_virtual_network_link" "agent_vnet_link_kv" {
  count                 = local.peer_with_pipeline_vnet ? 1 : 0
  name                  = module.common.kv_dns_agent_vnet_link_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.key_vault[0].name
  virtual_network_id    = local.pipeline_agent_vnet_id
}

resource "azurerm_private_dns_zone_virtual_network_link" "agent_vnet_link_cr" {
  count                 = local.peer_with_pipeline_vnet ? 1 : 0
  name                  = module.common.ml_container_registry_dns_agent_vnet_link_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.container_registry[0].name
  virtual_network_id    = local.pipeline_agent_vnet_id
}

resource "azurerm_private_dns_zone_virtual_network_link" "agent_vnet_link_blob" {
  count                 = local.peer_with_pipeline_vnet ? 1 : 0
  name                  = module.common.ml_blobstorage_dnszone_agent_vnetlink_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.dns_storageacc_blob[0].name
  virtual_network_id    = local.pipeline_agent_vnet_id
}

resource "azurerm_private_dns_zone_virtual_network_link" "agent_vnet_link_ml" {
  count                 = local.peer_with_pipeline_vnet ? 1 : 0
  name                  = module.common.ml_dns_agent_vnet_link_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.ml[0].name
  virtual_network_id    = local.pipeline_agent_vnet_id
}

resource "azurerm_private_dns_zone_virtual_network_link" "agent_vnet_link_iot_hub" {
  count                 = local.peer_with_pipeline_vnet ? 1 : 0
  name                  = module.common.iothub_dns_agent_vnet_link_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.iot_hub[0].name
  virtual_network_id    = local.pipeline_agent_vnet_id
}

resource "azurerm_private_dns_zone_virtual_network_link" "agent_vnet_link_event_hub" {
  count                 = local.peer_with_pipeline_vnet ? 1 : 0
  name                  = module.common.eventhub_dns_agent_vnet_link_name
  resource_group_name   = var.rg_name
  private_dns_zone_name = azurerm_private_dns_zone.event_hub[0].name
  virtual_network_id    = local.pipeline_agent_vnet_id
}
