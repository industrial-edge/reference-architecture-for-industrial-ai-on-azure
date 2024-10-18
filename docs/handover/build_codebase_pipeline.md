<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# Codebase Build Pipeline

## Overview

This pipeline is designed for the codebase validation. It is triggered by every commit on a feature branch.
The pipeline consists of multiple stages that perform static code analysis, run unit tests on the MLOps module, and conditionally execute infrastructure testing based on the files changed.

## Trigger

- **Pull Request Trigger**: Disabled (no automatic runs on pull requests).
- **Continuous Integration Trigger**:
  - Excluded branches:
    - `main`
    - `development`
  - Included paths for triggers:
    - `devops/pipeline/build_codebase_pipeline.yml`
    - `mlops/*`
    - `infrastructure/*`
    - `test/*`

## Variables

- `vg-az-client`: A variable group containing Azure client configuration used across the pipeline.

## Stages

### Static Analysis

This stage runs static code analysis using Flake8. It sets up a Python environment, installs and executes flake8 for any styling or logical errors using the same set of rules that were previously configured in Gitlab during phase 1. It outputs those errors in an HTML report, and then publishes that report as a pipeline artifact for further inspection.  
The static analysis stage is configured to continue on error, which means the next steps will still run even if there's an error during its execution.​

### Stage: Testing MLOps

This stage is always executed and runs unit tests for the MLOps module.
Jobs:

- **Python Version**: Utilizes Python 3.8 for running tests.
- **Test Execution**: Installs the required dependencies and executes the MLOps unit test suite.

### Testing Infrastructure

This stage conditionally runs tests for the infrastructure based on the detection of changes in the relevant files.

Jobs:

- **Check Changed Files**: Checks out the git repository and uses PowerShell to determine if relevant changes have occurred in the `infrastructure/*` or `devops/pipeline/build_codebase_pipeline.yml` paths. If changes are detected, a variable `runInfrastructureTests` is set to `true`.
- **Run Terraform Test**: This job runs if the previous job has set the `runInfrastructureTests` variable to `true`. It utilizes Go 1.19.3 for running tests and executes Terraform initialization and runs Go-based tests on the infrastructure as code. The job uses Azure credentials provided via pipeline variables to authenticate with Azure services for the execution of Terraform.
