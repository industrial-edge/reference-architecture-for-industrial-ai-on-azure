<!--
SPDX-FileCopyrightText: 2025 Siemens AG

SPDX-License-Identifier: MIT
-->

# Deployment

This document describes the deployment strategy for the Siemens Azure Enablement infrastructure.

To set up a new environment from scratch you first need to deploy the resources required by the Terraform backend configuration by following the steps outlined in [Terraform remote state document](terraform_remote_state.md).
*Note:* This is a one time step when you are first deploying your configuration. It doesn't need to be done for any other subsequent deployment.

###  Setting up the environment

Before running the deployment you need to set some environment variables which are already added to the file `.devcontainer/devcontainer.env`:
- ARM_SUBSCRIPTION_ID: Subscription id from Azure Portal
- ARM_TENANT_ID: Credentials for the Service Principal Authentication (Can be found in GitLab secrets)
- ARM_CLIENT_ID: Credentials for the Service Principal Authentication (Can be found in GitLab secrets)
- ARM_CLIENT_SECRET: Credentials for the Service Principal Authentication (Can be found in GitLab secrets)
- LOCATION: Default deployment location (can be skipped)
- TF_VAR_RESOURCE_GROUP_NAME: Terraform State RG
- TF_VAR_STORAGE_ACCOUNT_NAME: Terraform State Storage Account Name
- TF_VAR_CONTAINER_NAME: Terraform State Container Name

## The [deploy-infra.sh](/scripts/deploy-infra.sh) script

This script will deploy the Terraform modules into the resource group stored in the state. It authenticates using the Service Principal credentials.
Run `./scripts/deploy-infra.sh -h` for usage details:
- `-s | --source`: Source of deployment to deploy (Optional). This value will be used to tag the resource group and to name the Terraform state file. The default name for the Terraform state file is 'terraform.tfstate'.
- `-l | --location`: Location to deploy to (Optional). If not specified it will use the default location set in environment variables or Terraform configuration.
- `-v | --extra-var`: Can be used for any Terraform module extra variable, multiple times. Before passing an argument here make sure it is configured in `variables.tf` file inside the main module.
- `--skip-tests`: Skips the tests execution.

The main module represents the entry point of the script.

## Test execution

The module tests are run prior to executing the configuration. If one of the tests fail, the script execution stops.
Test execution can be skipped using the '--skip-tests' argument.

## Getting Terraform output

The script [deploy-infra.sh](/scripts/deploy-infra.sh] currently displays output variables pulled from the Terraform remote state.
