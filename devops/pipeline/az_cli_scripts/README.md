<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# README

This document explains the scripts and templates found in this folder. They support two processes, the Create Model Monitor Identity and Create Model Manager Workspace Identity processes.


## Create Model Monitor Identity

### create_model_monitor_identity.sh

The script `create_model_monitor_identity.sh` is the top level script for creating a new Model Monitor Identity. It has the following command line options:

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| -s subscriptionId | Y | - | The Azure Subscription the resources can be found in |
| -k keyVaultName | Y | - | The name of KeyVault used to create/store certificates and secrets |
| - d deviceName | Y | - | Name of the Model Monitor Device being registered|
| -t tenantId | Y | - | AAD Tenant the Service Principal will be created in |
| -c clientId | N | - | ClientId of an existing Service Principal to use |
| -S (true/false) | N | false | Use Self-Signed certificates. Currently CA based certs are not implemented |
| -b buildNumber | N | "{username}-{hostname}-{datetime}" | Provided by the ADO pipeline run to provide traceability |
| -a (true/false) | N | false | Determines whether the new credentials should be appended to the existing set (see scenarios below) |

#### Scenarios

This script supports three major scenarios

##### New Service Principal

This is the simplest case and for each identity being created, a new Service Principal is created in the AAD tenant. This is NOT the scenario to use in the Siemens tenant where generation of Service Principals like this is not allowed.

| Option | Value | Explanation |
|--------|-------|--------------|
| -c | {none} | Do not use this flag, a new Service Principal will be generated |
| -a | false | Do not append credentials. Not really an issue as the credential list is empty upon creation |


##### Use Existing Service Principal - single identity

To be used when the Service Principals for the Identities are created in a separate process, but it is still a 1-1 mapping from Model Manager Identity to Service Principal.

| Option | Value | Explanation |
|--------|-------|--------------|
| -c | {clientId} | Finds and uses the Service Principal with this ClientId |
| -a | false | Do not append credentials. Not really an issue as the credential list is empty upon creation |

##### Use Existing Service Principal - multiple identities

To be used when there is only a single Service Principal representing multiple Model Monitor Identities. This is the default Siemens tenant case.

| Option | Value | Explanation |
|--------|-------|--------------|
| -c | {clientId} | Finds and uses the Service Principal with this ClientId |
| -a | true | Appends the newly created certificate/credential to the list already on the service principal. |

### Execution flow

The script runs the following scripts in order:

- `create_keyvault_certificate.sh`
- `create_app_registration.sh` if and only if the `clientId` option is empty
- `add_certificate_to_app_registration.sh`
- `assign_monitoring_metrics_publisher_role.sh`
- `create_model_monitor_config.sh`

### add_certificate_to_app_registration.sh

Adds a certificate from KeyVault to the list of certificates on the app registration/service principal.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| -s subscriptionId | Y | - | The Azure Subscription the resources can be found in |
| -k keyVaultName | Y | - | The name of KeyVault used to create/store certificates and secrets |
| - d deviceName | Y | - | Name of the Model Monitor Device being registered|
| -t tenantId | Y | - | AAD Tenant the Service Principal will be created in |
| -c clientId | N | - | ClientId of an existing Service Principal to use |
| -a (true/false) | N | false | Determines whether the new credentials should be appended to the existing set (see scenarios below) |
| -x keyVault Suffix | N | Looked up in KeyVault | The unique suffixed used in KeyVault |

Depending on the value of the `-a` flag, it either adds the certificate called `AuthProxy-$deviceName-$keyvaultSuffix` from the KeyVault to the list of certificates on the app registration given by clientId, or deletes the existing ones and then adds the new one.

### assign_monitoring_metrics_publisher_role.sh

Assigned the Monitoring Metrics Publisher role to a service principal.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| -s subscriptionId | Y | - | The Azure Subscription the resources can be found in |
| -k keyVaultName | Y | - | The name of KeyVault used to create/store certificates and secrets |
| - d deviceName | Y | - | Name of the Model Monitor Device being registered|
| -c clientId | N | - | ClientId of an existing Service Principal to use |
| -x keyVault Suffix | N | Looked up in KeyVault | the unique suffixed used in KeyVault |

Find the service principal representing the app registration given by `clientId`. It then finds the Application Insights instance based on the `AppInsights-ConnectionString-$keyvaultSuffix` secret in KeyVault and assigned the role to the service principal. It finds the resource group of the App Insights (required for the assignment call) by querying the App Insights API.

### create_app_registration.sh

Creates a new App Registration and associated service principal. The main `create_model_monitor_identity.sh` only calls this if the top level `-c clientId` value is empty.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| -s subscriptionId | Y | - | The Azure Subscription the resources can be found in |
| - d deviceName | Y | - | Name of the Model Monitor Device being registered|

Creates the service principal - which also creates a new app registration - in the tenant that owns the `-s subscriptionId` subscription.

