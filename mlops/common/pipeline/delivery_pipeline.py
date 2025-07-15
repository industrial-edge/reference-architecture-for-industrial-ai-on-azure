import os

from azure.ai.ml import load_component
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import Pipeline

from mlops.common.pipeline.prepare_execute import ArgRunner
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


def construct_pipeline(args: dict, compute, environment):
    return construct(
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


def construct(
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


# def prepare_and_execute(args: dict):

#     compute = get_compute(args)
#     logger.info("Compute name {%s}", compute.name)

#     environment = get_environment(args)
#     logger.info(f"Environment: {environment.name}, version: {environment.version}")

#     pipeline_job = construct_pipeline(args, compute, environment)
#     # pipeline_job = construct_pipeline(
#     #     args.build_reference,
#     #     compute.name,
#     #     f"azureml:{environment.name}:{environment.version}",
#     #     args.display_name,
#     #     args.keyvault_name,
#     #     args.iot_hub_connection_string_secret_name,
#     #     args.event_hub_connection_string_secret_name,
#     #     args.device_id,
#     #     args.edge_package_name,
#     #     args.edge_package_version,
#     #     args.deploy_environment,
#     # )

#     execute_pipeline(args, pipeline_job)
#     #None


def main():

    arg_runner = ArgRunner()

    arg_runner.add_arg(
        "--keyvault_name",
        type=str,
        help="The name of the Azure Key vault that stores secrets needed for the delivery",
    )
    arg_runner.add_arg(
        "--iot_hub_connection_string_secret_name",
        type=str,
        help="The name of the secret in Azure Key vault that stores the iot-hub-connections-string",  # noqa: E501
    )
    arg_runner.add_arg(
        "--event_hub_connection_string_secret_name",
        type=str,
        help="The name of the secret in Azure Key vault that stores the event_hub_connection_string",  # noqa: E501
    )
    arg_runner.add_arg(
        "--device_id",
        type=str,
        help="Id of the IoT Hub device that is connected to the desired AI Model Manager workspace",  # noqa: E501
    )
    arg_runner.add_arg(
        "--edge_package_name",
        type=str,
        help="The name of the pacakge in Model Registry.",
    )
    arg_runner.add_arg(
        "--edge_package_version",
        type=str,
        help="The version of the pacakge in Model Registry.",
    )

    arg_runner.prepare_and_execute(construct_pipeline)


if __name__ == "__main__":
    main()
