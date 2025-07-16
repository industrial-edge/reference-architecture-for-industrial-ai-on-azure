#!/bin/bash

# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

echo "Create Model Manager Configuration"

helpFunction()
{
    echo ""
    echo "Usage: $0 -s subscriptionId -k keyVaultName -d deviceName -b buildNumber -x keyvaultSuffix -h iotHubName -r caRoot"
    echo -e "\t-s Subscription Id"
    echo -e "\t-k Key Vault Name"
    echo -e "\t-d Device Name"
    echo -e "\t-x KeyVault Suffix"
    echo -e "\t-b Build Number"
    echo -e "\t-h IoT Hub Name"
    echo -r "\t-r CA Root to use [G2|CA]"
    exit 1 # Exit script after printing help
}

while getopts "s:k:d:x:b:h:r:" opt
do
   case "$opt" in
      s ) subscriptionId="$OPTARG" ;;
      k ) keyVaultName="$OPTARG" ;;
      d ) deviceName="$OPTARG" ;;
      x ) keyvaultSuffix="$OPTARG" ;;
      b ) buildNumber="$OPTARG" ;;
      h ) iotHubName="$OPTARG" ;;
      r ) caRoot="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

echo $keyVaultName
echo $deviceName
echo $keyvaultSuffix
echo $buildNumber
echo $iotHubName
echo $subscriptionId

# Print helpFunction in case parameters are empty
if [ -z "$subscriptionId" ] || [ -z "$keyVaultName" ] || [ -z "$deviceName" ] || [ -z "$buildNumber" ] || [ -z "$iotHubName" ]
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

if [ -z $caRoot ]
then
   caRoot="G2"
fi

echo "Retrieving device certificate"

az keyvault certificate download --vault-name $keyVaultName -n "ModelManager-$deviceName-$keyvaultSuffix" -f ModelManager-public-key-$deviceName.pem -e PEM
publicCert=$(cat ModelManager-public-key-$deviceName.pem)
rm ModelManager-public-key-$deviceName.pem

echo "Retrieving device private key"

az keyvault secret download --vault-name $keyVaultName -n "ModelManager-$deviceName-$keyvaultSuffix" -f ModelManager-private-key-$deviceName.key
privateKey=$(cat ModelManager-private-key-$deviceName.key)
privateKey=$(echo "$privateKey" | awk '/BEGIN PRIVATE KEY/,/END PRIVATE KEY/' )

rm ModelManager-private-key-$deviceName.key

if [ $caRoot = "G2" ]; then
   echo "Retrieving DigiCert Global Root G2 ceritificate"
   capem=$(curl https://cacerts.digicert.com/DigiCertGlobalRootG2.crt.pem)
elif  [ $caRoot = "CA" ]; then
   echo "Retrieving DigiCert Global Root CA ceritificate"
   capem=$(curl https://cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem)
else
   echo "Unknown CA Root $caRoot"
   exit 1
fi

configuration=$(jq -n \
 --arg capem "$capem" \
 --arg x509_certificate "$publicCert" \
 --arg x509_private_key "$privateKey" \
 --arg build_number "$buildNumber" \
 --arg endpoint "wss://$iotHubName.azure-devices.net:443/\$iothub/websocket" \
 --arg topic_prefix "devices/$deviceName" \
 --arg username "${iotHubName}.azure-devices.net/${deviceName}/?api-version=2021-04-12" \
 --arg client_id "$deviceName" \
 '{ca_cert:$capem, client_id:$client_id, username:$username, topic_prefix:$topic_prefix, endpoint:$endpoint, build_number:$build_number, x509_certificate:$x509_certificate, x509_private_key:$x509_private_key}'
 )

secretName="Model-Manager-$deviceName-Configuration-$keyvaultSuffix"

echo "Writing $secretName back into KeyVault"

az keyvault secret set --vault-name $keyVaultName --name $secretName --value "$configuration"
