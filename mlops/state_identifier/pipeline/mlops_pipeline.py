import os

from azure.ai.ml import Input, MLClient, load_component
from azure.ai.ml.dsl import pipeline
from azure.identity import DefaultAzureCredential

from mlops.common.pipeline.prepare_execute import read_args_and_execute
from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)

gl_pipeline_components = []


@pipeline()
def state_identifier_data_regression(pipeline_job_input, model_name, build_reference):
    prepare_data = gl_pipeline_components[0](
        raw_data=pipeline_job_input,
    )
    train_with_data = gl_pipeline_components[1](
        training_data=prepare_data.outputs.prep_data,
    )
    score_with_data = gl_pipeline_components[2](
        prep_data=prepare_data.outputs.prep_data,
        model=train_with_data.outputs.model_output,
    )
    register_model_with_data = gl_pipeline_components[3](  # noqa: F841
        model=train_with_data.outputs.model_output,
        model_name=model_name,
        score_report=score_with_data.outputs.score_report,
        build_reference=build_reference,
        preparation_pipeline_path=prepare_data.outputs.preparation_pipeline_path,
    )

    return {
        "pipeline_job_prepped_data": prepare_data.outputs.prep_data,
        "pipeline_job_trained_model": train_with_data.outputs.model_output,
        "pipeline_job_score_report": score_with_data.outputs.score_report,
        "pipeline_job_mlops_results": register_model_with_data.outputs.mlops_results,
    }


def construct_pipeline(
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

    parent_dir = os.path.join(os.getcwd(), "mlops/state_identifier/components")
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

    pipeline_job = state_identifier_data_regression(
        Input(type="uri_file", path=data_dir),
        model_name,
        build_reference,
    )

    logger.info(f"Job name: {display_name}")

    pipeline_job.display_name = display_name
    pipeline_job.tags = {
        "environment": deploy_environment,
        "build_reference": build_reference,
    }

    # demo how to change pipeline output settings
    pipeline_job.outputs.pipeline_job_prepped_data.mode = "rw_mount"

    # set pipeline level compute
    pipeline_job.settings.default_compute = cluster_name
    pipeline_job.settings.force_rerun = True
    # set pipeline level datastore
    pipeline_job.settings.default_datastore = "workspaceblobstore"

    return pipeline_job


if __name__ == "__main__":
    read_args_and_execute(construct_pipeline)
