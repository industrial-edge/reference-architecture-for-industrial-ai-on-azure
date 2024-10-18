# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

variable "deployment_source" {
  type        = string
  description = "The deployment source (e.g dev)"
}

variable "random_suffix" {
  type        = string
  description = "The suffix appended to the resource names"
}
