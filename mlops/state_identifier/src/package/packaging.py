# SPDX-FileCopyrightText: 2025 Siemens AG
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
import json
import joblib
import pickle
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

PIPELINE_DESCRIPTION = """
        This pipeline runs an Clustering Model on an Industrial Edge device.
        The aim of the model is to distinguishes 3 operation states of a machine based on its energy consumption.

        This model was trained by K-Means clustering on energy consumption data measured
        on 3 phases of electrical current (ph1, ph2, ph3).

        The pipeline receives data from SIMATIC S7 Connector using AI Inference Server's Inter
        Signal Alignment feature.
        The intersignal alignment must be set to the same sampling rate of 250ms that the model was trained on.

        Data goes through a scikit-learn pipeline consisting of 2 stages, a preprocessing and a clustering.
        (Please note that even though the scikit pipeline has 2 stages it will be executed as
        a single component on AI Inference Server)

        The preprocessing step of the scikit-learn pipeline groups input data rows into data windows,
        300 data rows each.
        This window is advanced according to the 'step_size' parameter.
        If 'step_size' is set to the window size (300 in this case) the windows will be adjacent.
        If 'step_size' is set to be smaller than the window size, the windows will overlap.
        The preprocessing of the scikit-learn pipeline calculates a series of basic statistical
        features for each window (e.g.: Min, Max, Mean).

        The model itself is fed with these statistical features, producing a predicted class for each window.
        As a result the pipeline produces a single output for every 'step_size' number of data rows.
        The first output is produced after consuming a complete window (300 data rows)."""


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

    logger.info(
        " ===> Downloading model %s version %s from Model Registry",
        model_name,
        model_version,
    )

    model = ml_client.models.get(name=model_name, version=model_version)

    logger.info(f"model_name: {model_name}")
    logger.info(f"Model properties: {model.properties}")

    # Extract the 'model_json' value and parse it as JSON
    model_json_object = model.properties["model_json"]
    logger.info(f"model_json_object: {model_json_object}")

    model_json = json.loads(model_json_object)
    logger.info(f"model_json: {model_json}")

    # Get the Python version from the 'python_function' flavor
    python_version = model_json["flavors"]["python_function"]["python_version"]
    logger.info(f"python_version: {python_version}")

    download_model_path = Path(".") / "temp"
    logger.info("download_model_path: %s", download_model_path)
    os.makedirs(download_model_path, exist_ok=True)

    ml_client.models.download(
        name=model.name, version=model.version, download_path=download_model_path
    )

    logger.info("model_path: %s", download_model_path)
    for root, dirs, files in os.walk(download_model_path):
        for name in dirs:
            logger.info("Directory: %s", os.path.join(root, name))
        for name in files:
            logger.info("File: %s", os.path.join(root, name))

    model_path = download_model_path / model_name / "model"
    logger.info("model_path: %s", model_path)

    pkl_file = model_path / "model.pkl"
    logger.info("pkl_file: %s", pkl_file)

    model_instance = None
    with open(pkl_file, "rb") as f:
        model_instance = pickle.load(f)

    target_folder = download_model_path / model_name / "models"
    logger.info("target_folder: %s", target_folder)
    target_folder.mkdir(parents=True, exist_ok=True)

    target_model_path = target_folder / "clustering-model.joblib"
    logger.info("target_model_path: %s", target_model_path)

    joblib.dump(model_instance, target_model_path)

    return target_model_path, python_version


def get_package_id(ml_client: MLClient, package_name: str):
    logger.info(" ===> Getting package_id for %s from Model Registry", package_name)
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

    logger.info("package: %s  package_id: %s", package_name, package_id)
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
    logger.info(f"target_path: {target_path}")
    logger.info(f"model_path: {model_path}")

    # e.g.: model_path = "/somepath/image_classification/models/classification_mobilnet.tflite"
    # e.g.: model_folder = model_path.parent.parent = "/somepath/image_classification"
    model_folder = Path(model_path).parent.parent.resolve()
    model_file = "models/" + model_path.name

    logger.info(f"model_folder: {model_folder}")
    logger.info(f"model_file: {model_file}")
    logger.info(f"python_version: {python_version}")

    component = deployment.PythonComponent(
        name="inference",
        desc=COMPONENT_DESCRIPTION,
        version=package_version,
        python_version=python_version,
    )

    component.add_resources(
        current_dir,  # copy files from ../related folder
        ["entrypoint.py"],
    )
    component.add_resources(model_folder, model_file)
    component.set_entrypoint("entrypoint.py")

    component.add_input("ph1", "Double", "Measured energy consumption on phase 1")
    component.add_input("ph2", "Double", "Measured energy consumption on phase 2")
    component.add_input("ph3", "Double", "Measured energy consumption on phase 3")

    component.add_output(
        "prediction", "Integer", "Predicted cluster of the datapoint (0, 1 or 2)"
    )
    component.add_output("inertia", "Double", "Inertia metric on the model")

    component.add_metric("model_input_min")
    component.add_metric("model_input_max")
    component.add_metric("model_input_mean")

    component.add_resources(
        mlops_folder,
        [
            "state_identifier/src/si",
        ],
    )

    pipeline = deployment.Pipeline.from_components(
        [component], name=model_name, desc=PIPELINE_DESCRIPTION
    )

    pipeline.add_parameter("step_size", 300, "Integer")
    pipeline.set_timeshifting_periodicity(250)

    requirements_path = current_dir / "requirements.txt"
    logger.info(
        f"requirements_path: {requirements_path}",
    )
    component.set_requirements(requirements_path)

    logger.info(f"Saving package into {target_path}")
    pipeline_package_path = pipeline.save(
        target_path,
        version=package_version,
        package_id=package_id,
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
        model_path, package_version, package_id, python_version, model_name
    )
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
