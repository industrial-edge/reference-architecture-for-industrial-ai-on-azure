# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import os
import tempfile
from pathlib import Path

import tensorflow as tf
from azure.ai.ml import MLClient
from azure.ai.ml.constants import AssetTypes
from azure.identity import ManagedIdentityCredential
from common.src.base_logger import get_logger
from common.src.data_asset_creation_utils import create_data_asset
from image_classification.src.prep.prep import save_to_dir

logger = get_logger(__name__)


def main(
    github_url: str,
    asset_name_ci: str,
    asset_name_pr: str,
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    subsample_percentage: str,
):
    client = MLClient(
        credential=ManagedIdentityCredential(
            client_id=os.getenv("DEFAULT_IDENTITY_CLIENT_ID")
        ),
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )

    with tempfile.TemporaryDirectory() as temp_dir_name:
        file_name = Path(f"{temp_dir_name}/simatic_photos.tgz")

        destination_path = Path(temp_dir_name)
        subsample_path = Path(f"{temp_dir_name}/subsample")
        destination_path_processed = Path(f"{temp_dir_name}/simatic_photos")

        tf.keras.utils.get_file(
            fname=file_name,
            origin=github_url,
            extract=True,
            cache_dir=destination_path,
            cache_subdir="",
        )

        downloaded_file = [
            path for path in destination_path.iterdir() if path.is_dir()
        ][0]

        class_labels = [
            path.name for path in downloaded_file.iterdir() if path.is_dir()
        ]

        class_labels.sort()

        labels_dict = {label: i for i, label in enumerate(class_labels)}

        create_subsample_folder(
            downloaded_file, subsample_path, subsample_percentage, class_labels
        )

        create_data_asset(
            client,
            destination_path_processed,
            AssetTypes.URI_FOLDER,
            asset_name_ci,
            tags=labels_dict,
        )
        create_data_asset(
            client,
            subsample_path,
            AssetTypes.URI_FOLDER,
            asset_name_pr,
            tags=labels_dict,
        )

    logger.info(f"Data assets {asset_name_ci} and {asset_name_pr} created successfully")


def create_subsample_folder(
    dataset_path: Path,
    subsample_folder_path: Path,
    percentage_of_data: float,
    class_labels: list,
):
    """
    Create a subsample folder with the given percentage of total images from the given dataset.

    Arguments:
    dataset_path: str
        Path to the folder containing the original dataset
    subsample_folder_path: str
        Path to the folder where the subsampled images should be written
    percentage_of_data: float
        Percentage of the total images to be used as subsample
    window_size: int
        Size of the window used for windowing the data
    class_labels: list
        List containing all the class labels obtained from folder names

    Returns:
    None
        The function does not return any value.
    """
    image_generator = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1 / 255, validation_split=percentage_of_data
    )
    validation_set = image_generator.flow_from_directory(
        str(dataset_path), target_size=(224, 224), subset="validation"
    )

    save_to_dir(validation_set, subsample_folder_path, class_labels)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--github_url",
        type=str,
        help="Path to github repository containing raw data",
    )

    parser.add_argument(
        "--asset_name_ci", type=str, help="Name of the data asset for the CI pipeline"
    )

    parser.add_argument(
        "--asset_name_pr", type=str, help="Name of the data asset for the PR pipeline"
    )

    parser.add_argument(
        "--subscription_id",
        type=str,
        help="Azure subscription ID",
    )

    parser.add_argument(
        "--resource_group_name",
        type=str,
        help="Azure resource group name",
    )

    parser.add_argument(
        "--workspace_name",
        type=str,
        help="Azure Machine Learning workspace name",
    )

    parser.add_argument(
        "--subsample_percentage",
        type=float,
        default=0.1,
        help="Percentage of data to be used for subsample",
    )

    args = parser.parse_args()

    main(
        github_url=args.github_url,
        asset_name_ci=args.asset_name_ci,
        asset_name_pr=args.asset_name_pr,
        subscription_id=args.subscription_id,
        resource_group_name=args.resource_group_name,
        workspace_name=args.workspace_name,
        subsample_percentage=args.subsample_percentage,
    )
