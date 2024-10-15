#!/bin/bash

# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

echo "Register Device with IoT Hub"

helpFunction()
{
    echo ""
    echo "Usage: $0 -s subscriptionId -k keyVaultName -d deviceName -h iotHubName -x keyvaultSuffix"
    echo -e "\t-s Subscription Id"
    echo -e "\t-k Key Vault Name"
    echo -e "\t-x KeyVault Suffix"
    echo -e "\t-d Device Name"
    echo -e "\t-h IoT Hub Name"
    exit 1 # Exit script after printing help
}

while getopts "s:k:d:h:x:" opt
do
   case "$opt" in
      s ) subscriptionId="$OPTARG" ;;
      k ) keyVaultName="$OPTARG" ;;
      d ) deviceName="$OPTARG" ;;
      x ) keyvaultSuffix="$OPTARG" ;;
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

if [ -z $keyvaultSuffix ]
then
    echo "Retrieving unique KeyVault-Suffix"
    keyvaultSuffix=$(az keyvault secret show --vault-name $keyVaultName --name "KeyVault-Suffix" --query value -o tsv | tr -d '\r')
    echo "KeyVault-Suffix: $keyvaultSuffix"
fi

echo "Setting subscription to $subscriptionId"
az account set --subscription $subscriptionId

certificateName="ModelManager-$deviceName-$keyvaultSuffix"

echo "Retrieving device certificate $certificateName"

az keyvault certificate download --vault-name $keyVaultName -n $certificateName -f cert_$deviceName.crt -e DER

fingerprint=$(openssl x509 -in cert_$deviceName.crt -inform DER -noout -sha1 -fingerprint)

rm cert_$deviceName.crt

thumbprint=$(echo $fingerprint | cut -d"=" -f2)
thumbprint=$(echo $thumbprint | sed "s/://g")

echo $thumbprint

echo "Registering device $deviceName with IoT Hub $iotHubName"

az iot hub device-identity create --hub-name $iotHubName --device-id $deviceName --am x509_thumbprint --ptp "$thumbprint"
