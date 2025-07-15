# Infrastructure code structure for machine learning workspace

## Introduction
The document describes the resources required in order to create the Azure Machine Learning Workspace and its associated resources.

##Overview
The workspace is the top-level resource for Azure Machine Learning:

* Machine Learning Workspace - a centralized place to work with all the artifacts created when using Azure Machine Learning;
it keeps a history of all jobs, including logs, metrics, output, and a snapshot of the scripts,
it stores references to resources like datastores and compute, it also holds all assets like models, environments, components and data assets

Azure Machine Learning Workspace associated resources:

* Storage Account  - is used to store machine learning artifacts (this storage is used when uploading data to the workspace, stores artifacts such as job logs, if Jupyter notebooks are used these are stored here as well)
* Application Insights - is used to monitor and collect diagnostic information from the inference endpoints
* Key Vault -is used to store secrets that are used by compute targets and any other sensitive information that's needed by the workspace
* Container Registry - registers docker containers that are used during training and when a model is deployed
* Compute Cluster - is a designated compute resource where the job is run or where the endpoint is hosted; a compute cluster is a managed-compute infrastructure that allows the creation of a cluster of CPU or GPU compute nodes in the cloud  

Once the associated resources and the workspaces are created you can interact with it using the Machine Learning Studio

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

```

Some remarks:
* The Key Vault and the Application Insights associated resources are shared resources (used by two or more modules) created as part of the shared module. The mlops module references the Key Vault and
the Application Insights in order to create the workspace. This is achieved by passing the Key Vault ID and the Application Insights ID as variables to the mlops module

```text
main/main.tf

module "shared" {
  source                    = "../shared"
  ...
}

module "ml" {
  ...
  kv_id                             = module.shared.key_vault_id
  appinsights_id                    = module.shared.app_insights_id
  ...

```
