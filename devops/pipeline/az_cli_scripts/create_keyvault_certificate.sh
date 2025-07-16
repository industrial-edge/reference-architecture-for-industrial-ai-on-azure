#!/bin/bash

# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

echo "Create KeyVault Certificate"

helpFunction()
{
    echo ""
    echo "Usage: $0 -s subscriptionId -k keyVaultName -c certificatePrefix -S true/false -x keyvault_suffix -d deviceName -b buildNumber"
    echo -e "\t-s Subscription Id"
    echo -e "\t-k Key Vault Name"
    echo -e "\t-d Device Name"
    echo -e "\t-S Self Signed Certificate (true/false)"
    echo -e "\t-x KeyVault Suffix"
    echo -e "\t-b Build Number"
    echo -e "\t-c Certificate Prefix"
    exit 1 # Exit script after printing help
}

while getopts "s:k:d:S:x:b:c:" opt
do
   case "$opt" in
      s ) subscriptionId="$OPTARG" ;;
      k ) keyVaultName="$OPTARG" ;;
      d ) deviceName="$OPTARG" ;;
      S) selfSigned="$OPTARG" ;;
      x) keyvaultSuffix="$OPTARG" ;;
      b) buildNumber="$OPTARG" ;;
      c) certificatePrefix="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$subscriptionId" ] || [ -z "$keyVaultName" ] || [ -z "$deviceName" ] || [ -z "$buildNumber" ] || [ -z "$certificatePrefix" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

if [ -z "$selfSigned" ]
then
    selfSigned=false
fi

echo "Setting subscription to $subscriptionId"
az account set --subscription $subscriptionId

if [ -z $keyvaultSuffix ]
then
    echo "Retrieving unique KeyVault-Suffix"
    keyvaultSuffix=$(az keyvault secret show --vault-name $keyVaultName --name "KeyVault-Suffix" --query value -o tsv | tr -d '\r')
    echo "KeyVault-Suffix: $keyvaultSuffix"
fi

certificateName="$certificatePrefix-$deviceName-$keyvaultSuffix"

if $selfSigned
then
    echo "Creating SelfSigned KeyVault Certificate $certificateName in KeyVault $keyVaultName"

    policy=$(cat create_certificate_policy.json | sed "s/{DEVICE_NAME}/$deviceName/g")

    if [ -z "$policy" ]
    then
        echo "Unable to read create_certificate_policy.json"
        exit 1
    fi

    # Create device specific policy file
    echo "$policy" > "create_certificate_policy_$deviceName.json"

    az keyvault certificate create --vault-name $keyVaultName\
        --name $certificateName\
        --policy @create_certificate_policy_$deviceName.json\
        --tags "BuildNumber=$buildNumber"

    #Remove device specific policy file
    rm "create_certificate_policy_$deviceName.json"
else
    echo "Create a CA certificate [TODO]"
fi
