# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

output "outputs" {
  value = data.terraform_remote_state.agents.outputs
}
