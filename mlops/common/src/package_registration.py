# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import json
import os
from pathlib import Path
import shutil
import yaml
import zipfile

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import ManagedIdentityCredential
from simaticai import deployment

from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(
    resource_group_name: str,
    workspace_name: str,
    subscription_id: str,
    package_path: str,
    metrics_results: str,
    registry_results: str,
    model_name: str,
    model_version: str,
):
    """
    The job checks whether the `validate_package` job was successful,
    takes the Pipeline configuration package from output of job `create_package`.
    In case of successful run the configuration package is converted to
    deployment package and registered in the Model registry.
    """

    logger.info(f"model_name: {model_name}")
    logger.info(f"model_version: {model_version}")

    ml_client = get_client(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )

    package_path = Path(package_path).resolve()
    package_path = (
        package_path / "package_path" if package_path.is_dir() else package_path
    )

    registry_results = Path(registry_results).resolve()
    registry_results = (
        registry_results / "registry_results"
        if registry_results.is_dir()
        else registry_results
    )

    with open(metrics_results, "r") as json_results:
        model_tags = json.loads(json_results.read())

    workdir = Path("./test").resolve()
    workdir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(package_path, "r") as zip_ref:
        zip_ref.extractall(path=workdir)

    config_path = list(workdir.rglob("./**/pipeline_config.yml"))[0]
    logger.info("config_path: %s", config_path)
    with open(config_path, "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    pipeline_info = config["dataFlowPipelineInfo"]
    package_version = pipeline_info["dataFlowPipelineVersion"]
    package_id = pipeline_info["packageId"]

    package_name = pipeline_info["projectName"] + "_edge"

    logger.info("package to be moved: %s\n to: %s", package_path, workdir)
    # pipeline configuration package must be copied from read-only mounted file system
    package_path = shutil.copy(
        str(package_path),
        str(workdir / f"{'-'.join(package_name.split())}_{package_version}.zip"),
    )  # the package zip name is originally the input name of the job
    logger.info("package moved to %s", package_path)

    logger.info(f"package_name: {package_name}")
    logger.info(f"package_version: {package_version}")
    logger.info(f"package_id: {package_id}")

    edge_package_path = deployment.convert_package(package_path)
    register_package(
        ml_client=ml_client,
        package_path=edge_package_path,
        package_name=package_name,
        package_version=package_version,
        package_id=package_id,
        model_tags=model_tags,
        model_name=model_name,
        model_version=model_version,
    )

    registry_results_content = {
        "edge_package_name": package_name,
        "edge_package_version": package_version,
        "edge_package_id": package_id,
    }
    with open(registry_results, "w", encoding="utf-8") as json_file:
        json.dump(registry_results_content, json_file, indent=4)


def get_client(subscription_id: str, resource_group_name: str, workspace_name: str):
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


def register_package(
    ml_client: MLClient,
    package_path: Path,
    package_name: str,
    package_version: str,
    package_id: str,
    model_tags: dict,
    model_name: str,
    model_version: str,
):
    """Registers the packaged model in Model Registry"""
    logger.info(
        "Registering package with name %s and version %s", package_name, package_version
    )

    model_tags["packageid"] = package_id
    model_tags["model_name"] = model_name
    model_tags["model_version"] = model_version

    ml_client.models.create_or_update(
        Model(
            type="custom_model",
            path=package_path,
            name=package_name,
            version=package_version,
            tags=model_tags,
            description="Azure Edge Pipeline Package",
        )
    )
    return package_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--package_path",
        type=str,
        help="Path to saved package",
    )
    parser.add_argument(
        "--registry_results",
        type=str,
        help="Path to resulted json file",
    )
    parser.add_argument(
        "--metrics_results",
        type=str,
        help="File with the computed metrics",
    )
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure Machine learning resource group"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine learning Workspace name"
    )
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument(
        "--model_name", type=str, help="Name of the model in the package"
    )
    parser.add_argument(
        "--model_version", type=str, help="Version of the model in the package"
    )

    args = parser.parse_args()

    main(
        resource_group_name=args.resource_group_name,
        workspace_name=args.workspace_name,
        subscription_id=args.subscription_id,
        package_path=args.package_path,
        metrics_results=args.metrics_results,
        registry_results=args.registry_results,
        model_name=args.model_name,
        model_version=args.model_version,
    )
