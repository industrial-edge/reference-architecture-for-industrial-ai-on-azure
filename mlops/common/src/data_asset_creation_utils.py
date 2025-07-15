from azure.ai.ml.entities import Data
from azure.ai.ml import MLClient
from azure.ai.ml.constants import AssetTypes
from pathlib import Path
from typing import Union


def create_data_asset(
    client: MLClient,
    path: Path,
    asset_type: Union[AssetTypes.URI_FOLDER, AssetTypes.URI_FILE],
    asset_name: str,
    tags: dict = None,
):
    """
    Creates a data asset in the Azure Machine Learning workspace.

    Arguments:
    client : MLClient
        The Azure Machine Learning client.
    path : Path
        The path to the file where the dataset is stored.
    asset_type : Union[AssetTypes.URI_FOLDER, AssetTypes.URI_FILE]
        The type of the asset. Can be either AssetTypes.URI_FOLDER or AssetTypes.URI_FILE.
    asset_name : str
        The name of the asset in AzureML.
    tags : dict
        The tags to be added to the asset.

    Returns:
        None
    """
    data_asset = Data(
        path=path,
        type=asset_type,
        description="Data Asset",
        name=asset_name,
        tags=tags,
    )

    client.data.create_or_update(data_asset)
