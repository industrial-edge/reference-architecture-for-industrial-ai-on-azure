terraform {
  backend "azurerm" {
    key = "agents.tfstate"
  }
}
