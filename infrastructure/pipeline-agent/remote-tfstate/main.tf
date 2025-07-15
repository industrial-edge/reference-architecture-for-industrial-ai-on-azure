data "terraform_remote_state" "agents" {
  backend = "azurerm"
  config = {
    resource_group_name  = var.tfstate_resource_group_name
    storage_account_name = var.tfstate_storage_account_name
    container_name       = var.tfstate_container_name

    key                  = "agents.tfstate"
  }
  defaults = {
    rg_name = null
    vnet_id = null
    vnet_name = null
    agent_subnet_id = null
  }
}
