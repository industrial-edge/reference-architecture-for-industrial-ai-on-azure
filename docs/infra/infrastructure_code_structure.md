<!--
SPDX-FileCopyrightText: 2025 Siemens AG

SPDX-License-Identifier: MIT
-->

# Infrastructure code structure

## Introduction
The document describes how the Terraform code is structured in the solution, it describes the existing modules and how the solution has been extended
to include the network resources.

## Overview
The infrastructure code is organised into multiple folders/modules. As the number of resources increase, it may become complex to manage and maintain the entire configuration as part of one single .tf file.
Grouping the resources dedicated to one task into their own module can help with managing the complexity.

```text
infrastructure
|__ shared
        |__ main.tf
            * Key Vault
            * Application Insights (workspace-based)
            * Log Analytics Workspace
            ...
|__ mlops
        |__ main.tf
            * Machine Learning Workspace
            * Storage Account
            * Container Registry
            * Compute Cluster
            ...
|__ iot_management
        |__ main.tf
            * IoT Hub (with default EventHub endpoint)
            ...
|__ main

|__ common

|__ network


```

* The shared module contains resources referenced by two or more modules.
* The mlops module contains all the resources needed to deploy the Azure Machine Learning Workspace.
* The main module is the root module (the primary entry point that contains the Terraform files), that calls all the other child modules.
* The common module is intended to be referenced/called from other child modules (it is not a module that can independently deployed, therefore it does not define a provider); at the moment it is used to facilitate a consistent format and style for resource naming but it can also be extended with resource "templates" (for example, if the requirement to have multiple function apps would arrise, instead of having multiple azurerm_linux_function_app across modules, this can reside in the common module and reused, ensuring consistency).  
* The Logs and Metric solution uses the Application Insights instance, the Log Analytics Workspace instance and the Key Vault instance (for certificate and secret management) that are deployed part of the shared module

Some remarks:
* The workspace-based Application Insights is intended to be shared by all PaaS resources that need to gather their specific telemetry.
Any resource part of a child module that needs to reference the Application Insights instance or any of its properties can achieve this by using an input variable
(e.g the Machine Learning Workspace needs to reference the Application Insights created as part of the shared module, and this is achieved by passing the value of the Application Insights ID as an input variable )

```text
main/main.tf

module "shared" {
  source                    = "../shared"
  ...
}

module "ml" {
  source                            = "../mlops"
  ...
  appinsights_id                    = module.shared.app_insights_id
  ...  
}

mlops/main.tf
resource "azurerm_machine_learning_workspace" "ml" {
  name                          = module.common.ml_workspace_name
  ...
  application_insights_id       = var.appinsights_id
  ...
}
```
* The Key Vault is also part of the shared module and referenced by resources in multiple child modules (e.g key vault secrets are required to be created in many of the child modules, and in order to achive this the key vault id is being passed as an input variable)

```text
main/main.tf
module "shared" {
  source                    = "../shared"
  ...
}

module "ml" {
  source                            = "../mlops"
  ...
  kv_id                             = module.shared.key_vault_id
  ...
}
```

* When working with modules, the Terraform configuration changes from a flat to a hierarchical one: each module contains its own set of resources,
and possibly its own child modules, which can potentially create a deep, complex tree of resource configurations.
The intention is to keep the module tree as FLAT as possible, with only one level of child modules if possible.

## Network Security with VNETs

The infrastructure has been extended with the resources needed to enable the isolation and communication of exiting resouces inside a Virtual Network. This has been achieved by introducing a new network module as well as network specific resources for each of the existing modules, resources that reside in the network.tf files inside of each of the existing modules that need to be part of the virtual network.

```text
infrastructure
|__ network
        |__ main.tf
        ...
|__ shared
        |__ main.tf
        |__ network.tf
        ...  
|__ mlops
        |__ main.tf
        |__ network.tf
        ...
|__ iot_management
        |__ main.tf
        |__ network.tf
        ...  
|__ pipeline-agent
        |__ main.tf
        |__ network.tf  
        ...
|__ main
        |__ main.tf  
        ...
|__ common

```

