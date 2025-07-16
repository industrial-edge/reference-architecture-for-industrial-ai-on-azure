# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

"""
Instantiates MLOps pipeline for packaging
"""
import os
import sys

sys.path.append(".")

from azure.ai.ml import Input, MLClient
from azure.ai.ml import load_component
from azure.ai.ml.dsl import pipeline
from azure.identity import DefaultAzureCredential

from mlops.common.pipeline.prepare_execute import ArgRunner
from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)

gl_pipeline_components = {}


@pipeline()
def packaging_pipeline_state_identifier(
    pipeline_job_input,
    model_type,
    model_name,
    model_version,
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
        subscription_id=subscription_id,
        workspace_name=workspace_name,
        resource_group_name=resource_group_name,
        asset_name=asset_name,
        asset_version=asset_version,
        validation_results=validate_package.outputs.validation_results,
        raw_data=pipeline_job_input,
        model=create_package.outputs.output_model,
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
        subscription_id=subscription_id,
        workspace_name=workspace_name,
        resource_group_name=resource_group_name,
        asset_name=asset_name,
        asset_version=asset_version,
        validation_results=validate_package.outputs.validation_results,
        raw_data=pipeline_job_input,
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


def construct_pipeline(args: dict, compute, environment):
    return construct(
        build_reference=args.build_reference,
        cluster_name=compute.name,
        environment_name=f"azureml:{environment.name}:{environment.version}",
        display_name=args.display_name,
        deploy_environment=args.deploy_environment,
        model_type=args.model_type,
        model_name=args.model_name,
        model_version=args.model_version,
        subscription_id=args.subscription_id,
        workspace_name=args.workspace_name,
        resource_group_name=args.resource_group_name,
        raw_data=args.raw_data,
    )


def construct(
    build_reference: str,
    cluster_name: str,
    environment_name: str,
    display_name: str,
    deploy_environment: str,
    model_type: str,
    model_name: str,
    model_version: str,
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

    gl_pipeline_components["create_payload"] = load_component(
        model_dir + "/components/payload.yml"
    )
    gl_pipeline_components["create_package"] = load_component(
        parent_dir + "/package.yml"
    )
    gl_pipeline_components["validate_package"] = load_component(
        parent_dir + "/validate.yml"
    )
    gl_pipeline_components["score_package"] = load_component(
        model_dir + "/components/score_package.yml"
    )
    gl_pipeline_components["register_package"] = load_component(
        parent_dir + "/register.yml"
    )

    if model_type == "state_identifier":

        pipeline_job = packaging_pipeline_state_identifier(
            pipeline_job_input=Input(type="uri_file", path=data_dir),
            model_type=model_type,
            model_name=model_name,
            model_version=model_version,
            subscription_id=subscription_id,
            workspace_name=workspace_name,
            resource_group_name=resource_group_name,
            asset_name=raw_data,
            asset_version=latest_asset_version,
        )
    elif model_type == "image_classification":
        pipeline_job = packaging_pipeline_image_classification(
            pipeline_job_input=Input(type="uri_file", path=data_dir),
            model_type=model_type,
            model_name=model_name,
            model_version=model_version,
            subscription_id=subscription_id,
            workspace_name=workspace_name,
            resource_group_name=resource_group_name,
            asset_name=raw_data,
            asset_version=latest_asset_version,
        )

    for component_name, component in gl_pipeline_components.items():
        logger.info(f"Setting environment for component: {component_name}")
        component.environment = environment_name
        gl_pipeline_components[component_name] = component

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


def main():

    arg_runner = ArgRunner()

    arg_runner.add_arg(
        "--model_name", type=str, help="Name used for registration of model"
    )
    arg_runner.add_arg(
        "--model_type", type=str, help="Type of used machine learning model"
    )
    arg_runner.add_arg(
        "--model_version", type=str, help="Version used for registration of model"
    )
    arg_runner.add_arg(
        "--raw_data",
        type=str,
        help="Name of raw data asset",
    )
    arg_runner.add_arg(
        "--payload_data",
        type=str,
        help="Path to payload data to be created",
    )

    arg_runner.prepare_and_execute(construct_pipeline)


if __name__ == "__main__":
    main()
