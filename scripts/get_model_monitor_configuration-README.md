<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# README

## get_model_monitor_configuration.sh

This script is used to retrieve configuration data for the Model Monitor application from KeyVault.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| -t tenantId | Y | - | Id of the Tenant the KeyVault is in |
| -s subscriptionId | Y | - | Id of the Subscription the KeyVault is in |
| -k keyVaultName | Y | - | Name of the KeyVault the configuration data is in |
| -d deviceName | Y | - | Name of the device being configured |
| -c (true/false) | N | false | Whether to use Device Code (true) or interactive (false) login |

The configuration data is written to a file called `Model-Monitor-$deviceName-Configuration.json` where $keyvaultSuffix is read from KeyVault.


