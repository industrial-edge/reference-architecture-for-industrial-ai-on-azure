import argparse
import azure.core.exceptions
from pathlib import Path

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment, BuildContext
from azure.identity import DefaultAzureCredential

from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)


def get_environment(args: dict):
    return get(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.conda_path,
        args.environment_name,
        args.env_description,
        eval(args.update_env),
    )


def get(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    conda_path: str,
    environment_name: str,
    description: str,
    update_env: bool,
):
    try:
        logger.info(f"Checking {environment_name} environment.")
        logger.info(f"update_env: {update_env}")

        client = MLClient(
            DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )

        environments = client.environments.list(name=environment_name)

        if update_env or not environments:
            env_docker_conda = Environment(
                build=BuildContext(path=Path(conda_path).parent),
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

            version_numbers = []
            for env in environments:
                version_numbers.append(int(env.version))

            latest_version = max(version_numbers, default=-1)
            logger.info(f"Latest version: {latest_version}")

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


def environment_argument_parser(parser: argparse.ArgumentParser):
    def add_arg(parser, arg_name, **kwargs):
        logger.info("environment. Adding argument %s", arg_name)
        if not any(arg_name in action.option_strings for action in parser._actions):
            parser.add_argument(arg_name, **kwargs)

    add_arg(parser, "--subscription_id", type=str, help="Azure subscription id")
    add_arg(
        parser,
        "--resource_group_name",
        type=str,
        help="Azure Machine learning resource group",
    )
    add_arg(
        parser,
        "--workspace_name",
        type=str,
        help="Azure Machine learning Workspace name",
    )
    add_arg(
        parser,
        "--env_base_image_name",
        type=str,
        help="Environment custom base image name",
    )
    add_arg(parser, "--conda_path", type=str, help="path to conda requirements file")
    add_arg(
        parser,
        "--environment_name",
        type=str,
        help="Azure Machine learning environment name",
    )
    add_arg(
        parser,
        "--env_description",
        type=str,
        default="Environment created using Conda.",
    )
    add_arg(
        parser,
        "--update_env",
        type=str,
        help="Determines if Azure Machine Learning Environment should be updated or not.",
        required=False,
        default="False",
    )


def main():
    parser = argparse.ArgumentParser("prepare_environment")
    environment_argument_parser(parser)

    args = parser.parse_args()
    get_environment(args)


if __name__ == "__main__":
    main()
