<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# Resource cleanup scheduled job

We have a nightly CI/CD job configured in [.gitlab-ci.yml](https://code.siemens.com/di-fa-industrial-ai/partners/microsoft/azure-enablement/azure-enablement/-/blob/main/.gitlab-ci.yml) file that runs on a schedule and deletes all the redundant resource groups. Currently it is set to run nightly at 3:00AM UTC time using 'main' as target branch.  
The schedule can be found [here](https://code.siemens.com/di-fa-industrial-ai/partners/microsoft/azure-enablement/azure-enablement/-/pipeline_schedules) having the description "Deleting unnecessary Azure resources".  

## Context  

During the Terraform test execution, there might be additional resources added to the resource group deployed which are not part of our configuration. Since these don't exist in the Terraform state, they will not be removed as part of the destroy step. This prevents the resource group from being deleted and we might end up with a large number of redundant resource groups.
The purpose of the scheduled job is to prevent this from happening.

## Steps

The job utilizes the Azure CLI (Command-Line Interface) to automate the cleanup of Azure resource groups by performing the following steps:

1. Log in to Azure using the Service Principal credentials.
1. Retrieve a list of Azure resource groups whose names start with either "rg-dev-" or "rg-test-" and delete them.
1. Log out.
