# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse

from mlops.common.pipeline.get_compute import get_compute
from mlops.common.pipeline.get_environment import get_environment
from mlops.common.pipeline.pipeline_execution_utils import execute_pipeline
from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)


def prepare_and_execute(args, construct_pipeline):

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
        eval(args.update_env),
    )

    logger.info(f"Environment: {environment.name}, version: {environment.version}")

    pipeline_job = construct_pipeline(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        compute.name,
        f"azureml:{environment.name}:{environment.version}",
        args.display_name,
        args.deploy_environment,
        args.build_reference,
        args.model_name,
        args.asset_name,
    )

    execute_pipeline(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.experiment_name,
        pipeline_job,
        args.wait_for_completion,
        args.output_file,
        ["pipeline_job_mlops_results"],
    )


def read_args_and_execute(construct_pipeline):
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
    parser.add_argument("--max_instances", type=int, default=2)
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
        "--env_base_image_name", type=str, help="Environment custom base image name"
    )
    parser.add_argument(
        "--conda_path", type=str, help="path to conda requirements file"
    )
    parser.add_argument(
        "--env_description", type=str, default="Environment created using Conda."
    )
    parser.add_argument(
        "--model_name", type=str, default="Name used for registration of model"
    )
    parser.add_argument(
        "--output_file", type=str, required=False, help="A file to save run id"
    )
    parser.add_argument(
        "--asset_name",
        type=str,
        required=False,
        help="The data asset to be used by the pipeline.",
    )
    parser.add_argument(
        "--update_env",
        type=str,
        help="Determines if Azure Machine Learning Environment should be updated or not.",
        required=False,
        default="False",
    )

    args = parser.parse_args()

    prepare_and_execute(args, construct_pipeline)
