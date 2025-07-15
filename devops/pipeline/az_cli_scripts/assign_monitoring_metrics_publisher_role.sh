#!/bin/bash

# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

echo "Assign Monitoring Metrics Publisher Role"

helpFunction()
{
    echo ""
    echo "Usage: $0 -s subscriptionId -c clientId -x keyvault_suffix -k keyVaultName"
    echo -e "\t-s Subscription Id"
    echo -e "\t-k Key Vault Name"
    echo -e "\t-c Client Id"
    echo -e "\t-x KeyVault Suffix"
    exit 1 # Exit script after printing help
}

while getopts "s:c:x:k:" opt
do
   case "$opt" in
      s ) subscriptionId="$OPTARG" ;;
      c) clientId="$OPTARG" ;;
      x) keyvaultSuffix="$OPTARG" ;;
      k ) keyVaultName="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$subscriptionId" ] || [ -z "$clientId" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# We need to use the App Insights module which might not be installed
# So allow it to be installed without prompting
az config set extension.use_dynamic_install=yes_without_prompt

echo "Setting subscription to $subscriptionId"
az account set --subscription $subscriptionId

if [ -z $keyvaultSuffix ]
then
    echo "Retrieving unique KeyVault-Suffix"
    keyvaultSuffix=$(az keyvault secret show --vault-name $keyVaultName --name "KeyVault-Suffix" --query value -o tsv | tr -d '\r')
    echo "KeyVault-Suffix: $keyvaultSuffix"
fi

echo "Find service principal for clientId $clientId"
servicePrincipalId=$(az ad sp list --filter "appId eq '$clientId'" --query "[].id" -o tsv | tr -d '\r')

echo $servicePrincipalId

echo "Retrieving Application Insights Connection String"
connectionStringKeyName="AppInsights-ConnectionString-$keyvaultSuffix"
applicationInsightsConnectionString=$(az keyvault secret show --vault-name $keyVaultName --name $connectionStringKeyName --query value -o tsv | tr -d '\r')
instrumentationKey=$(echo $applicationInsightsConnectionString | grep -oP '(?<=InstrumentationKey=)[^;]+')
echo $instrumentationKey

echo "Finding Application Insights resource"

appInsightsName=$(az monitor app-insights component show --query "[?instrumentationKey=='$instrumentationKey'].[applicationId][0][0]")
appInsightsName=$(echo $appInsightsName | tr -d '"')

echo "Finding the resource group for $appInsightsName"
resourceGroupName=$(az monitor app-insights component show --query "[?instrumentationKey=='$instrumentationKey'].[resourceGroup][0][0]")
resourceGroupName=$(echo $resourceGroupName | tr -d '"')
echo $resourceGroupName

echo "Assigning role Monitoring Metrics Publisher to service principal $servicePrincipalId"

az role assignment create --assignee $servicePrincipalId --role "Monitoring Metrics Publisher" --scope "/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/microsoft.insights/components/$appInsightsName"
