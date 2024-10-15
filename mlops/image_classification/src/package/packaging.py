# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

"""
Code creates a Pipeline configuration and runtime package from trained model
"""
import argparse
import os
import shutil
import uuid
from pathlib import Path

import mlflow
import tensorflow
from azure.ai.ml import MLClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import ManagedIdentityCredential
from common.src.base_logger import get_logger
from simaticai import deployment

logger = get_logger(__name__)

COMPONENT_DESCRIPTION = """Image Classification package using MobileNet model
trained for Simatic hardwares."""


def get_client(subscription_id, resource_group_name, workspace_name):
    """Creates MLClient to work in MLOps Job"""

    azure_credential = ManagedIdentityCredential(
        client_id=os.getenv("DEFAULT_IDENTITY_CLIENT_ID")
    )

    ml_client = MLClient(
        credential=azure_credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )
    return ml_client


def download_model(ml_client: MLClient, model_name: str, model_version: str):
    """Downloads trained model from Model Registry and produces a tflite version"""
    model_path = Path(".").resolve()
    os.makedirs(model_path, exist_ok=True)

    model = ml_client.models.get(name=model_name, version=model_version)
    ml_client.models.download(
        name=model.name, version=model.version, download_path=model_path
    )

    model_dir = model_path / model.name / "model"
    tf_model = mlflow.tensorflow.load_model(model_dir)
    converter = tensorflow.lite.TFLiteConverter.from_keras_model(tf_model)
    tflite_model = converter.convert()

    tflite_path = model_path / "classification_mobilnet.tflite"
    with open(tflite_path, "wb") as model_file:
        model_file.write(tflite_model)

    return tflite_path


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

    logger.info("Working directory for packaging: {%s}", Path(".").resolve())
    component.add_resources(model_folder, model_file)
    component.add_resources(
        Path("image_classification/src/package"),  # copy files from ../related folder
        [
            "__init__.py",
            "entrypoint.py",
            "payload.py",
            "vision_classifier.py",
        ],
    )
    component.set_entrypoint("entrypoint.py")

    component.add_input(
        "vision_payload",
        "String",
        "Vision connector MQTT payload holding the image to be classified.",
    )
    component.add_output(
        "prediction",
        "String",
        "The most probable class predicted for the image as an integer string.",
    )

    component.add_metric("ic_probability")

    component.set_requirements(
        Path("image_classification/src/package/runtime_requirements_tflite.txt")
    )

    pipeline = deployment.Pipeline.from_components(
        [component], name="Image Classification", desc="Image Classification TFLite"
    )

    logger.info(f"Saving package into {target_path}")
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
    logger.info(f"Pipeline Job parameters: {model_name}, {model_version}")

    model_path = download_model(ml_client, model_name, model_version)
    package_version, package_id = get_latest(ml_client, package_name)

    config_package_path = create_package(model_path, package_version, package_id)
    package_path = Path(package_path)
    package_path = (
        package_path / "package_path" if package_path.is_dir() else package_path
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
        "--package_path",
        type=str,
        default="UriFile output for saved Pipeline configuration package",
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

    args = parser.parse_args()
    logger.info(f"Pipeline Job parameters: {args.model_name}, {args.model_version}")

    main(
        model_name=args.model_name,
        model_version=args.model_version,
        package_name=args.package_name,
        package_path=args.package_path,
        resource_group_name=args.resource_group_name,
        workspace_name=args.workspace_name,
        subscription_id=args.subscription_id,
    )
