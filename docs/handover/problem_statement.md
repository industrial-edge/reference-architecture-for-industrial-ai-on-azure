<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# Problem Statement and Strategic Objectives

[[_TOC_]]

The purpose of this document is to give an overview of the objectives covered during Phase 1 and Phase 2 of the engagement:

- Infrastructure as Code
- Security
- Reference MLOps Architecture
- Logs and Metrics Architecture
- Improvement of AIMM registration process in the cloud

The individual subjects are explored in more detail in their respective documentations.

## 1. Infrastructure as Code

**Ask**:
Create a solution for automation of IaC (Infrastructure as Code) and CI/CD which will enable Siemens joint customers to run Azure services with best practices baked into the automatically provisioned Azure resources and reference design.

**Outcome**:  
The Terraform infrastructure code is organized into modules in order to manage complexity as the number of resources increases:

- The main module acts as the root, orchestrating the inclusion of all other child modules.
- The common module provides a base for consistent naming and could be extended to include resource "templates" to ensure consistency across the infrastructure.
- There is a shared module that includes common resources like Key Vault, Application Insights, and Log Analytics Workspace, which are used by multiple other modules.
- The IoT management module includes resources for IoT solutions, such as the IoT Hub.
- The MLOps module contains resources necessary for setting up an Azure Machine Learning Workspace, such as a Compute Cluster, Storage Account, and Container Registry.

### Deployment

Key steps for initial deployment from a local environment:

- **Create a Service Principal**: A service principal with at least `Contributor` rights to the subscription must be created if it does not exist.
- **Terraform Remote State**: Set up the Terraform backend configuration as per the Terraform [remote state document](../infra/terraform_remote_state.md).
- **Set Environment Variables**: Define necessary variables in `.devcontainer/devcontainer.env`, which include Azure credentials and default settings.
- **Deployment Script**: Use the `deploy-infra.sh` script to apply Terraform modules. This script also has the capability to run infra-related tests.
To deploy with a Virtual Network (VNET), use the `--enable-vnet` flag.

Key steps for initial deployment from CI/CD pipeline:

- **Service Principal and Terraform State**: Same as the local environment steps 1 and 2.
- **Azure Pipelines Variables**: Set the required Terraform variables in Azure Pipelines by creating a variable group that matches the name used in the pipeline's YAML configuration.
- **Self-Hosted Agents**: If necessary, set up self-hosted agents and ensure their VNET is peered with the main infrastructure VNET for secure pipeline access.
- **Verify VNET Configuration**: Confirm the configuration for the Terraform remote state is correct, particularly for VNET peering, in the main.tf file of the agents.
- **Trigger Deployment Pipeline**: Use the `deploy_infrastructure.yml` pipeline for deploying to environments. The pipeline supports modifiable network IP configuration parameters, which are provided at runtime.

Notes:

- The `deploy-infra.sh` script is common for both local and CI/CD pipeline deployments.
- When deploying from the CI/CD pipeline, additional parameters (`--enable-vnet` and `--peer-pipeline`) are included to accommodate VNET setup and peering with the pipeline agents' VNET.

## 2. Security

**Ask**:
Extend the foundation architecture built in phase 1 to production level by addressing Security, Data privacy areas for automation of infrastructure as code.

**Outcome:**
Threat Modeling was performed using the Microsoft Threat Modeling tool. The process and outcomes are documented in the repository's wiki.  
From the Network Security perspective, the updated architecture incorporates virtual networks (VNETs), subnets, private endpoints, and connectivity options for integrating on-premise networks with Azure services.  

Highlights of the revised architecture:

- **Virtual Networks (VNETs)**: Two VNETs are established:
  - The main VNET for project resources.
  - The runner/agents VNET for self-hosted pipeline agents, peered with the main VNET for infrastructure deployment and MLOps pipeline execution.

