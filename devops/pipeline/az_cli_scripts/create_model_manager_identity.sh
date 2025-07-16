#!/bin/bash

# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

echo "Create Model Manager Identity"

helpFunction()
{
    echo ""
    echo "Usage: $0 -s subscriptionId -k keyVaultName -S true/false -d deviceName -h iotHubName -b buildNumber -r caRoot"
    echo -e "\t-s Subscription Id"
    echo -e "\t-k Key Vault Name"
    echo -e "\t-d Device Name"
    echo -e "\t-S Self Signed Certificate (true/false)"
    echo -e "\t-h IoT Hub Name"
    echo -e "\t-b Build Number"
    echo -e "\t-r CA Root to use [G2|CA]"
    exit 1 # Exit script after printing help
}

while getopts "s:k:d:S:b:h:r:" opt
do
   case "$opt" in
      s ) subscriptionId="$OPTARG" ;;
      k ) keyVaultName="$OPTARG" ;;
      d ) deviceName="$OPTARG" ;;
      S) selfSigned="$OPTARG" ;;
      c ) clientId="$OPTARG" ;;
      b ) buildNumber="$OPTARG" ;;
      r ) caRoot="$OPTARG" ;;
      h ) iotHubName="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$subscriptionId" ] || [ -z "$keyVaultName" ] || [ -z "$deviceName" ] || [ -z "$iotHubName" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

if [ -z "$selfSigned" ]
then
    selfSigned=false
fi

if [ -z "$buildNumber" ]
then
    buildNumber=$(whoami)-$(hostname)-$(date -Iseconds)
fi

echo "Setting subscription to $subscriptionId"
az account set --subscription $subscriptionId

echo "Retrieving unique KeyVault-Suffix from $keyVaultName"
keyvaultSuffix=$(az keyvault secret show --vault-name $keyVaultName --name "KeyVault-Suffix" --query value -o tsv | tr -d '\r')
echo "keyvaultSuffix: $keyvaultSuffix"

# Create the certificate in KeyVault
./create_keyvault_certificate.sh -s $subscriptionId -k $keyVaultName -d $deviceName -S $selfSigned -x $keyvaultSuffix -b $buildNumber  -c "ModelManager"

./register_device_with_iot_hub.sh -s $subscriptionId -k $keyVaultName -d $deviceName -x $keyvaultSuffix -h $iotHubName

./create_model_manager_config.sh  -s $subscriptionId -k $keyVaultName -d $deviceName -x $keyvaultSuffix -b $buildNumber -h $iotHubName -r $caRoot
