# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

output "outputs" {
  value = data.terraform_remote_state.agents.outputs
}