- **Subnets within the Main VNET**:
  - **Integration Subnet**: Hosts private endpoints for Platform as a Service (PaaS) resources like ML Workspace, IoT Hub, etc.
  - **Training Subnet**: Contains the compute cluster for model training, secured with a Network Security Group (NSG) for network traffic rules.
  - **GatewaySubnet**: Dedicated to the VPN Gateway required for connecting Azure to on-premise networks.
- **Private Endpoints**: PaaS resources have private endpoints within the VNET, linked to an Azure Private DNS Zone for network resolution. However, Azure Monitor components utilize an Azure Monitor Private Link Scope (AMPLS) to expose a consolidated private endpoint.
- **On-Premise to Azure Connectivity**:
  - A virtual network gateway facilitates both site-to-site and point-to-site VPN connections, allowing secure access to Azure resources from on-premise networks.
  - A VPN gateway requires a GatewaySubnet and can connect on-premise VPN devices or personal computers (via VPN client) to the VNET.
Connected devices receive private IP addresses for accessing resources in the cloud.
  - Azure Private DNS Resolver is deployed for resolving Azure Private Links from the on-premise network.

## 3. Reference MLOps Architecture

**Ask:**
Build production level architecture for MLOps pipelines in Azure to allow for automated and repeatable model training, packaging, and delivery which will enable Microsoft and Siemens joint manufacturing customers to onboard Siemens Industrial AI stack faster than before through automated “Deploy-to-Azure” accelerator.

**Outcome:**

### **MLOps Training Pipelines**

Both use-cases developed during this engagement: _State Identifier_ and _Image Classification_ share the same pipeline structure, which contains the following stages:
1. **Prepare Data**:
- Processes input data from a Data Asset.
- Uses different data sets for the State Identifier (timeseries without labels) and Image Classification (labeled images) use cases.
- Outputs a prepared dataset and a joblib file for the State Identifier; splits and resizes images for Image Classification.

2. **Train with Data**:
- Trains a K-Means model for the State Identifier and a MobileNet-based model for Image Classification.
- Employs mlflow for logging, saving the trained model as a stage output.

3. **Score with Data**:
- Evaluates the model using the prepared data for the State Identifier and testing data for Image Classification.
- Computes performance metrics and logs them with mlflow, with results saved as stage outputs.

4. **Register Model**:
- Registers models to AzureML with mlflow, tagging them with performance metrics.

### Packaging Pipeline

Packaging step is auto-triggered in PR pipelines but requires manual approval in CI pipeline. The MLOps packaging pipeline includes the following stages:

- **Creating payload data**: Converting validation raw data to MQTT messages for image classification or processing Parquet data for state identification.
- **Preparing data**: Transforming data is specific to the State Identifier use case, mirroring steps in the training pipeline.
- **Creating the package**: Compressing all necessary files into a .zip file.
- **Validating the package**: Simulating inference server actions to output validation results.
- **Scoring the package**: Evaluating model performance using metrics analogous to the training pipeline, differing for Image Classification and State Identifier cases.
- **Registering the package**: Post-validation, successful packages are registered in the AzureML Model Registry with associated metrics.

### Delivery Pipeline

The model delivery process occurs after packaging a machine learning model and its dependencies into a zip file. The delivery is executed through an interaction between Azure services and the AI Model Manager (AIMM) via IoT Hub, utilizing an Event Hub messaging endpoint and a SAS link for package download. The process involves continuous updates on the delivery state through a loop.

### CI and PR Pipelines for Code Quality and Model Training

There are two types of pipelines: CI and PR, with a focus on code quality and preparing production-ready models, respectively. There is a CI and a PR pipeline for each implemented use case.  
PR pipelines are designed to ensure code quality for commits and use a subset of the full dataset. CI pipelines aim to train models on the full dataset to create production candidates and are triggered when a pull request is merged into 'development' branch.
The stages for both CI and PR pipelines include variable generation for training, packaging and delivery, model training, packaging, and delivery, with the CI pipeline having two additional approval stages.

