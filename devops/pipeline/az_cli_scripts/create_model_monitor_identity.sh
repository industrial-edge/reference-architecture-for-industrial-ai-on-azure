#!/bin/bash

# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

echo "Create Model Monitor Identity"

helpFunction()
{
    echo ""
    echo "Usage: $0 -s subscriptionId -k keyVaultName -S true/false -r true/false -d deviceName -c clientId -t tenantId -a true/false -b buildNumber"
    echo -e "\t-s Subscription Id"
    echo -e "\t-k Key Vault Name"
    echo -e "\t-d Device Name"
    echo -e "\t-S Self Signed Certificate (true/false)"
    echo -e "\t-c Client Id"
    echo -e "\t-t Tenant Id"
    echo -e "\t-a Append App Credentials (true/false)"
    echo -e "\t-b Build Number"
    exit 1 # Exit script after printing help
}

while getopts "s:k:d:S:c:t:a:b:" opt
do
   case "$opt" in
      s ) subscriptionId="$OPTARG" ;;
      k ) keyVaultName="$OPTARG" ;;
      d ) deviceName="$OPTARG" ;;
      S) selfSigned="$OPTARG" ;;
      c) clientId="$OPTARG" ;;
      t) tenantId="$OPTARG" ;;
      a) appendAppCredentials="$OPTARG" ;;
      b) buildNumber="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$subscriptionId" ] || [ -z "$keyVaultName" ] || [ -z "$deviceName" ] || [ -z "$tenantId" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

if [ -z "$selfSigned" ]
then
    selfSigned=false
fi

if [ -z "$appendAppCredentials" ]
then
    appendAppCredentials=false
fi

if [ -z "$buildNumber" ]
then
    buildNumber=$(whoami)-$(hostname)-$(date -Iseconds)
fi

echo "Setting subscription to $subscriptionId"
az account set --subscription $subscriptionId

echo "Retrieving unique KeyVault-Suffix"
keyvaultSuffix=$(az keyvault secret show --vault-name $keyVaultName --name "KeyVault-Suffix" --query value -o tsv | tr -d '\r')
echo "keyvaultSuffix: $keyvaultSuffix"

# Create the certificate in KeyVault
./create_keyvault_certificate.sh -s $subscriptionId -k $keyVaultName -d $deviceName -S $selfSigned -x $keyvaultSuffix -b $buildNumber -c "AuthProxy"

if [ -z "$clientId" ]
then
   ./create_app_registration.sh -s $subscriptionId -d $deviceName -b $buildNumber
   clientId=$(cat "Model-Monitor-$deviceName-ObjectId.txt")
   echo $clientId
   rm "Model-Monitor-$deviceName-ObjectId.txt"
fi

./add_certificate_to_app_registration.sh -s $subscriptionId -k $keyVaultName -d $deviceName -x $keyvaultSuffix -c $clientId

./assign_monitoring_metrics_publisher_role.sh -s $subscriptionId -c $clientId -x $keyvaultSuffix -k $keyVaultName

./create_model_monitor_config.sh -s $subscriptionId -k $keyVaultName -d $deviceName -x $keyvaultSuffix -c $clientId -t $tenantId -b $buildNumber
