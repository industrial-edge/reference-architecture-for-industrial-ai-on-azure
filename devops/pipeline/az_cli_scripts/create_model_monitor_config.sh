#!/bin/bash

# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

echo "Create Model Monitor Configuration"

helpFunction()
{
    echo ""
    echo "Usage: $0 -s subscriptionId -k keyVaultName -d deviceName -b buildNumber -x keyvaultSuffix -c clientId"
    echo -e "\t-s Subscription Id"
    echo -e "\t-k Key Vault Name"
    echo -e "\t-d Device Name"
    echo -e "\t-x KeyVault Suffix"
    echo -e "\t-c Client Id"
    echo -e "\t-t Tenant Id"
    echo -e "\t-b Build Number"
    exit 1 # Exit script after printing help
}

while getopts "s:k:d:c:t:x:b:" opt
do
   case "$opt" in
      s ) subscriptionId="$OPTARG" ;;
      k ) keyVaultName="$OPTARG" ;;
      d ) deviceName="$OPTARG" ;;
      x) keyvaultSuffix="$OPTARG" ;;
      c) clientId="$OPTARG" ;;
      t) tenantId="$OPTARG" ;;
      b) buildNumber="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$subscriptionId" ] || [ -z "$keyVaultName" ] || [ -z "$deviceName" ] || [ -z "$clientId" ] || [ -z "$tenantId" ] || [ -z "$buildNumber" ]
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

echo "Retrieving Application Insights Connection String"
connectionStringKeyName="AppInsights-ConnectionString-$keyvaultSuffix"
applicationInsightsConnectionString=$(az keyvault secret show --vault-name $keyVaultName --name $connectionStringKeyName --query value -o tsv | tr -d '\r')

echo $applicationInsightsConnectionString

instrumentationKey=$(echo $applicationInsightsConnectionString | grep -oP '(?<=InstrumentationKey=)[^;]+')
echo $instrumentationKey

ingestionEndpoint=$(echo $applicationInsightsConnectionString | grep -oP '(?<=IngestionEndpoint=)[^;]+')
echo $ingestionEndpoint

# Need to escape the // in the https:// so it can be substituted into the json using sed
ingestionEndpoint=$(echo $ingestionEndpoint | sed 's/\//\\\//g')

echo "Retrieving device certificate"

az keyvault key download --vault-name $keyVaultName -n "AuthProxy-$deviceName-$keyvaultSuffix" -f AuthProxy-public-key-$deviceName.pem -e PEM
publicCert=$(cat AuthProxy-public-key-$deviceName.pem)
rm AuthProxy-public-key-$deviceName.pem

echo "Retrieving device private key"

az keyvault secret download --vault-name $keyVaultName -n "AuthProxy-$deviceName-$keyvaultSuffix" -f AuthProxy-private-key-$deviceName.key
privateKey=$(cat AuthProxy-private-key-$deviceName.key)
rm AuthProxy-private-key-$deviceName.key

echo "Creating Model Monitor Configuration"

configuration=$(jq -n \
 --arg Certificate "$publicCert" \
 --arg PrivateKey "$privateKey" \
 --arg BuildNumber "$buildNumber" \
 --arg TenantId "$tenantId" \
 --arg ClientId "$clientId" \
 --arg InstrumentationKey "$instrumentationKey" \
 --arg IngestionEndpoint "$ingestionEndpoint" \
   '{Certificate: $Certificate, PrivateKey: $PrivateKey, BuildNumber: $BuildNumber, TenantId: $TenantId, ClientId: $ClientId, InstrumentationKey: $InstrumentationKey, IngestionEndpoint: $IngestionEndpoint}'
 )

secretName="Model-Monitor-$deviceName-Configuration-$keyvaultSuffix"

echo "Writing $secretName back into KeyVault"

az keyvault secret set --vault-name $keyVaultName --name $secretName --value "$configuration"