The appId of the newly created service principal is written to a temporary file called `Model-Monitor-$deviceName-ObjectId.txt`. This is picked up by `create_model_monitor_identity.sh`, written to the `clientId` variable and the file is deleted.

### create_keyvault_certificate.sh

Creates a new certificate in KeyVault. Currently ONLY works with Self Signed certs (`-S true`). CA based certs can be added later.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| -s subscriptionId | Y | - | The Azure Subscription the resources can be found in |
| -k keyVaultName | Y | - | The name of KeyVault used to create/store certificates and secrets |
| - d deviceName | Y | - | Name of the Model Monitor Device being registered|
| -S (true/false) | N | false | Use Self-Signed certificates. Currently CA based certs are not implemented |
| -x keyVault Suffix | N | Looked up in KeyVault | The unique suffixed used in KeyVault |
| - d deviceName | Y | - | Name of the Model Monitor Device being registered|
| -c Certificate Prefix | Y - | Prefix used on the certificate name, e.g. Model_Manager or Model_Monitor |

Creates a new self-signed certificate using the `create_model_monitor_certificate_policy.json` as the policy template. The template contains a subject field of ` "subject": "CN={DEVICE_NAME}",` the script substitutes the `-d deviceName` value in so you end up with the name of the device being the subject of the certificate.

### create_model_monitor_config.sh

Creates the Json configuration block to be downloaded to the factory and used to configure AI Model Monitor.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| -s subscriptionId | Y | - | The Azure Subscription the resources can be found in |
| -k keyVaultName | Y | - | The name of KeyVault used to create/store certificates and secrets |
| - d deviceName | Y | - | Name of the Model Monitor Device being registered|
| -t tenantId | Y | - | AAD Tenant the Service Principal will be created in |
| -c clientId | N | - | ClientId of an existing Service Principal to use |
| -b buildNumber | N | "local" | Provided by the ADO pipeline run to provide trackability |
| -x keyVault Suffix | N | Looked up in KeyVault | The unique suffixed used in KeyVault |

Looks up a number of secrets from KeyVault then uses the `model_monitor_config.json` template to build a Json string that is stored back in KeyVault as the `Model-Monitor-$deviceName-Configuration-$keyvaultSuffix` secret.

## Create Model Manager Identity

### create_model_manager_identity.sh

The script create_model_manager_identity.sh is the top level script for creating a new Model Manager workspace identity. It has the following command line options:


| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| -s subscriptionId | Y | - | The Azure Subscription the resources can be found in |
| -k keyVaultName | Y | - | The name of KeyVault used to create/store certificates and secrets |
| -d deviceName | Y | - | Name of the Model Monitor Device being registered|
| -S (true/false) | N | false | Use Self-Signed certificates. Currently CA based certs are not implemented |
| -b buildNumber | N | "{username}-{hostname}-{datetime}" | Provided by the ADO pipeline run to provide traceability |
| -h IoT Hub Name | Y | - | Name of the IOT Hub to register the device on |
| -r CA Root to use [G2 or CA] | Y | - | Which DigiCert root certificate to use. CA to be used only in China. |

### Execution flow

The script runs the following scripts in order

- `create_keyvault_certificate.sh`
- `register_device_with_iot_hub.sh`
- `create_model_manager_config.sh`

### register_device_with_iot_hub.sh

Creates a device registration on the specified IoT Hub for the named device.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| -s subscriptionId | Y | - | The Azure Subscription the resources can be found in |
| -k keyVaultName | Y | - | The name of KeyVault used to create/store certificates and secrets |
| -d deviceName | Y | - | Name of the Model Monitor Device being registered|
| -h IoT Hub Name | Y | - | Name of the IOT Hub to register the device on |
| -x keyVault Suffix | N	| Looked up in KeyVault	| The unique suffixed used in KeyVault |

### create_model_manager_config.sh

Creates the device specific configuration data and stores it as a secret.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| -s subscriptionId | Y | - | The Azure Subscription the resources can be found in |
| -k keyVaultName | Y | - | The name of KeyVault used to create/store certificates and secrets |
| -d deviceName | Y | - | Name of the Model Monitor Device being registered|
| -b buildNumber | N | "{username}-{hostname}-{datetime}" | Provided by the ADO pipeline run to provide traceability |
| -h IoT Hub Name | Y | - | Name of the IOT Hub to register the device on |
| -r CA Root to use [G2 or CA] | Y | - | Which DigiCert root certificate to use. CA to be used only in China. |
| -x keyVault Suffix | N	| Looked up in KeyVault	| The unique suffixed used in KeyVault |

The -r option determines which DigiCert root certificate to include in the configuration, this should be `G2` in more cases, only use `CA` for China.

The secret is store with name `Model-Manager-$deviceName-Configuration-$keyvaultSuffix`.
