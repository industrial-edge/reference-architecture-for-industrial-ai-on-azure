#!/bin/bash

# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

echo "Add Certificate to App Registration"

helpFunction()
{
    echo ""
    echo "Usage: $0 -s subscriptionId -k keyVaultName -c clientId -x keyvault_suffix -d deviceName -a true/false"
    echo -e "\t-s Subscription Id"
    echo -e "\t-k Key Vault Name"
    echo -e "\t-d Device Name"
    echo -e "\t-x KeyVault Suffix"
    echo -e "\t-c Client Id"
    echo -e "\t-a Append App Credentials (true/false)"
    exit 1 # Exit script after printing help
}

while getopts "s:k:d:x:c:a:" opt
do
   case "$opt" in
      s ) subscriptionId="$OPTARG" ;;
      k ) keyVaultName="$OPTARG" ;;
      d ) deviceName="$OPTARG" ;;
      x) keyvaultSuffix="$OPTARG" ;;
      c) clientId="$OPTARG" ;;
      a) appendAppCredentials="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$subscriptionId" ] || [ -z "$keyVaultName" ] || [ -z "$deviceName" ] || [ -z "$clientId" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

echo "Setting subscription to $subscriptionId"
az account set --subscription $subscriptionId

if [ -z $keyvaultSuffix ]
then
    echo "Retrieving unique KeyVault-Suffix"
    keyvaultSuffix=$(az keyvault secret show --vault-name $keyVaultName --name "KeyVault-Suffix" --query value -o tsv | tr -d '\r')
    echo "KeyVault-Suffix: $keyvaultSuffix"
fi

echo "Adding certificate AuthProxy-$deviceName-$keyvaultSuffix to App Registration $clientId"

if $appendAppCredentials
then
   echo "Appending App Credentials"
   az ad app credential reset --id $clientId --cert "AuthProxy-$deviceName-$keyvaultSuffix" --keyvault $keyVaultName --append
else
   echo "Resetting App Credentials"
   az ad app credential reset --id $clientId --cert "AuthProxy-$deviceName-$keyvaultSuffix" --keyvault $keyVaultName
fi
