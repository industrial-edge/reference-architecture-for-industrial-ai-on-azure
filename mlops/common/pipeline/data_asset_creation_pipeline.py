# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

import os

from azure.ai.ml import load_component
from azure.ai.ml.dsl import pipeline

from mlops.common.pipeline.prepare_execute import ArgRunner
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


def construct_pipeline(args: dict, compute, environment):
    return construct(
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


def construct(
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


# def prepare_and_execute(args: dict):

#     compute = get_compute(args)
#     logger.info("Compute name {%s}", compute.name)

#     environment = get_environment(args)
#     logger.info(f"Environment: {environment.name}, version: {environment.version}")

#     pipeline_job = construct_pipeline(args, compute, environment)
#     # pipeline_job = construct_pipeline(
#     #     build_reference=args.build_reference,
#     #     cluster_name=compute.name,
#     #     environment_name=f"azureml:{environment.name}:{environment.version}",
#     #     display_name=args.display_name,
#     #     deploy_environment=args.deploy_environment,
#     #     model_type=args.model_type,
#     #     subscription_id=args.subscription_id,
#     #     workspace_name=args.workspace_name,
#     #     resource_group_name=args.resource_group_name,
#     #     github_url=args.github_url,
#     #     asset_name_ci=args.asset_name_ci,
#     #     asset_name_pr=args.asset_name_pr,
#     #     subsample_percentage=args.subsample_percentage,
#     # )

#     execute_pipeline(args, pipeline_job)
#     #None


def main():

    arg_runner = ArgRunner()

    arg_runner.add_arg(
        "--model_type", type=str, help="Type of used machine learning model"
    )
    arg_runner.add_arg(
        "--subsample_percentage",
        type=str,
        default=0.1,
        help="Percentage of data to be used for subsample",
    )
    arg_runner.add_arg(
        "--github_url",
        type=str,
        help="Path to github repository containing raw data",
    )
    arg_runner.add_arg(
        "--asset_name_ci",
        type=str,
        help="Name of the asset for the CI pipeline",
    )
    arg_runner.add_arg(
        "--asset_name_pr",
        type=str,
        help="Name of the asset for the PR pipeline",
    )

    arg_runner.prepare_and_execute(construct_pipeline)


if __name__ == "__main__":
    main()
