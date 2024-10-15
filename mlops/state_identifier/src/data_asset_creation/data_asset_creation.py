# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import tempfile
from pathlib import Path
import os

import pandas as pd
import requests
from azure.ai.ml import MLClient
from azure.ai.ml.constants import AssetTypes
from azure.identity import ManagedIdentityCredential
from common.src.data_asset_creation_utils import create_data_asset
from common.src.base_logger import get_logger

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
        sample_file = Path(temp_dir_name) / "si-sample"
        sample_path = f"{sample_file}.parquet"

        download_file(sample_path, github_url)

        subsample_data_path = f"{sample_file}_subsample.parquet"
        create_subsample_parquet(sample_path, subsample_data_path, subsample_percentage)

        create_data_asset(client, sample_path, AssetTypes.URI_FILE, asset_name_ci)
        create_data_asset(
            client, subsample_data_path, AssetTypes.URI_FILE, asset_name_pr
        )

    logger.info(f"Data assets {asset_name_ci} and {asset_name_pr} created successfully")


def download_file(path: str, origin: str):
    """
    Downloads a files using the requests library and writes it to a file on local.

    Arguments:
    path: str
        Path to the file in which the downloaded file will be written.
    origin: str
        Link to the GitHub where the dataset is stored.

    Returns:
    None
        The function does not return any value.
    """
    response = requests.get(origin, allow_redirects=True, timeout=120)
    with open(path, "wb") as fout:
        fout.write(response.content)


def create_subsample_parquet(
    dataset_path: str, subsample_file: str, percentage_of_data: float
):
    """
    Creates a subsample of the initial dataset and writes it to a parquet file.

    Arguments:
    dataset_path: str
        Path to the local address of the dataset.
    subsample_file: str
        Path to the file where the subsample will be written.
    percentage_of_data: float
        Percentage of the initial dataset to be saved in the subsample.

    Returns:
    None
        The function does not return any value.
    """
    dataset = pd.read_parquet(dataset_path)
    data_rows = dataset.shape[0]

    percentage_rows = int(data_rows * percentage_of_data)

    data_subset = dataset.head(percentage_rows)
    data_subset.to_parquet(subsample_file, index=False)


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
