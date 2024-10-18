<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# Branching Strategy and Merge Pipeline

## Introduction

In our project, we maintain two primary branches: the `development` branch (default) and the `main` branch. This section provides an overview of the purpose of each branch, policies, the list of pipelines that target each branch and the merging strategy. It also documents the pipeline that merges the changes from `development` into `main`.

## Branches

### Development Branch

- **Purpose**: The `development` branch is the default one, serves as the integration branch where feature branches are merged once their pull requests (PRs) are completed. This branch contains the latest code changes that are in the process of being validated for broader release.

- **Merging**: Whenever a feature branch is ready for integration, a PR is opened against the `development` branch. Upon successful review, the feature branch is merged into `development`.

- **Policies**:
  - require a minimum number of reviewers (currently 2)
  - changes must be made via pull requests
  - check for linked work items
  - check for comment resolution
  - automatically include reviewers

- **Pipelines that target the development branch**:
  - [Image Classification CI Dev Pipeline](../../devops/pipeline/image_classification_ci_dev_pipeline.yml) (commits/PRs)
  - [State Identifier CI Dev Pipeline](../../devops/pipeline/state_identifier_ci_dev_pipeline.yml) (commits/PRs)

### Main Branch

- **Purpose**: The `main` branch represents the stable version of the project. It reflects the production-ready state of the application, and only tested and validated changes from the `development` branch are merged into it.

- **Merging**: Changes in the `development` branch are merged into the `main` branch using a scheduled pipeline that runs on a weekly basis. More details on the pipeline are provided in the [Merging Strategy](#merging-strategy) section below.

- **Policies**:
  - require a minimum number of reviewers (currently 2)
  - changes must be made via pull requests
  - check for linked work items
  - check for comment resolution
  - automatically include reviewers

- **Pipelines that target the development branch**:
  - [Merge Dev to Main](../../devops/pipeline/merge_dev_to_main.yaml) (scheduled)

## Merging strategy
Development branch is merged into main using a scheduled pipeline implemented in [`devops/pipeline/merge_dev_to_main.yaml`](../../devops/pipeline/merge_dev_to_main.yaml). The pipeline will be triggered on a weekly basis, currently set to run every Monday at 3AM UTC, if there are any new changes in the development branch.
The following steps are executed:

1. Print Azure CLI version.
2. Set default Azure DevOps organization and project.
3. Create a PR that has development branch as source and main branch as target, with a default title and description. The PR is set to auto-complete, ensuring that when all PR critera (like approvals) are met, it will be automatically completed and merged.

## Conclusion

The `development` branch serves as the primary integration point for new features and changes. The `main` branch stands as the representation of the production-ready state, ensuring that only validated and stable changes are released. By making use of the scheduled pipeline, the weekly integration of changes from `development` to `main` is automated.
