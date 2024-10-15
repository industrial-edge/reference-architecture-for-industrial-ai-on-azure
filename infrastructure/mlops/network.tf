resource "azurerm_subnet" "training_subnet" {
  count                = var.vnet_enabled ? 1 : 0
  name                 = module.common.ml_compute_cluster_subnet_name
  resource_group_name  = var.rg_name
  virtual_network_name = var.vnet_name
  address_prefixes     = [var.training_subnet_address_range]
}

resource "azurerm_network_security_group" "training_subnet" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.ml_training_subnet_nsg_name
  location            = var.location
  resource_group_name = var.rg_name

  security_rule {
    name                       = "BatchNodeManagement"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "29876-29877"
    source_address_prefix      = "BatchNodeManagement"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AzureMachineLearning"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "44224"
    source_address_prefix      = "AzureMachineLearning"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AzureActiveDirectory"
    priority                   = 120
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "AzureActiveDirectory"
  }

  security_rule {
    name                       = "BatchNodeManagementOutbound"
    priority                   = 130
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "BatchNodeManagement.${var.location}"
  }

  security_rule {
    name                       = "AzureMachineLearningOutbound"
    priority                   = 140
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "AzureMachineLearning"
  }

  security_rule {
    name                       = "AzureStorageAccount"
    priority                   = 150
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "Storage.${var.location}"
  }

  security_rule {
    name                       = "AzureFrontDoor"
    priority                   = 160
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "AzureFrontDoor.FrontEnd"
  }

  security_rule {
    name                       = "AzureContainerRegistry"
    priority                   = 170
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "AzureContainerRegistry.${var.location}"
  }

  security_rule {
    name                       = "MicrosoftContainerRegistry"
    priority                   = 180
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "VirtualNetwork"
    destination_address_prefix = "MicrosoftContainerRegistry"
  }
}

resource "azurerm_subnet_network_security_group_association" "training_nsg" {
  count                     = var.vnet_enabled ? 1 : 0
  subnet_id                 = azurerm_subnet.training_subnet[0].id
  network_security_group_id = azurerm_network_security_group.training_subnet[0].id
}

resource "azurerm_private_endpoint" "ml" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.ml_workspace_private_endpoint_name
  location            = var.location
  resource_group_name = var.rg_name
  subnet_id           = var.integration_subnet_id

  private_dns_zone_group {
    name                 = module.common.private_dns_zone_group_name
    private_dns_zone_ids = [var.ml_private_dns_zone_id]
  }

  private_service_connection {
    name                           = module.common.ml_workspace_private_service_connection_name
    private_connection_resource_id = azurerm_machine_learning_workspace.ml.id
    subresource_names              = ["amlworkspace"]
    is_manual_connection           = false
  }
}

resource "azurerm_private_endpoint" "container_registry" {
  count               = var.vnet_enabled ? 1 : 0
  name                = module.common.ml_container_registry_private_endpoint_name
  location            = var.location
  resource_group_name = var.rg_name
  subnet_id           = var.integration_subnet_id

  private_dns_zone_group {
    name                 = module.common.private_dns_zone_group_name
    private_dns_zone_ids = [var.cr_private_dns_zone_id]
  }

  private_service_connection {
    name                           = module.common.ml_container_registry_private_service_connection_name
    private_connection_resource_id = azurerm_container_registry.ml.id
    subresource_names              = ["registry"]
    is_manual_connection           = false
  }
}

resource "azurerm_private_endpoint" "storage_account_blob" {
   count                = var.vnet_enabled ? 1 : 0
   name                = module.common.ml_blobstorage_private_endpoint_name
   location            = var.location
   resource_group_name = var.rg_name
   subnet_id           = var.integration_subnet_id

   private_service_connection {
     name                           = module.common.ml_blobstorage_private_service_connection_name
     private_connection_resource_id = azurerm_storage_account.ml.id
     subresource_names              = ["blob"]
     is_manual_connection           = false
   }

   private_dns_zone_group {
     name = module.common.private_dns_zone_group_name
     private_dns_zone_ids = [var.private_dns_zone_id_stg_blob]
   }
}
