resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

module "common" {
  source            = "../common"
  deployment_source = var.deployment_source
  random_suffix     = random_string.suffix.result
}

resource "azurerm_resource_group" "rg" {
  name     = module.common.agent_rg_name
  location = var.location
  tags     = { "Deployment:Source" : var.deployment_source }
}

resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "azurerm_linux_virtual_machine_scale_set" "agent" {
  name                = module.common.agent_vm_scaleset_name
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = var.sku
  admin_username      = var.agent_name
  instances           = var.number_of_agents

  network_interface {
    name    = module.common.agent_network_interface
    primary = true

    ip_configuration {
      name      = module.common.agent_vm_scaleset_name
      subnet_id = azurerm_subnet.default.id
      primary   = true
      public_ip_address {
        name = module.common.agent_public_ip
      }
    }
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts"
    version   = "latest"
  }

  admin_ssh_key {
    username   = var.agent_name
    public_key = tls_private_key.ssh.public_key_openssh
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_virtual_machine_scale_set_extension" "agent" {
  name                         = module.common.agent_vm_scaleset_extension_name
  publisher                    = "Microsoft.Azure.Extensions"
  type                         = "CustomScript"
  type_handler_version         = "2.1"
  virtual_machine_scale_set_id = azurerm_linux_virtual_machine_scale_set.agent.id

  settings = jsonencode({
    "script" = "${base64encode(templatefile("../../scripts/agent-init.sh", {
      AGENT_NAME           = "${var.agent_name}",
      AZDO_PAT             = "${var.azdo_pat}",
      AZDO_ORG_SERVICE_URL = "${var.azdo_org_service_url}",
      AGENT_POOL           = "${var.agent_pool}"
    }))}"
  })
}