### The network module
The network module deploys the virtual network that all the resources from the other modules (mlops, shared, iot_management) are part of.
The aim of this module is to organize the resources into a virtual network, create a segmentation/logical division of the network using subnets, implement a customisable IP addressing schema, create the private DNS records for the virtual network.
```
infrastructure
|__ network
        |__ main.tf
          * Virtual Network
          * Subnet
          * Private DNS Zones
          * Private DNS Zones Network Links
```

The virtual network address space is customisable using the variable ```vnet_address_space```.

The subnet address space is customisable using the variable ```integration_subnet_address_space```.

* the IP address space is specific to each organisation, choose an address space that should not already be in use, can't redefine the IP address space for a network after it is created
* to create a virtual network, at least one subnet needs to be defined, a subnet contains a range of IP addresses that fall within the virtual network address space, the range of one subnet can't overlap with the range of another

Azure Private DNS is used to resolve domain names in the virtual network. Terraform's ```azurerm_private_dns_zone``` is used to create Private DNS zones within Azure DNS and these zones are hosted on Azure's name server (basically servers that provide name resolution for DNS domains hosted in Azure). Once the private DNS zone is created it is linked to the virtual network using the ```azurerm_private_dns_zone_virtual_network_link``` resource.

Because these private DNS zones are used with private endpoints (these are defined in the network.tf of each module), the name of the Private DNS Zone must follow the name schema in the [product documentation](https://learn.microsoft.com/en-gb/azure/private-link/private-endpoint-dns#azure-services-dns-zone-configuration) in order for the two resources (private endpoint and private DNS zone) to be connected successfully. This is because Azure PaaS services already have a DNS configuration for a public endpoint and this configuration must be overridden  to connect using the private endpoint

|Private link resource type|Subresource|Private DNS zone name|
|--------------|--------------|---------------|
|Storage account|blob|privatelink.blob.core.windows.net|
|Azure Machine Learning|amlworkspace|privatelink.api.azureml.ms|
|Azure Container Registry|registry|privatelink.azurecr.io|
|Azure Key Vault |vault|privatelink.vaultcore.azure.net|
|Azure IoT Hub|iotHub|privatelink.azure-devices.net|
|Azure Event Hubs|namespace|privatelink.servicebus.windows.net|

### Network related resources for the shared, mlops and iot_management modules
The network related resources for the shared, mlops and iot_management modules are located in the network.tf file of each module.
This is where the private endpoints for each of the resources is defined.
A private endpoint is a network interface that uses a private IP address from the virtual network, this is how the resource/ PaaS service is brought into the virtual network. In other words, a private endpoint is a network interface that creates a private connection between the virtual network and a resource.
The resource/PaaS service is no longer accessed using a public IP address, but using a private IP address that is assigned to the resource from the address space of the subnet. Any traffic to an from the resource entirely bypasses the public internet, the connection uses the Microsoft Azure backbone network instead.

```text
infrastructure
|__ shared
        |__ network.tf
          * Private endpoint for Key Vault
          * Private endpoint for Azure Monitor
        ...  
|__ mlops
        |__ network.tf
          * Private endpoint for Blob Storage
          * Private endpoint for Container Registry
          * Private endpoint for Machine Learning Workspace
        ...
|__ iot_management
        |__ network.tf
          * Private endpoint for IoT Hub
          ...
```

Notes for Azure Monitor:
The private endpoint set-up for Azure Monitor differs in some respects from the other resources in this project.
This is because Azure Monitor is a collection of different interconnected services that work together.
Instead of having a private endpoint for each resource under the Azure Monitor collection (Application Insights, Log Analytics Workspace etc.),
the resources that need to be part of the virtual network are first linked to a Azure Monitor Private Link Scope resource, and then the private
endpoint is created for the AMPLS resource.
In other words, instead of creating multiple private endpoints, one for each resource, Azure Monitor uses a single private endpoint, from the virtual network to an AMPLS.


```text
Virtual Network --- Private Endpoint --- AMPLS --- Application Insights
                                               --- Log Analytics Workspace  
```

### The main module
The main module is the root module (the primary entry point) that calls all the other child modules.
The main module has been extended to allow the deployment of resources under a virtual network.
The vnet module is instantiated by the main module and outputs information required in the shared, mlops and iot_management modules:
 * the ID of the virtual network
 * the ID of the subnet
 * the IDs of the Private DNS Zones

 These output variables of the network module are passed in as input variables to the child modules (shared, mlops and iot_management modules), and their values are used to create the private endpoints specific to each resources in the child modules.
 Passing the output variable of one module as an input variable to another module creates an implicit dependencies between the respurces in the modules (dependencies are inferred ad resurces are created and destroyed in the right order):

```text
### Virtual Network ###
module "vnet" {
  source                           = "../network"
  vnet_enabled                     = var.vnet_enabled
  vnet_address_space               = var.vnet_address_space
  integration_subnet_address_space = var.integration_subnet_address_space
  ...
}

### Shared Resources ###
module "shared" {
  source                                       = "../shared"
  vnet_enabled                                 = var.vnet_enabled
  vnet_id                                      = module.vnet.vnet_id
  integration_subnet_id                        = module.vnet.integration_subnet_id
  kv_private_dns_zone_id                       = module.vnet.kv_private_dns_zone_id
}

### MLOps Resources ###
module "ml" {
  source                            = "../mlops"
  vnet_enabled                      = var.vnet_enabled
  vnet_id                           = module.vnet.vnet_id
  vnet_name                         = module.vnet.vnet_name
  integration_subnet_id             = module.vnet.integration_subnet_id
  private_dns_zone_id_stg_blob      = module.vnet.private_dns_zone_id_stgacc_blob
  cr_private_dns_zone_id            = module.vnet.cr_private_dns_zone_id
  ml_private_dns_zone_id            = module.vnet.ml_private_dns_zone_id
  ...
}

### IoT Management Resources ###
module "iotmngmt" {
  source                                      = "../iot_management"
  vnet_enabled                                = var.vnet_enabled
  vnet_id                                     = module.vnet.vnet_id
  integration_subnet_id                       = module.vnet.integration_subnet_id
  iothub_private_dns_zone_id                  = module.vnet.iothub_private_dns_zone_id
  ...
}
```

One can choose to deploy the resources with or without the virtual network. This is achieved throught the ```vnet_enabled``` variable (set by default to true) located in variables.tf file of the main module and passed as an input variable in all the other modules.

This is achieved by using the ```count``` Terraform meta-argument.
If a resource includes a ```count``` block  whose value is a whole number, Terraform will create that many instances of the resource.
It also accepts numeric [expressions](https://developer.hashicorp.com/terraform/language/expressions), but it is worth mentioning that the count value
must be known before Terraform performs any remote resource actions, in other words it cannot  refer to any resource attributes that aren't known untill after the configuration is applied (i.e can't use a ID of a resource that is known only after the resource is created, but can use an input variable)


In this implementation, all network resources (all the ones in the network module, plus those defined in the network.tf file of shared, mlops and iot_management modules) use the ```count``` meta-argument with a conditional expression (```<CONDITION> ? <TRUE VAL> : <FALSE VAL>```)

```text
count = var.vnet_enabled ? 1 : 0
```

For example, the virtual network will only be created if ```vnet_enabled = true```
```
resource "azurerm_virtual_network" "vnet" {
  count               = var.vnet_enabled ? 1 : 0
  ...
}
```

More often than not, once one or multiple instances are created via ```count```, a way of referring to a resource instance is needed.
Instances are identified by an index number, starting with 0: ```<TYPE>.<NAME>[<INDEX>] or module.<NAME>[<INDEX>]```
(for example azurerm_subnet.integration_subne[0] refers to an individual instance).

For example, in the network module, the integration subnet needs to reference the virtual network instance
```text
resource "azurerm_virtual_network" "vnet" {
  count               = var.vnet_enabled ? 1 : 0
  ...
}

resource "azurerm_subnet" "integration_subnet" {
  count                = var.vnet_enabled ? 1 : 0
  virtual_network_name = azurerm_virtual_network.vnet[0].name
  ...
}
```

## Module dependency and order of deployment

In the main.tf of the main module one can notice the usage of ```depends_on```, used to create an explicit dependency between some of the modules.

```
### Shared Resources ###
module "shared" {
  source                                       = "../shared"
  ...
}

### MLOps Resources ###
module "ml" {
  source                            = "../mlops"
  depends_on                        = [module.shared]
  ...
}

### IoT Management Resources ###
module "iotmngmt" {
  source                                      = "../iot_management"
  depends_on                                  = [module.shared]
}
```

Also, in the main.tf of the shared module one can notice the usage of ```depends_on``` to create explicit dependencies between resources.

```
resource "azurerm_key_vault_secret" "ai_connstring_secret" {
  ...
  depends_on = [ azurerm_key_vault_access_policy.current]
}

resource "azurerm_key_vault_secret" "ai_appid_secret" {
  ...
  depends_on = [ azurerm_key_vault_access_policy.current]
}

resource "azurerm_key_vault_secret" "kv_suffix_secret" {
  ...
  depends_on = [ azurerm_key_vault_access_policy.current]
}
```


```depends_on``` is a meta-argument  used to handle hidden resource or module dependencies that Terraform cannot infer automatically (can be used in ```module``` blocks and in ```resource``` blocks, regardless of resource type).
* most resources don't have any relationship, and Terraform can make changes to several unrelated resources in parallel.
* some resources must be processed after others, and in this case most dependencies are automatically implied by Terraform using expression references.
* some dependencies cannot be recognised implicitly, and in these rare cases ```depends-on``` can explicitly specify a dependency between otherwise independent resources or modules.

In this configuration there needs to be an explicit dependency between the ```shared``` module and the ```mlops``` module, as well as between the ```shared``` module and the ```iot_management``` module.
This explicit dependency is required due to the change from using an inline key vault access policy to multiple standalone ones.

As the [Terraform documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault_access_policy.html)  explains it is possible to define Key Vault Access Policies:
* within the azure_key_vault resource inside the access_policy block
* using the azurerm_key_vault_access_policy resouce  

However, it is NOT possible to use both methods to manage access policies within Key Vault as it will cause conflicts.

If Terraform must manage access control policies and take actions that require those policies to be present, there is a hidden dependency between the access policy and a resource whose creation depends on it: the Key Vault access policy that grants the current service principal permissions
to handle secrets in Key Vault must be created before any Key Vault secrets are created:
* the ```azurerm_key_vault_access_policy``` with name ```current``` defined in the ```shared``` module must be created before any of the Key Vault Secrets defined in the ```mlops``` module
* the ```azurerm_key_vault_access_policy``` with name ```current``` defined in the ```shared``` module must be created before any of the Key Vault Secrets defined in the ```iot_management``` module
* the ```azurerm_key_vault_access_policy``` with name ```current``` defined in the ```shared``` module must be created before any of the Key Vault Secrets part of the same ```shared``` module

Without the explicit dependencies, there is no guarantee when it comes to the order of resource creation, which will lead to intermittent errors whenever any of the Key Vault secret resources creation will be triggered before the Key Vault access policy resource creation completes, leading to 403 Forbidden errors (in the example below ml-container-registry-name KV secret cannot be created because the key vault access policy is not yet in place)

For example:
```
Error: checking for presence of existing Secret "ml-container-registry-name": keyvault.BaseClient#GetSecret: Failure responding to request: StatusCode=403 -- Original Error: autorest/azure: Service returned an error. Status=403 Code="Forbidden" Message="The user, group or application 'appid=***' does not have secrets get permission on key vault 'kv-****;location=westeurope'. InnerError={"code":"AccessDenied"}
│
│   with module.ml.azurerm_key_vault_secret.ml,
│   on ../mlops/main.tf line 16, in resource "azurerm_key_vault_secret" "ml":
│   16: resource "azurerm_key_vault_secret" "ml" {
  ...
  ```
