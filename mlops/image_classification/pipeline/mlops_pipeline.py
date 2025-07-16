# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

import os

from azure.ai.ml.dsl import pipeline
from azure.ai.ml import Input, load_component, MLClient
from azure.identity import DefaultAzureCredential

from mlops.common.pipeline.prepare_execute import ArgRunner
from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)

gl_pipeline_components = []


@pipeline()
def image_classification_job(pipeline_job_input, model_name, build_reference):
    prepare_data = gl_pipeline_components[0](
        raw_data=pipeline_job_input,
    )
    train_with_data = gl_pipeline_components[1](
        training_data=prepare_data.outputs.training_data,
    )
    score_with_data = gl_pipeline_components[2](
        test_data=prepare_data.outputs.test_data,
        model=train_with_data.outputs.model_output,
    )
    register_model_with_data = gl_pipeline_components[3](
        model_metadata=train_with_data.outputs.model_metadata,
        model_name=model_name,
        score_report=score_with_data.outputs.score_report,
        build_reference=build_reference,
    )

    return {
        "pipeline_job_training_data": prepare_data.outputs.training_data,
        "pipeline_job_test_data": prepare_data.outputs.test_data,
        "pipeline_job_trained_model": train_with_data.outputs.model_output,
        "pipeline_job_score_report": score_with_data.outputs.score_report,
        "pipeline_job_azureml_outputs": register_model_with_data.outputs.azureml_outputs,
    }


def construct_pipeline(args: dict, compute, environment):
    return construct(
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


def construct(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    cluster_name: str,
    environment_name: str,
    display_name: str,
    deploy_environment: str,
    build_reference: str,
    model_name: str,
    asset_name: str,
):
    client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )

    parent_dir = os.path.join(os.getcwd(), "mlops/image_classification/components")

    latest_asset_version = next(
        i.latest_version for i in client.data.list() if i.name == asset_name
    )

    data_dir = f"azureml:{asset_name}:{latest_asset_version}"

    prepare_data = load_component(source=parent_dir + "/prep.yml")
    train_model = load_component(source=parent_dir + "/train.yml")
    score_data = load_component(source=parent_dir + "/score.yml")
    register_model = load_component(source=parent_dir + "/register.yml")

    # Set the environment name to custom environment using name and version number
    prepare_data.environment = environment_name
    train_model.environment = environment_name
    score_data.environment = environment_name
    register_model.environment = environment_name
    prepare_data()

    gl_pipeline_components.append(prepare_data)
    gl_pipeline_components.append(train_model)
    gl_pipeline_components.append(score_data)
    gl_pipeline_components.append(register_model)

    pipeline_job = image_classification_job(
        Input(type="uri_folder", path=data_dir), model_name, build_reference
    )
    pipeline_job.display_name = display_name
    pipeline_job.tags = {
        "environment": deploy_environment,
        "build_reference": build_reference,
    }

    # demo how to change pipeline output settings
    pipeline_job.outputs.pipeline_job_training_data.mode = "rw_mount"

    # set pipeline level compute
    pipeline_job.settings.default_compute = cluster_name
    pipeline_job.settings.force_rerun = True
    # set pipeline level datastore
    pipeline_job.settings.default_datastore = "workspaceblobstore"

    return pipeline_job


if __name__ == "__main__":

    arg_runner = ArgRunner()

    arg_runner.add_arg(
        "--model_name", type=str, default="Name used for registration of model"
    )
    arg_runner.add_arg(
        "--asset_name",
        type=str,
        required=False,
        help="The data asset to be used by the pipeline.",
    )

    arg_runner.prepare_and_execute(construct_pipeline)
