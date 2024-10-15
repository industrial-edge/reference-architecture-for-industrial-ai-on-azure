#!/bin/bash

function printError(){
    echo -e "${RED}$*${NC}"
}

function printWarning(){
    echo -e "${YELLOW}$*${NC}"
}

function printMessage(){
    echo -e "${GREEN}$*${NC}"
}

function az_login() {
    # Check if current process's user is logged on Azure
    # If no, then triggers az login
    if [ -z "$ARM_TENANT_ID" ]; then
        printError "Variable ARM_TENANT_ID not set"
        exit 1
    fi
    if [ -z "$ARM_CLIENT_ID" ]; then
        printError "Variable ARM_CLIENT_ID not set"
        exit 1
    fi
    if [ -z "$ARM_CLIENT_SECRET" ]; then
        printError "Variable ARM_CLIENT_SECRET not set"
        exit 1
    fi

    if [ -z "$ARM_SUBSCRIPTION_ID" ]; then
        printError "Variable ARM_SUBSCRIPTION_ID not set"
        az login --service-principal --username $ARM_CLIENT_ID --password $ARM_CLIENT_SECRET --tenant $ARM_TENANT_ID
        # get Azure Subscription and Tenant Id if already connected
        ARM_SUBSCRIPTION_ID=$(az account show --query id --output tsv 2> /dev/null) || true
    fi
    azOk=true
    az account set -s "$ARM_SUBSCRIPTION_ID" 2>/dev/null || azOk=false
    if [[ ${azOk} == false ]]; then
        printWarning "Need to az login"
       az login --service-principal --username $ARM_CLIENT_ID --password $ARM_CLIENT_SECRET --tenant $ARM_TENANT_ID
    fi

    azOk=true
    az account set -s "$ARM_SUBSCRIPTION_ID"   || azOk=false
    if [[ ${azOk} == false ]]; then
        echo -e "unknown error"
        exit 1
    fi
}
