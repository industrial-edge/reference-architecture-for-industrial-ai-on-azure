# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}
