# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import os

from azure.ai.ml import load_component
from azure.ai.ml.dsl import pipeline

from mlops.common.pipeline.get_compute import get_compute
from mlops.common.pipeline.get_environment import get_environment
from mlops.common.pipeline.pipeline_execution_utils import (
    execute_pipeline,
)
from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)

gl_pipeline_components = []


@pipeline()
def data_asset_creation_pipeline(
    github_url: str,
    asset_name_ci: str,
    asset_name_pr: str,
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    subsample_percentage: str,
    model_type: str,
):
    """
    Creates the pipeline components.

    Arguments:
    github_url: str
        Path to github repository containing raw data
    asset_name_ci: str
        Name of the asset for the CI pipeline
    asset_name_pr: str
        Name of the asset for the PR pipeline
    subscription_id: str
        Azure subscription id
    resource_group_name: str
        Azure Machine learning resource group
    workspace_name: str
        Azure Machine learning Workspace name
    subsample_percentage: str
        Percentage of data to be used for subsample
    model_type: str
        Type of used machine learning model

    Returns:
       None
    """

    gl_pipeline_components[0](
        github_url=github_url,
        asset_name_ci=asset_name_ci,
        asset_name_pr=asset_name_pr,
        subsample_percentage=subsample_percentage,
        subscription_id=subscription_id,
        workspace_name=workspace_name,
        resource_group_name=resource_group_name,
        model_type=model_type,
    )


def construct_pipeline(
    build_reference: str,
    cluster_name: str,
    environment_name: str,
    display_name: str,
    deploy_environment: str,
    model_type: str,
    subscription_id: str,
    workspace_name: str,
    resource_group_name: str,
    github_url: str,
    asset_name_ci: str,
    asset_name_pr: str,
    subsample_percentage: str,
):
    """
    Loads the components and creates instances of the components.

    Arguments:
        build_reference: str
            Unique identifier for Azure DevOps pipeline run
        cluster_name: str
            Azure Machine learning cluster name
        environment_name: str
            Azure Machine Learning Environment name for job execution
        display_name: str
            Job execution run name
        deploy_environment: str
            execution and deployment environment. e.g. dev, prod
        model_type st:r
            Type of used machine learning model
        subscription_id: str
            Azure subscription id
        workspace_name: str
            Azure Machine learning Workspace name
        resource_group_nam:e str
            Azure Machine learning resource group
        github_url: str
            Path to github repository containing raw data
        asset_name_ci: str
            Name of the asset for the CI pipeline
        asset_name_pr: str
            Name of the asset for the PR pipeline
        subsample_percentage: str
            Percentage of data to be used for subsample

    Returns:
        pipeline_job: PipelineJob
            Azure Machine learning pipeline job
    """
    parent_dir = os.path.join(os.getcwd(), "mlops/common/components")

    create_data_asset = load_component(parent_dir + "/data_asset_creation.yml")

    # Set the environment name to custom environment using name and version number
    create_data_asset.environment = environment_name

    gl_pipeline_components.append(create_data_asset)

    pipeline_job = data_asset_creation_pipeline(
        github_url=github_url,
        asset_name_ci=asset_name_ci,
        asset_name_pr=asset_name_pr,
        model_type=model_type,
        subscription_id=subscription_id,
        workspace_name=workspace_name,
        resource_group_name=resource_group_name,
        subsample_percentage=subsample_percentage,
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
    """
    Selects the compute clusters, environments,
    loads all the necessary components and executes the pipeline.
    """

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
        args.env_base_image_name,
        args.conda_path,
        args.environment_name,
        args.env_description,
        True,
    )

    logger.info(f"Environment: {environment.name}, version: {environment.version}")

    pipeline_job = construct_pipeline(
        build_reference=args.build_reference,
        cluster_name=compute.name,
        environment_name=f"azureml:{environment.name}:{environment.version}",
        display_name=args.display_name,
        deploy_environment=args.deploy_environment,
        model_type=args.model_type,
        subscription_id=args.subscription_id,
        workspace_name=args.workspace_name,
        resource_group_name=args.resource_group_name,
        github_url=args.github_url,
        asset_name_ci=args.asset_name_ci,
        asset_name_pr=args.asset_name_pr,
        subsample_percentage=args.subsample_percentage,
    )

    execute_pipeline(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.experiment_name,
        pipeline_job,
        args.wait_for_completion,
        args.output_file,
        None,
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
        help="execution and deployment environment. e.g. dev, prod",
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
        "--env_description",
        type=str,
        default="Environment created using Conda.",
    )
    parser.add_argument(
        "--env_base_image_name",
        type=str,
        help="Base image name for the environment",
    )
    parser.add_argument(
        "--model_type", type=str, help="Type of used machine learning model"
    )
    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run id"
    )
    parser.add_argument(
        "--subsample_percentage",
        type=str,
        default=0.1,
        help="Percentage of data to be used for subsample",
    )
    parser.add_argument(
        "--github_url",
        type=str,
        help="Path to github repository containing raw data",
    )
    parser.add_argument(
        "--asset_name_ci",
        type=str,
        help="Name of the asset for the CI pipeline",
    )
    parser.add_argument(
        "--asset_name_pr",
        type=str,
        help="Name of the asset for the PR pipeline",
    )

    args = parser.parse_args()

    prepare_and_execute(args)


if __name__ == "__main__":
    main()
