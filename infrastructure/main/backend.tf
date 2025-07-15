# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

terraform {
  backend "azurerm" {
    key = "terraform.tfstate"
  }
}