### Data Asset Creation Pipeline

The pipeline for creating data assets is defined in a YAML file and comprises two main stages: variable generation and data asset creation job execution:

- **variable_generation_training_packaging**: utilizes a YAML template to extract various variable from a config file such as AzureML workspace details, GitHub URL, model-related information, compute cluster details, experiment metadata, and environment specifics.
- **execute_data_asset_creation_job**: the script used in this step is use case specific:
  - State Identifier: includes functionality to download data, create a subsample, and upload the results as a data asset in AzureML.
  - Image Classification: contains functions to create a subsample of an image dataset and upload the new dataset as a data asset in AzureML.

## 4. Logs and Metrics Architecture

**Ask:**
Design for centralized observability in Azure which will empower Microsoft and Siemens joint customers to monitor their edge applications centrally in Azure rather than logging into each edge device.  

**Outcome:**

**Phase 2 Solution**:

- Utilizes OpenTelemetry Collector (OTelCol) in the Operational Technology (OT) and Information Technology (IT) layers.
- Follows the OTLP protocol for data transfer.
- The OT layer's OTelCol instance collects and possibly relays telemetry data.
- The IT layer's OTelCol instance receives data and sends it to Azure Monitor and an in-factory Prometheus instance.
- The updated architecture removes the need for the Azure Function used in Phase 1.

**Security:**

- mTLS for OTelCol instances.
- AAD-based authentication for Azure Monitor Exporter via an Authentication Proxy.
- Requirement for both Instrumentation Key and an AAD identity with the right role for AppInsights access.

**Reliability:**

- Local persistence of telemetry data to handle OTelCol downtime.
- Data buffering for network interruptions between OT and IT layers and to Azure.
- Retry mechanisms in place for connectivity issues to AppInsights.

**Cost Optimization:**

- Log Analytics configured with a standard 30-day data retention policy.

## 5. Improvement of AIMM registration process in the cloud

**Ask:**
Improve the process of registration of AIMM in the cloud for C2E/E2C communication through the automation of identity creation in DevOps pipelines for Model Manager and Model Monitor.

**Outcome:**
The certificate generation process used in the registration steps for both AI Model Monitor and AI Model Manager has been automated using scripts.

Personas:

- Harald: Automation engineer in the factory, installs AI Model Monitor / AI Model Manager.
- Ian: IT Administrator with the capability to perform certain privileged tasks outside of the factory.

### AI Model Monitor Certificate Generation

Certificate Generation Process:

1. Harald initiates a request for a new Model Monitor Identity.
2. Ian triggers an ADO pipeline to create the identity, which operates under a designated Service Principal.
3. The pipeline requests a certificate from KeyVault.
4. KeyVault creates and retains the certificate.
5. The pipeline then retrieves the certificate and binds it to the Service Principal. It also sets up necessary permissions in Application Insights.
6. A JSON configuration for the Model Monitor is created and stored in KeyVault.

### AI Model Manager Certificate Generation

Certificate Generation Process:

1. Harald initiates a request for a new Model Manager Workspace Identity.
2. Ian triggers an ADO pipeline to create the workspace identity, which operates under a designated Service Principal/
3. The pipeline requests a certificate from KeyVault.
4. KeyVault creates and stores the certificate.
5. The pipeline retrieves the certificate and registers the new device in IoT Hub.
6. A JSON configuration for Model Manager is created and stored in KeyVault.

More detailed documentation on certificate management can be found at:

- [AI Model Monitor Certificate Generation](../certificates/ai_model_monitor_certificate_generation.md)
- [Readme for the scripts used in the creation of Model Monitor Identity and Model Manager Identity](../../devops/pipeline/az_cli_scripts/README.md)
- [ADR on Certificate Management process](https://dev.azure.com/siemens-microsoft-iai/Siemens-Microsoft-IAI/_wiki/wikis/Siemens-Microsoft-IAI.wiki/73/001-Certificate-Management-Process)
