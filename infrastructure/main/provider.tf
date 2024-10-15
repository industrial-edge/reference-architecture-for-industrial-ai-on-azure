# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

terraform {
  required_version = ">= 0.13"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.35.0, < 4.0.0"
    }
  }
}

provider "azurerm" {
  features {
  }
}
