# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

terraform {
  backend "azurerm" {
    key = "agents.tfstate"
  }
}
