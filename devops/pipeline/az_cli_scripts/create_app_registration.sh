#!/bin/bash

echo "Create App Registration"

helpFunction()
{
    echo ""
    echo "Usage: $0 -s subscriptionId -d deviceName -b buildNumber"
    echo -e "\t-s Subscription Id"
    echo -e "\t-d Device Name"
    echo -e "\t-b Build Number"
    exit 1 # Exit script after printing help
}

while getopts "s:d:b:" opt
do
   case "$opt" in
      s ) subscriptionId="$OPTARG" ;;
      d ) deviceName="$OPTARG" ;;
      b) buildNumber="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$subscriptionId" ] || [ -z "$deviceName" ] || [ -z "$buildNumber" ]
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

echo "Creating Service Principal for Model-Monitor-$deviceName"
servicePrincipal=$(az ad sp create-for-rbac --name "Model-Monitor-$deviceName")
objectId=$(echo $servicePrincipal | jq -r ".appId")
echo $objectId > "Model-Monitor-$deviceName-ObjectId.txt"

# Add a tag with the build number
az ad sp update --id $objectId --set tags='["BuilderNumer='$buildNumber'"]'
