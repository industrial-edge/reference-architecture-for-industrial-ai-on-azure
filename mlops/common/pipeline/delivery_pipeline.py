# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import os

from azure.ai.ml import load_component
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import Pipeline

from mlops.common.pipeline.get_environment import get_environment
from mlops.common.pipeline.get_compute import get_compute
from mlops.common.pipeline.pipeline_execution_utils import execute_pipeline
from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)

gl_pipeline_components = {}


@pipeline()
def package_delivery(
    keyvault_name: str,
    iot_hub_connection_string_secret_name: str,
    event_hub_connection_string_secret_name: str,
    device_id: str,
    edge_package_name: str,
    edge_package_version: str,
    deploy_environment: str,
):
    gl_pipeline_components.get("deliver_command")(
        keyvault_name=keyvault_name,
        iot_hub_connection_string_secret_name=iot_hub_connection_string_secret_name,
        event_hub_connection_string_secret_name=event_hub_connection_string_secret_name,
        device_id=device_id,
        edge_package_name=edge_package_name,
        edge_package_version=edge_package_version,
        deploy_environment=deploy_environment,
    )
    return {}


def construct_pipeline(
    build_reference: str,
    cluster_name: str,
    environment: str,
    display_name: str,
    keyvault_name: str,
    iot_hub_connection_string_secret_name: str,
    event_hub_connection_string_secret_name: str,
    device_id: str,
    edge_package_name: str,
    edge_package_version: str,
    deploy_environment: str,
) -> Pipeline:
    parent_dir = os.path.join(os.getcwd(), "mlops/common/components")
    deliver_command = load_component(source=parent_dir + "/deliver.yml")
    deliver_command.environment = environment
    gl_pipeline_components.update(deliver_command=deliver_command)

    pipeline_job = package_delivery(
        keyvault_name,
        iot_hub_connection_string_secret_name,
        event_hub_connection_string_secret_name,
        device_id,
        edge_package_name,
        edge_package_version,
        deploy_environment,
    )
    pipeline_job.display_name = display_name
    pipeline_job.tags = {
        "build_reference": build_reference,
    }
    pipeline_job.settings.default_compute = cluster_name
    pipeline_job.settings.force_rerun = True
    pipeline_job.settings.default_datastore = "workspaceblobstore"

    return pipeline_job


def prepare_and_execute(args: dict):
    compute = get_compute(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.cluster_name,
        args.cluster_size,
        args.cluster_region,
        args.min_instances,
        args.max_instances,
        args.idle_time_before_scale_down,
    )
    logger.info("Compute name {%s}", compute.name)

    environment = get_environment(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.env_base_image_name,
        args.conda_path,
        args.environment_name,
        args.env_description,
        eval(args.update_env),
    )
    logger.info(f"Environment: {environment.name}, version: {environment.version}")

    pipeline_job = construct_pipeline(
        args.build_reference,
        compute.name,
        f"azureml:{environment.name}:{environment.version}",
        args.display_name,
        args.keyvault_name,
        args.iot_hub_connection_string_secret_name,
        args.event_hub_connection_string_secret_name,
        args.device_id,
        args.edge_package_name,
        args.edge_package_version,
        args.deploy_environment,
    )

    execute_pipeline(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.experiment_name,
        pipeline_job,
        args.wait_for_completion,
        args.output_file,
    )


def main():
    parser = argparse.ArgumentParser("build_environment")
    parser.add_argument(
        "--build_reference",
        type=str,
        help="Unique identifier for Azure DevOps pipeline run",
    )
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure Machine learning resource group"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine learning Workspace name"
    )
    parser.add_argument(
        "--cluster_name", type=str, help="Azure Machine learning cluster name"
    )
    parser.add_argument(
        "--env_base_image_name", type=str, help="Environment custom base image name"
    )
    parser.add_argument(
        "--conda_path", type=str, help="path to conda requirements file"
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        help="Azure Machine Learning Environment name for job execution",
    )
    parser.add_argument(
        "--env_description", type=str, default="Edge Package Delivery Environment"
    )
    parser.add_argument("--display_name", type=str, help="Job execution run name")
    parser.add_argument(
        "--experiment_name", type=str, help="Job execution experiment name"
    )
    parser.add_argument(
        "--keyvault_name",
        type=str,
        help="The name of the Azure Key vault that stores secrets needed for the delivery",
    )
    parser.add_argument(
        "--iot_hub_connection_string_secret_name",
        type=str,
        help="The name of the secret in Azure Key vault that stores the iot-hub-connections-string",  # noqa: E501
    )
    parser.add_argument(
        "--event_hub_connection_string_secret_name",
        type=str,
        help="The name of the secret in Azure Key vault that stores the event_hub_connection_string",  # noqa: E501
    )
    parser.add_argument(
        "--device_id",
        type=str,
        help="Id of the IoT Hub device that is connected to the desired AI Model Manager workspace",  # noqa: E501
    )
    parser.add_argument(
        "--edge_package_name",
        type=str,
        help="The name of the pacakge in Model Registry.",
    )
    parser.add_argument(
        "--edge_package_version",
        type=str,
        help="The version of the pacakge in Model Registry.",
    )
    parser.add_argument(
        "--wait_for_completion",
        type=str,
        help="determine if pipeline to wait for job completion",
    )

    parser.add_argument(
        "--deploy_environment",
        type=str,
        help="Environment where asset is deployed",
    )
    parser.add_argument(
        "--update_env",
        type=str,
        help="Determines if Azure Machine Learning Environment should be updated or not.",
        required=False,
        default="False",
    )

    parser.add_argument(
        "--cluster_size", type=str, help="Azure Machine learning cluster size"
    )
    parser.add_argument(
        "--cluster_region", type=str, help="Azure Machine learning cluster region"
    )
    parser.add_argument("--min_instances", type=int, default=0)
    parser.add_argument("--max_instances", type=int, default=4)
    parser.add_argument("--idle_time_before_scale_down", type=int, default=120)

    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run id"
    )
    args = parser.parse_args()

    prepare_and_execute(args)


if __name__ == "__main__":
    main()
