#!/bin/bash

# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

helpFunction()
{
    echo ""
    echo "Usage: $0 -s subscriptionId -k keyVaultName -d deviceName -t tenantId -c (true/false)"
    echo -e "\t-s Subscription Id"
    echo -e "\t-k Key Vault Name"
    echo -e "\t-d Device Name"
    echo -e "\t-t Tenant Id"
    echo -e "\t-c Use Device Code authentication"
    exit 1 # Exit script after printing help
}

while getopts "s:k:d:t:c:" opt
do
   case "$opt" in
      s ) subscriptionId="$OPTARG" ;;
      k ) keyVaultName="$OPTARG" ;;
      d ) deviceName="$OPTARG" ;;
        t ) tenantId="$OPTARG" ;;
        c ) useDeviceCode="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$subscriptionId" ] || [ -z "$keyVaultName" ] || [ -z "$deviceName" ] || [ -z "$tenantId" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

if [ -z "$useDeviceCode" ]
then
    useDeviceCode="false"
fi

if $useDeviceCode
then
    az login --tenant $tenantId --use-device-code
else
    az login --tenant $tenantId
fi

az account set --subscription $subscriptionId

echo "Retrieving unique KeyVault-Suffix"
keyvaultSuffix=$(az keyvault secret show --vault-name $keyVaultName --name "KeyVault-Suffix" --query value -o tsv | tr -d '\r')
echo "keyvaultSuffix: $keyvaultSuffix"

secretName="Model-Monitor-$deviceName-Configuration-$keyvaultSuffix"

echo "Retrieving Model Monitor Configuration"
modelMonitorConfiguration=$(az keyvault secret show --vault-name $keyVaultName --name $secretName --query value -o tsv | tr -d '\r')

echo $modelMonitorConfiguration > "Model-Monitor-$deviceName-Configuration.json"
