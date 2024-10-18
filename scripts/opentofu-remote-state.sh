#!/bin/bash

# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

# Optional parameters can be supplied
# i.e ./opentofu-remote-state.sh -e "local" -l "westus"
# will create a resource group with name "tfstatelocal" located in the "westus" region

#If no optional parameters are supplied then the default values are used, an empty string for environment and westeurope region
#i.e ./opentofu-remote-state.sh will create a resource group with name "tfstate" located in "westeurope" region

TF_LOCATION="westeurope"
TF_ENVIRONMENT=""

while [ $# -gt 0 ]; do
    if [[ $1 == "-l" ]]; then
        TF_LOCATION="$2"
    fi
    if [[ $1 == "-e" ]]; then
        TF_ENVIRONMENT="$2"
    fi
    shift
done

echo TF_LOCATION=$TF_LOCATION
echo TF_ENVIRONMENT=$TF_ENVIRONMENT


TF_VAR_resource_group_name=tfstate$TF_ENVIRONMENT
TF_VAR_storage_account_name=tfstate$RANDOM
TF_VAR_container_name=tfstate

# Create resource group
az group create --name $TF_VAR_resource_group_name --location $TF_LOCATION

# Create storage account
az storage account create --resource-group $TF_VAR_resource_group_name --name $TF_VAR_storage_account_name --sku Standard_LRS --encryption-services blob

# Create blob container
az storage container create --name $TF_VAR_container_name --account-name $TF_VAR_storage_account_name

#Use an acccess key to authenticate to the storage account
ACCOUNT_KEY=$(az storage account keys list --resource-group $TF_VAR_resource_group_name --account-name $TF_VAR_storage_account_name --query '[0].value' -o tsv)

#After the creation of the access key this is set as an environment variable for OpenTofu
export ARM_ACCESS_KEY=$ACCOUNT_KEY

#Display the resource name
echo "TF_VAR_resource_group_name=$TF_VAR_resource_group_name"
echo "TF_VAR_storage_account_name=$TF_VAR_storage_account_name"
echo "TF_VAR_container_name=$TF_VAR_container_name"
echo "LOCATION=$TF_LOCATION"

export TF_VAR_resource_group_name=$TF_VAR_resource_group_name
export TF_VAR_storage_account_name=$TF_VAR_storage_account_name
export TF_VAR_container_name=$TF_VAR_container_name
export LOCATION=$TF_LOCATION
