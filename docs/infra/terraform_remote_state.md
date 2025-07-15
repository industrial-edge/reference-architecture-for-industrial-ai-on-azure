<!--
SPDX-FileCopyrightText: 2025 Siemens AG

SPDX-License-Identifier: MIT
-->

### 1. Creating the terraform remote state
Open a bash terminal and run the following bash script located under the scripts folder to create the terraform remote state.
This script creates a storage account inside a newly created resource group called tfstate.
It uses an environment variable (ARM_ACCESS_KEY) to store the storage access key (using an environment variable prevents the key from being written to disk)

```sh
azure-enablement/scripts/> ./terraform-remote-state.sh
``` 
Upon successful completion the resource names required for configuring the Terraform backend state are displayed:
- resource group name: the name of the resource group containing the storage account
- storage account name: the name of the storage account
- container name: the name e storage container within the storage account

### 2. Configure the Terraform backend state
In order to configure the Terraform backed state the following information is needed:
- resource group name (required): the name of the resource group containing the storage account
- storage account name(required): the name of the storage account
- container name(required): the name of the storage container within the storage account
- key(required): the name of the blob used  to retrieve the Terraform's state file inside the storage container 

Open the backend.tf file in the common folder, under infrastructure folder, and add the above resource names (as displayed when running the script from section 1 above)
For example:

```sh
terraform {
  backend "azurerm" {
    resource_group_name = "tfstatedev"
    storage_account_name = "tfstate3215"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}
```
Open the terminal and run the terraform init command

```sh
terraform init
```

Alternative option
Alternatively, a partial configuration can be used
Another option would be to add a new file backend.conf (can also be added to .gitignore) under the common folder (same location as the provider.tf file) with the following contents.
For example, backend.conf file might look like

```sh
resource_group_name  = "tfstatedev"
storage_account_name = "tfstate3215"
container_name       = "tfstate"
```

In the backend.tf file keep only the key name and remove the rest
```sh
terraform {
  backend "azurerm" {
    key = "terraform.tfstate"
  }
}
```

From the terminal run terraform init with the newly defined backend configuration

```sh
infrastructure\common> terraform init -backend-config="backend.conf"
```

### Side node
The script can also take 2 optional parameters, if no optional parameters are provided default values are used
For example

```sh
azure-enablement/scripts/>  ./terraform-remote-state.sh -e "local" -l "westus"
``` 
will create a resource group with name RESOURCE_GROUP="tfstatelocal" located in westup (LOCATION=westus"")