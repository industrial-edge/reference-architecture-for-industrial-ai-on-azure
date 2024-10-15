# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

"""
Instantiates MLOps pipeline for packaging
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.append(".")

from azure.ai.ml import Input, MLClient
from azure.ai.ml import load_component
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import Environment, BuildContext
from azure.identity import DefaultAzureCredential

from mlops.common.pipeline.get_compute import get_compute
from mlops.common.pipeline.pipeline_execution_utils import execute_pipeline
from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)

gl_pipeline_components = {}


@pipeline()
def packaging_pipeline_state_identifier(
    pipeline_job_input,
    model_type,
    model_name,
    model_version,
    package_name,
    subscription_id,
    workspace_name,
    resource_group_name,
):

    create_payload = gl_pipeline_components["create_payload"](
        raw_data=pipeline_job_input,
    )

    prepare_data = gl_pipeline_components["prepare_data"](raw_data=pipeline_job_input)

    create_package = gl_pipeline_components["create_package"](
        model_type=model_type,
        model_name=model_name,
        model_version=model_version,
        package_name=package_name,
        subscription_id=subscription_id,
        workspace_name=workspace_name,
        resource_group_name=resource_group_name,
    )

    validate_package = gl_pipeline_components["validate_package"](
        model_type=model_type,
        payload_data=create_payload.outputs.payload_data,
        package_path=create_package.outputs.package_path,
    )

    score_package = gl_pipeline_components["score_package"](
        validation_results=validate_package.outputs.validation_results,
        prep_data=prepare_data.outputs.prep_data,
    )

    register_package = gl_pipeline_components["register_package"](
        package_path=create_package.outputs.package_path,
        subscription_id=subscription_id,
        workspace_name=workspace_name,
        resource_group_name=resource_group_name,
        metrics_results=score_package.outputs.metrics_results,
        model_name=model_name,
        model_version=model_version,
    )

    return {
        "package_path": create_package.outputs.package_path,
        "registry_results": register_package.outputs.registry_results,
    }


@pipeline()
def packaging_pipeline_image_classification(
    pipeline_job_input,
    model_type,
    model_name,
    model_version,
    package_name,
    subscription_id,
    workspace_name,
    resource_group_name,
    asset_name,
    asset_version,
):

    create_payload = gl_pipeline_components["create_payload"](
        raw_data=pipeline_job_input,
    )

    create_package = gl_pipeline_components["create_package"](
        model_type=model_type,
        model_name=model_name,
        model_version=model_version,
        package_name=package_name,
        subscription_id=subscription_id,
        workspace_name=workspace_name,
        resource_group_name=resource_group_name,
    )

    validate_package = gl_pipeline_components["validate_package"](
        model_type=model_type,
        payload_data=create_payload.outputs.payload_data,
        package_path=create_package.outputs.package_path,
    )

    score_package = gl_pipeline_components["score_package"](
        validation_results=validate_package.outputs.validation_results,
        raw_data=pipeline_job_input,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        asset_name=asset_name,
        asset_version=asset_version,
    )

    register_package = gl_pipeline_components["register_package"](
        package_path=create_package.outputs.package_path,
        subscription_id=subscription_id,
        workspace_name=workspace_name,
        resource_group_name=resource_group_name,
        metrics_results=score_package.outputs.metrics_results,
        model_name=model_name,
        model_version=model_version,
    )

    return {
        "package_path": create_package.outputs.package_path,
        "registry_results": register_package.outputs.registry_results,
    }


def construct_pipeline(
    build_reference: str,
    cluster_name: str,
    environment_name: str,
    display_name: str,
    deploy_environment: str,
    model_type: str,
    model_name: str,
    model_version: str,
    package_name: str,
    subscription_id: str,
    workspace_name: str,
    resource_group_name: str,
    raw_data: str,
):
    parent_dir = os.path.join(os.getcwd(), "mlops/common/components")
    logger.info("parent_dir: %s", parent_dir)
    model_dir = os.path.join(os.getcwd(), "mlops", model_type)
    logger.info("model_dir: %s", model_dir)
    logger.info("raw_data name: %s", raw_data)

    client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )

    latest_asset_version = next(
        i.latest_version for i in client.data.list() if i.name == raw_data
    )

    data_dir = f"azureml:{raw_data}:{latest_asset_version}"

    create_payload = load_component(model_dir + "/components/payload.yml")
    gl_pipeline_components["create_payload"] = create_payload

    create_package = load_component(parent_dir + "/package.yml")
    create_package.environment = environment_name
    gl_pipeline_components["create_package"] = create_package

    validate_package = load_component(parent_dir + "/validate.yml")
    validate_package.environment = environment_name
    gl_pipeline_components["validate_package"] = validate_package

    score_package = load_component(model_dir + "/components/score_package.yml")
    score_package.environment = environment_name
    gl_pipeline_components["score_package"] = score_package

    register_package = load_component(parent_dir + "/register.yml")
    register_package.environment = environment_name
    gl_pipeline_components["register_package"] = register_package

    if model_type == "state_identifier":
        prepare_data = load_component(model_dir + "/components/prep.yml")
        prepare_data.environment = environment_name
        gl_pipeline_components["prepare_data"] = prepare_data

        pipeline_job = packaging_pipeline_state_identifier(
            pipeline_job_input=Input(type="uri_file", path=data_dir),
            model_type=model_type,
            model_name=model_name,
            model_version=model_version,
            package_name=package_name,
            subscription_id=subscription_id,
            workspace_name=workspace_name,
            resource_group_name=resource_group_name,
        )
    elif model_type == "image_classification":
        pipeline_job = packaging_pipeline_image_classification(
            pipeline_job_input=Input(type="uri_file", path=data_dir),
            model_type=model_type,
            model_name=model_name,
            model_version=model_version,
            package_name=package_name,
            subscription_id=subscription_id,
            workspace_name=workspace_name,
            resource_group_name=resource_group_name,
            asset_name=raw_data,
            asset_version=latest_asset_version,
        )

    pipeline_job.display_name = display_name
    pipeline_job.tags = {
        "environment": deploy_environment,
        "build_reference": build_reference,
    }

    # set pipeline level compute
    pipeline_job.settings.default_compute = cluster_name
    pipeline_job.settings.force_rerun = True
    # set pipeline level datastore
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

    environment = get_environment(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.conda_path,
        args.environment_name,
        args.env_description,
        eval(args.update_env),
    )

    logger.info(f"Environment: {environment.name}, version: {environment.version}")

    pipeline_job = construct_pipeline(
        build_reference=args.build_reference,
        cluster_name=compute.name,
        environment_name=f"azureml:{environment.name}:{environment.version}",
        display_name=args.display_name,
        deploy_environment=args.deploy_environment,
        model_type=args.model_type,
        model_name=args.model_name,
        model_version=args.model_version,
        package_name=args.package_name,
        subscription_id=args.subscription_id,
        workspace_name=args.workspace_name,
        resource_group_name=args.resource_group_name,
        raw_data=args.raw_data,
    )

    execute_pipeline(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.experiment_name,
        pipeline_job,
        args.wait_for_completion,
        args.output_file,
        ["registry_results"],
    )


def main():
    parser = argparse.ArgumentParser("build_environment")
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
        "--cluster_size", type=str, help="Azure Machine learning cluster size"
    )
    parser.add_argument(
        "--cluster_region", type=str, help="Azure Machine learning cluster region"
    )
    parser.add_argument("--min_instances", type=int, default=0)
    parser.add_argument("--max_instances", type=int, default=4)
    parser.add_argument("--idle_time_before_scale_down", type=int, default=120)

    parser.add_argument(
        "--build_reference",
        type=str,
        help="Unique identifier for Azure DevOps pipeline run",
    )
    parser.add_argument(
        "--deploy_environment",
        type=str,
        help="execution and deployment environment. e.g. dev, prod, test",
    )
    parser.add_argument(
        "--experiment_name", type=str, help="Job execution experiment name"
    )
    parser.add_argument("--display_name", type=str, help="Job execution run name")
    parser.add_argument(
        "--wait_for_completion",
        type=str,
        help="determine if pipeline to wait for job completion",
    )
    parser.add_argument(
        "--environment_name",
        type=str,
        help="Azure Machine Learning Environment name for job execution",
    )
    parser.add_argument(
        "--conda_path", type=str, help="path to conda requirements file"
    )
    parser.add_argument(
        "--env_description", type=str, help="Environment created using Conda."
    )
    parser.add_argument(
        "--model_type", type=str, help="Type of used machine learning model"
    )
    parser.add_argument(
        "--model_name", type=str, help="Name used for registration of model"
    )
    parser.add_argument(
        "--model_version", type=str, help="Version used for registration of model"
    )
    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run id"
    )
    parser.add_argument(
        "--package_name",
        type=str,
        help="Name used for registration of the created package",
    )
    parser.add_argument(
        "--raw_data",
        type=str,
        help="Name of raw data asset",
    )
    parser.add_argument(
        "--payload_data",
        type=str,
        help="Path to payload data to be created",
    )
    parser.add_argument(
        "--update_env",
        type=str,
        help="Determines if Azure Machine Learning Environment should be updated or not.",
        required=False,
        default="False",
    )

    args = parser.parse_args()

    prepare_and_execute(args)


def get_environment(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    conda_path: str,
    environment_name: str,
    description: str,
    update_env: bool,
):
    """
    Creates MLOps Environment for execution of Packaging step
    """
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
                build=BuildContext(path=Path(conda_path).parent),
                name=environment_name,
                description=description,
            )

            environment = client.environments.create_or_update(env_docker_conda)
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

    except Exception as _e:
        logger.info(f"Error occurred while creating ML environment..\n{_e} ")
        raise _e


if __name__ == "__main__":
    main()
