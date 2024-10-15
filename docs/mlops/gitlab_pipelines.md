<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# CI/CD Pipelines on Gitlab
This document describes how the CI/CD Pipeline is structured and how it works in order to create and trigger MLOps Pipeline jobs on Azure ML Workspaces.

## Gitlab Pipeline and Downstream pipelines
In [Gitlab CI](https://docs.gitlab.com/ee/ci/) a pipeline consists of different jobs that define what to do, and stages that define how to run the job.  
For the task that creates and trigger multiple MLOps Pipelines, two [Downstream pipelines](https://docs.gitlab.com/ee/ci/pipelines/downstream_pipelines.html) have been created, and they can be triggered on every GitLab CI/CD pipeline manually.

As the project contains two different use cases and models, they can be executed with two separate pipelines:
- `ic_platform_pipeline` for Image Classification, and
- `si_platform_pipeline` for State Identifier use case.

Each Downstream Pipeline can be triggered with a single job in `trigger` stage,
- `create_ic_pipeline` for Image Classification, and
- `create_si_pipeline` for State Identifer use case.
Once the given job is triggered, the relevant downstream pipeline is started.

## Jobs in the Downstream Pipelines
Both use cases are built up from different steps from data preparation to model delivery. Despite some of them being separate jobs in the MLOps pipeline, they can be merged into one GitLab job.
This way the present pipeline is structured as follows.

### `load_config_variables` (automatic):  
Loads the relevant configuration from the file `mlops/config/model_config.json` to environment variables for the next jobs. This file contains all of data related to the model which is defined by the trigger job.
These variables can be  
- model dependent:  
    Defines the model to be used.
    - `ML_MODEL_CONFIG_NAME`: the key for the model to be used, eg. "state_identifier"
    - `ENV_NAME`: the key for the environment to be used, eg. "dev",
    - `MODEL_BASE_NAME`: tha name used for indentify the model in the MLOps pipeline, eg. "clustering",
    - `PACKAGE_NAME`: the name of the Edge Pipeline Package to create, eg. "State-Identifier-edge",
- MLOPs pipeline relevant:
    - `DISPLAY_BASE_NAME`: the name will be shown in the MLOps pipeline name, eg. "mlops",
    - `EXPERIMENT_BASE_NAME`: the name will be shown in the MLOps pipeline name, eg."stateidentifier",
- Azure infrastructure relevant:  
    Defines the Azure ML Workspace resources which will be used to execute the MLOps Pipeline
    - `RESOURCE_GROUP_NAME`: Resource Group which contains the necessary resources,
    - `WORKSPACE_NAME`: the name of the used Azure ML Workspace,
    - `KEYVAULT_NAME`: the name of the Keyvault which stores the required credentials,
    - `CLUSTER_NAME`: the name of the Compute Cluster to be used for execution,
    - `CLUSTER_REGION`: the Region where the Compute Cluster should be placed,
    - `CLUSTER_SIZE`: the Size of the Compute Cluster to be used for execution,
    - `CONDA_PATH`: the Path of the conda.yml which defines the Python environment for mlops_pipeline,
    - `ENVIRONMENT_NAME`: the name of the Environment to be used for execution,
    - `ENV_BASE_IMAGE_NAME`: the name of the base Docker Image where the Environment with the Python environment will be built,
    - `ASSET_NAME`: the name of the data asset to be used
    - `VALIDATION_ASSET_NAME`: the name of the data asset to be used for validate the packaged model

This job will be executed automatically once the downstream pipeline is started.

### `execute_mlops_pipeline` (automatic):
Builds and executes the MLOps pipeline defined for both models in its own directory via Python module `pipeline.mlops_pipeline`.  

The functionality of the MLOps pipeline is explained in depth in the document [MLOps Training Pipeline](./mlops_training_pipeline.md).

This job will be executed automatically once the previous job is finished successfully.

### `package_model` (manual):  
Once the `execute_mlops_pipeline` is executed, the `packaging_model` can be manually triggered.

The job takes its inputs as:
- `model_name`:  name of the model to package from Model Registry
- `model_version`: version of the same model
- `package_name`: the name of the Edge Pipeline Package to create

The job executes the Python script [packaging_pipeline.py](../../mlops/common/pipeline/packaging_pipeline.py), which creates and executes the required MLOps pipeline on Azure ML Workspace.

During the execution, the module
1) logs into Azure with Service Principal
1) creates a Python environment with `simaticai` for packaging
1) uploads the folder `mlops` as context for the MLOps packaging job
1) obtains or creates a compute cluster to execute the MLOps job

The MLOps packaging job
- gets the defined model from the Model Registry
- creates the Edge Configuration Package with the model specific Python script `mlops/{model_type}/src/package/packaging.py`
- registers the created package in the Model registry

Once the job has been executed successfully, it will pass its outputs as environment variables:
- `package_name`: the name of the registered Edge Configuration Package
- `package_version`: the version of the registered Edge Configuration Package

### `deliver_model` (manual):
Once `package_model` is executed, `deliver_model` can be manually triggered.

The job takes its inputs as:
- `package_name`: the name of the Edge Pipeline Package to deliver
- `package_version`: the version of the Edge Pipeline Package to deliver
- `target_device`: the name of the targeted AI Model Manager registered among the devices of the IoT Hub

The job executes a [delivery_pipeline.py](../../mlops/common/pipeline/delivery_pipeline.py) Python script, which creates and executes the required MLOps pipeline on Azure ML Workspace.

During execution, the module
1) logs into Azure with a Service Principal
1) creates a Python environment for delivery
1) uploads the folder `mlops` as context for the MLOps delivery job
1) obtains or creates a compute cluster to execute the MLOps job

The MLOps delivery job
- gets the defined package from the Model Registry
- creates a SAS link for the package
- initializes a download with the defined AI Model Manager
