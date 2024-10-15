#!/bin/bash

# Deploys infrastructure
# This script needs environment variables already loaded in order to run

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Load utils lib
. "$SCRIPT_DIR"/utils.sh

function usage {
    echo ""
    echo "Deploys Azure resources."
    echo ""
    echo "  -a | --action str         Action to perform: plan, apply or output (Optional, default is 'apply')"
    echo "  -o | --output-name str    Variable's value to output. (Optional, if present, --action must be output. If not present, all outputs re returned)"
    echo "  -s | --source str         Deployment source. (Optional, the value will be used to tag the resource group and to name the OpenTofu state file)"
    echo "  -l | --location str       Location to deploy. (Optional, will use the default value set in environment variables or in OpenTofu configuration)"
    echo "  --enable-vnet             To deploy behind a VNET or not. (Optional, default is false)"
    echo "  -v | --extra-var str=str  Extra var for the opentofu commands (ex. 'var1=value'). (Optional, can be used multiple times)"
    echo "  --skip-tests              Skip the test execution. (Optional, default is false)"
    echo "  --peer-pipeline           Specifies whether the infrastructure should be paired with the virtual network of the pipeline"
    echo "  -h | --help               Display this message."
    echo ""
    echo "ex: "
    echo "   $0 --action apply -s test --location westus --skip-tests --peer-pipeline"
    echo "   $0 --action output - --output-name keyvault_name"
    echo "   $0 --action apply -s main --extra-var ml_sa_account_kind=Storage "
    echo ""
}

function run_test() {
    pushd "$SCRIPT_DIR/../infrastructure/main/test"

    go mod tidy

    printMessage "Starting test execution"

    go test -timeout 30m end2end_test.go

    exitCode=$?

    # Check the exit status
    if [[ ${exitCode} -eq 0 ]]; then
        printMessage "OpenTofu tests passed."
    else
        printError "OpenTofu tests failed."
        exit 1
    fi

    popd
}

function init_opentofu() {
    printMessage "Initializing OpentTofu configuration"

    echo TF_VAR_resource_group_name=$TF_VAR_resource_group_name
    echo TF_VAR_storage_account_name=$TF_VAR_storage_account_name
    echo TF_VAR_container_name=$TF_VAR_container_name

    tofu init \
        -backend-config="resource_group_name=$TF_VAR_resource_group_name" \
        -backend-config="storage_account_name=$TF_VAR_storage_account_name" \
        -backend-config="container_name=$TF_VAR_container_name" \
        -backend-config="key=$tfstate_filename.tfstate"
}

function run_opentofu() {
    # Run OpenTofu Config
    pushd "$SCRIPT_DIR/../infrastructure/main"

    printMessage "Starting the execution of the OpenTofu configuration"
    tofu fmt

    init_opentofu

    tofu validate

    if [[ "$action" == "output" ]]; then
        if [[ -z ${outputName} ]]; then
            tofu output --raw "$outputName"
        else
            tofu output
        fi
    elif [[ "$action" == "plan" ]]; then
        tofu plan ${tfVars} -input=false
    elif [[ "$action" == "apply" ]]; then
        tofu plan ${tfVars} -input=false
        tofu apply ${tfVars} -input=false -auto-approve
    else
        printError "Invalid action $actionName"
    fi

    popd
}

## MAIN ##
runTests=true
vnetEnabled=false
peerWithPipeline=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -a|--action) action="$2"; shift ;;
        -o|--output-name) outputName="$2"; shift ;;
        -l|--location) loc="$2"; shift ;;
        -s|--source) source="$2"; shift ;;
        --enable-vnet) vnetEnabled=true ;;
        --peer-pipeline) peerWithPipeline=true ;;
        -v|--extra-var) extraVar+=("$2"); shift ;;
        --skip-tests) runTests=false ;;
        -h|--help) help=1 ;;
        *) printError "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

tfVars=" -var vnet_enabled=$vnetEnabled"
tfVars+=" -var peer_with_pipeline=$peerWithPipeline"
# tfVars={$tfVars}" -var resource_group_name=$TF_VAR_resource_group_name"
# tfVars={$tfVars}" -var storage_account_name=$TF_VAR_storage_account_name"
# tfVars={$tfVars}" -var container_name=$TF_VAR_container_name"

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

if [[ -n $source ]]; then
    tfVars+=" -var deployment_source=$source"
    tfstate_filename=$source
fi

if [[ -n $loc ]]; then
    LOCATION=$loc
    tfVars+=" -var location=$LOCATION"
fi

if [[ -n $extraVar ]]; then
    for var in "${extraVar[@]}"; do
        tfVars+=" -var $var"
    done
fi

az_login

if  $runTests ; then
    run_test
else
    printMessage "Skipping test execution.."
fi

run_opentofu
