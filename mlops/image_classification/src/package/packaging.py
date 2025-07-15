"""
Code creates a Pipeline configuration and runtime package from trained model
"""
import argparse
import os
import json
import shutil
import uuid
from pathlib import Path

import mlflow
import tensorflow
from azure.ai.ml import MLClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import ManagedIdentityCredential
from simaticai import deployment

from common.src.base_logger import get_logger

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
    model = ml_client.models.get(name=model_name, version=model_version)

    logger.info(f"Model properties: {model.properties}")

    # Extract the 'model_json' value and parse it as JSON
    model_json = json.loads(model.properties["model_json"])

    # Get the Python version from the 'python_function' flavor
    python_version = model_json["flavors"]["python_function"]["python_version"]
    logger.info(f"python_version: {python_version}")

    model_path = Path(".").resolve()
    os.makedirs(model_path, exist_ok=True)

    ml_client.models.download(
        name=model.name, version=model.version, download_path=model_path
    )

    model_dir = model_path / model.name / "model"
    tf_model = mlflow.tensorflow.load_model(model_dir)
    converter = tensorflow.lite.TFLiteConverter.from_keras_model(tf_model)
    tflite_model = converter.convert()

    target_folder = Path(".") / "models"
    target_folder.mkdir(parents=True, exist_ok=True)

    target_model_path = target_folder / "classification_mobilnet.tflite"
    with open(target_model_path, "wb") as model_file:
        model_file.write(tflite_model)

    return target_model_path, python_version


def get_package_id(ml_client: MLClient, package_name: str):
    """Finds the package_id of an edge package given package in Model registry,
    returns its packageId"""

    package_version = -1
    package_id = None
    try:
        for model in ml_client.models.list(name=package_name):
            if package_version < int(model.version):
                package_id = model.tags.get("packageid")
                package_version = int(model.version)

    except ResourceNotFoundError:
        package_id = str(uuid.uuid4())

    if package_id is None:
        package_id = str(uuid.uuid4())

    logger.info("Package: %s  package_id: %s", package_name, package_id)
    return package_id


def create_package(
    model_path: Path,
    package_version: str,
    package_id: str,
    python_version: str,
    model_name: str,
):

    logger.info(
        " ===> Creating package for %s version %s with package_id %s",
        model_name,
        package_version,
        package_id,
    )

    """Create a PythonComponent to use the saved model."""

    current_dir = Path(os.path.dirname(__file__))
    logger.info(f"current_dir: {current_dir}")

    mlops_folder = (current_dir / ".." / ".." / "..").resolve()
    mlops_folder = mlops_folder.resolve()
    logger.info(f"mlops_folder: {mlops_folder}")

    target_path = Path("packages").resolve()
    logger.info("target_path: {%s}", target_path)
    logger.info("model_path: {%s}", model_path)

    # e.g.: model_path = "/somepath/image_classification/models/classification_mobilnet.tflite"
    # e.g.: model_folder = model_path.parent.parent = "/somepath/image_classification"
    model_folder = Path(model_path).parent.parent.resolve()
    model_file = "models/" + model_path.name

    logger.info("model_folder: {%s}", model_folder)
    logger.info("model_file: {%s}", model_file)

    component = deployment.PythonComponent(
        name="inference",
        desc=COMPONENT_DESCRIPTION,
        version=package_version,
        python_version=python_version,
    )

    component.add_resources(model_folder, model_file)

    component.add_resources(
        current_dir,
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
        "ImageSet",
        "Vision connector ZMQ payload holding the image to be classified.",
    )
    component.add_output(
        "prediction",
        "String",
        "The most probable class predicted for the image as an integer string.",
    )

    component.add_metric("ic_probability")

    requirements_path = current_dir / "runtime_requirements_tflite.txt"
    logger.info(f"requirements_path: {requirements_path}")

    component.set_requirements(requirements_path)

    pipeline = deployment.Pipeline.from_components(
        [component], name=model_name, desc=f"description of {model_name} pipeline"
    )

    logger.info(f"Saving package into {target_path}")
    pipeline_package_path = pipeline.save(
        target_path, version=package_version, package_id=package_id
    )

    return pipeline_package_path


def main(
    model_name: str,
    model_version: str,
    package_path: Path,
    resource_group_name: str,
    workspace_name: str,
    subscription_id: str,
    output_model: str,
):
    """
    Downloads the model from Model registry.
    Creates Edge Package from model.
    Registers the created Edge Package.
    """

    ml_client = get_client(subscription_id, resource_group_name, workspace_name)
    logger.info(f"Pipeline Job parameters: {model_name}, {model_version}")
    logger.info(f"model_name: {model_name}")
    logger.info(f"model_version: {model_version}")
    package_name = model_name + "_edge"
    logger.info(f"package_name: {package_name}")

    model_path, python_version = download_model(ml_client, model_name, model_version)
    package_id = get_package_id(ml_client, package_name)

    package_version = model_version

    config_package_path = create_package(
        model_path,
        package_version,
        package_id,
        python_version,
        model_name,
    )
    package_path = Path(package_path)
    package_path = (
        package_path / "package_path" if package_path.is_dir() else package_path
    )

    logger.info(f"config_package_path: {config_package_path}")
    logger.info(f"package_path: {package_path}")

    logger.info("moving package from %s to %s", config_package_path, package_path)
    shutil.move(config_package_path, package_path)

    if output_model:

        logger.info(f"model_path: {model_path}")

        logger.info(f"output_model: {output_model}")
        os.makedirs(output_model, exist_ok=True)

        output_model_path = Path(output_model) / model_path.name
        logger.info(f"output_model_path: {output_model_path}")

        shutil.copy(model_path, output_model_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser("packaging")
    parser.add_argument("--model_name", type=str, default="Name of registered model")
    parser.add_argument(
        "--model_version", type=str, default="Version of registered model"
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
    parser.add_argument("--output_model", type=str, help="model download to output")

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
        package_path=args.package_path,
        resource_group_name=args.resource_group_name,
        workspace_name=args.workspace_name,
        subscription_id=args.subscription_id,
        output_model=args.output_model,
    )
