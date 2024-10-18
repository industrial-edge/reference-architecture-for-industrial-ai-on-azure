# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import azure.core.exceptions

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment
from azure.identity import DefaultAzureCredential

from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)


def get_environment(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    env_base_image_name: str,
    conda_path: str,
    environment_name: str,
    description: str,
    update_env: bool,
):
    try:
        logger.info(f"Checking {environment_name} environment.")
        client = MLClient(
            DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )

        environments = client.environments.list(name=environment_name)

        if update_env or not environments:
            env_docker_conda = Environment(
                image=env_base_image_name,
                conda_file=conda_path,
                name=environment_name,
                description=description,
            )

            for attempts in range(3):
                try:
                    environment = client.environments.create_or_update(env_docker_conda)
                except azure.core.exceptions.ResourceExistsError:
                    if attempts == 2:
                        raise
                    logger.error("Environment already exists. Retrying.")

            logger.info(f"Environment {environment_name} has been created or updated.")
            return environment
        else:
            version_numbers = [int(env.version) for env in environments]
            latest_version = max(version_numbers, default=-1)
            environment = client.environments.get(
                name=environment_name, version=latest_version
            )

            logger.info(
                f"Retrieved the latest version of the environment: {latest_version}"
            )
            return environment

    except Exception:
        logger.critical(
            "Oops! invalid credentials or error while creating ML environment.. Try again..."
        )
        raise


def main():
    parser = argparse.ArgumentParser("prepare_environment")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure Machine learning resource group"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine learning Workspace name"
    )
    parser.add_argument(
        "--env_base_image_name", type=str, help="Environment custom base image name"
    )
    parser.add_argument(
        "--conda_path", type=str, help="path to conda requirements file"
    )
    parser.add_argument(
        "--environment_name", type=str, help="Azure Machine learning environment name"
    )
    parser.add_argument(
        "--description", type=str, default="Environment created using Conda."
    )
    parser.add_argument(
        "--update_env",
        type=str,
        help="Determines if Azure Machine Learning Environment should be updated or not.",
    )
    args = parser.parse_args()

    get_environment(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.env_base_image_name,
        args.conda_path,
        args.environment_name,
        args.description,
        eval(args.update_env),
    )


if __name__ == "__main__":
    main()
