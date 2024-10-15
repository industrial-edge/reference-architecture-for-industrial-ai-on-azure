#!/bin/bash

# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

#
# Deploys pipeline agents
# This script needs environment variables already loaded in order to run

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Load utils lib
. "$SCRIPT_DIR"/utils.sh

function usage {
    echo ""
    echo "Deploys pipeline agents."
    echo ""
    echo "  -a | --action str         Action to perform: plan, apply or output (Optional, default is 'apply')"
    echo "  -o | --output-name str    Variable's value to output. (Optional, if present, --action must be output. If not present, all outputs re returned)"
    echo "  -v | --extra-var str=str  Extra var for the opentofu commands (ex. 'var1=value'). (Optional, can be used multiple times)"
    echo "  -h | --help               Display this message."
    echo ""
    echo "ex: "
    echo "   $0 --action plan"
    echo "   $0 --action output --output-name agent_vnet_name"
    echo "   $0 --extra-var vm_scaleset_sku=Standard --extra-var location=westeurope"
    echo ""
}

function init_opentofu() {
    printMessage "Initializing OpenTofu configuration"

    echo TF_VAR_resource_group_name=$TF_VAR_resource_group_name
    echo TF_VAR_storage_account_name=$TF_VAR_storage_account_name
    echo TF_VAR_container_name=$TF_VAR_container_name

    tofu init \
        -backend-config="tfstate_resource_group_name=$TF_VAR_resource_group_name" \
        -backend-config="tfstate_storage_account_name=$TF_VAR_storage_account_name" \
        -backend-config="tfstate_container_name=$TF_VAR_container_name" \
        -backend-config="key=agents.tfstate"
}

function run_opentofu() {
    # Run OpenTofu Config
    printMessage "Starting the execution of the OpenTofu configuration"
    tofu fmt
    tofu validate

    init_opentofu

    if [[ "$action" == "output" ]]; then
        if [[ -z ${outputName} ]]; then
            tofu output --raw "$outputName"
        else
            tofu output
        fi
    elif [[ "$action" == "plan" ]]; then
        tofu plan ${tfVars} -input=false

    elif [[ "$action" == "apply" ]]; then
        tofu apply ${tfVars} -input=false -auto-approve
    else
        printError "Invalid action $actionName"
    fi
}

## MAIN ##
pushd "$SCRIPT_DIR/../infrastructure/pipeline-agent" > /dev/null

# reset the current directory on exit using a trap so that the directory is reset even on error
function finish {
  popd > /dev/null
}
trap finish EXIT

action="apply"
tfVars=""

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -a|--action) action="$2"; shift ;;
        -o|--output-name) outputName="$2"; shift ;;
        -v|--extra-var) extraVar+=("$2"); shift ;;
        -h|--help) help=1 ;;
        *) printError "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [[ -n "$help" ]]; then
    usage
    exit 2
fi

if [[ -n $action ]]; then
    actionsOpt=("plan" "apply" "output")

    if [[ ! ${actionsOpt[*]} =~ (^|[[:space:]])"$action"($|[[:space:]]) ]]; then
        printError "Invalid action $action"
        usage
        exit 1
    fi
fi

if [[ -n $extraVar ]]; then
    for var in "${extraVar[@]}"; do
        tfVars+=" -var $var"
    done
fi


az_login

run_opentofu
