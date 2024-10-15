# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

"""
Code creates a Pipeline configuration and runtime package from trained model
"""
import argparse
import logging
import os
from pathlib import Path
import shutil
import uuid

from azure.ai.ml import MLClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import ManagedIdentityCredential
from simaticai import deployment

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

COMPONENT_DESCRIPTION = """
        This component receives data rows of measured energy consumption data
        (ph1, ph2, ph3) from SIMATIC S7 Connector and
        predicts a cluster for every 'step_size' number of data rows."""


def get_client(subscription_id, resource_group_name, workspace_name):
    """Creates MLClient to work in MLOps Job"""

    ml_client = MLClient(
        credential=ManagedIdentityCredential(
            client_id=os.getenv("DEFAULT_IDENTITY_CLIENT_ID")
        ),
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )

    return ml_client


def download_model(ml_client: MLClient, model_name: str, model_version: str):
    """Downloads trained model from Model Registry"""
    model_path = Path(".").resolve()
    os.makedirs(model_path, exist_ok=True)

    model = ml_client.models.get(name=model_name, version=model_version)
    ml_client.models.download(
        name=model.name, version=model.version, download_path=model_path
    )

    models = list(f for f in model_path.rglob("./**/model.pkl"))
    logger.info("Downloaded models: %s", models)

    if len(models) > 0:
        return models[0]


def get_latest(ml_client: MLClient, package_name: str):
    """Finds the latest version of the given package in Model registry,
    returns its version number and packageId"""

    # TODO: This approach to get the package_version and package_id is problematic
    # in case of concurrently running packaging pipelines
    try:
        package_version = max(
            list(int(p.version) for p in ml_client.models.list(name=package_name))
        )
        package_id = ml_client.models.get(
            name=package_name, version=package_version
        ).tags.get("packageid")
    except ResourceNotFoundError:
        package_version = 0
        package_id = str(uuid.uuid4())

    logger.info("Latest version of %s: %s", package_name, package_version)
    return str(package_version + 1), package_id


def create_package(model_path: Path, package_version: str, package_id: str):
    """Create a PythonComponent to use the saved model."""

    target_path = Path("packages").resolve()
    model_folder = Path(model_path).parent.resolve()
    model_file = model_path.name

    component = deployment.PythonComponent(
        name="inference",
        desc=COMPONENT_DESCRIPTION,
        version="1.0.0",
        python_version="3.8",
    )

    logger.info("Working directory for packaging: %s", Path(".").resolve())
    component.add_resources(model_folder, model_file)
    component.add_resources(
        Path("state_identifier/src/package"),  # copy files from ../related folder
        [
            "__init__.py",
            "entrypoint.py",
            "inference.py",
        ],
    )
    component.add_resources(".", "state_identifier/src/prep/preprocessing_utils.py")
    component.set_entrypoint("entrypoint.py")

    component.add_input("ph1", "Double", "Measured energy consumption on phase 1")
    component.add_input("ph2", "Double", "Measured energy consumption on phase 2")
    component.add_input("ph3", "Double", "Measured energy consumption on phase 3")

    component.add_output(
        "prediction", "Integer", "Predicted cluster of the datapoint (0, 1 or 2)"
    )
    component.add_output("inertia", "Double", "Inertia mertic on the model")

    component.add_metric("model_input_min")
    component.add_metric("model_input_max")
    component.add_metric("model_input_mean")

    component.set_requirements(Path("state_identifier/src/package/requirements.txt"))

    pipeline = deployment.Pipeline.from_components(
        [component], name="State Identifier", desc="State Identifier"
    )

    pipeline.add_parameter("step_size", 300, "Integer")
    pipeline.set_timeshifting_periodicity(250)

    logger.info("Saving package into %s", target_path)
    pipeline_package_path = pipeline.save(
        target_path, version=package_version, package_id=package_id
    )

    return pipeline_package_path


def main(
    model_name: str,
    model_version: str,
    package_name: str,
    package_path: Path,
    resource_group_name: str,
    workspace_name: str,
    subscription_id: str,
):
    """
    Downloads the model from Model registry.
    Creates Edge Package from model.
    Registers the created Edge Package.
    """

    ml_client = get_client(subscription_id, resource_group_name, workspace_name)
    logger.info("Pipeline Job parameters: %s, %s", model_name, model_version)

    model_path = download_model(ml_client, model_name, model_version)
    package_version, package_id = get_latest(ml_client, package_name)

    config_package_path = create_package(model_path, package_version, package_id)
    package_path = Path(package_path)
    package_path = (
        package_path / "package_path" if package_path.is_dir() else package_path
    )

    logger.info(
        "package_path and package_name: %s, %s (from %s)",
        package_path,
        config_package_path.name,
        package_name,
    )

    logger.info("moving package from %s to %s", config_package_path, Path(package_path))
    shutil.move(config_package_path, Path(package_path))


if __name__ == "__main__":

    parser = argparse.ArgumentParser("packaging")
    parser.add_argument("--model_name", type=str, default="Name of registered model")
    parser.add_argument(
        "--model_version", type=str, default="Version of registered model"
    )

    parser.add_argument(
        "--package_name", type=str, default="Name to use for registering package"
    )

    parser.add_argument(
        "--resource_group_name",
        type=str,
        default="Azure Machine learning resource group",
    )
    parser.add_argument(
        "--workspace_name", type=str, default="Azure Machine learning Workspace name"
    )
    parser.add_argument("--subscription_id", type=str, default="Azure subscription id")
    parser.add_argument("--package_path", type=str, default="UriFile saved package")

    args = parser.parse_args()
    logger.info(
        "Pipeline Job parameters: %s, %s, %s",
        args.model_name,
        args.model_version,
        args.package_path,
    )

    main(
        model_name=args.model_name,
        model_version=args.model_version,
        package_name=args.package_name,
        package_path=args.package_path,
        resource_group_name=args.resource_group_name,
        workspace_name=args.workspace_name,
        subscription_id=args.subscription_id,
    )
