# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import requests
from azure.ai.ml.constants import AssetTypes
from azure.identity import CredentialUnavailableError

from mlops.state_identifier.src.data_asset_creation.data_asset_creation import (
    create_data_asset,
    create_subsample_parquet,
    download_file,
    main,
)


class TestDataAssetCreation(TestCase):
    _args = {
        "github_url": "link",
        "asset_name_ci": "data_ci",
        "asset_name_pr": "data_pr",
        "subscription_id": "mock_subscription_id",
        "resource_group_name": "mock_resource_group_name",
        "workspace_name": "mock_workspace_name",
        "subsample_percentage": "0.1",
    }

    @patch(
        "mlops.state_identifier.src.data_asset_creation.data_asset_creation.requests.get"
    )
    def test_download_file_success(self, mock_get):
        url_path = self._args["github_url"]
        mock_get.return_value = MagicMock(content=b"data")

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdirname = Path(tmpdirname)
            tmpdirname.mkdir(parents=True, exist_ok=True)

            download_file(tmpdirname / "data_mock.txt", url_path)

            self.assertEqual(len(list(tmpdirname.rglob("./**/*.txt"))), 1)

        mock_get.assert_called_with(url_path, allow_redirects=True, timeout=120)

    def test_create_data_asset_success(self):
        create_or_update_mock = MagicMock()
        client = MagicMock(data=MagicMock(create_or_update=create_or_update_mock))
        _create_args_list = ["path", "file", "asset"]

        create_data_asset(client, *_create_args_list)

        call_args_create = create_or_update_mock.call_args_list[0][0][0]

        self.assertEqual(call_args_create.name, _create_args_list[2])
        self.assertEqual(call_args_create.description, "Data Asset")
        self.assertEqual(call_args_create.type, _create_args_list[1])
        self.assertEqual(
            call_args_create.path, Path(os.path.join(os.getcwd(), _create_args_list[0]))
        )
        create_or_update_mock.assert_called_once()

    def test_create_subsample_parquet_success(self):

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdirname = Path(tmpdirname)
            tmpdirname.mkdir(parents=True, exist_ok=True)
            data = np.random.rand(20, 3)
            data_df = pd.DataFrame(data, columns=["1", "2", "3"])
            dataset_path = tmpdirname / "data_mock.parquet"
            subsample_file = tmpdirname / "subsample.parquet"

            data_df.to_parquet(dataset_path)

            create_subsample_parquet(dataset_path, subsample_file, 0.1)
            parquet_file_df = pd.read_parquet(subsample_file)

            self.assertEqual(len(parquet_file_df), 2)
            self.assertEqual(parquet_file_df.shape[1], 3)

    @patch(
        "mlops.state_identifier.src.data_asset_creation.data_asset_creation.MLClient"
    )
    @patch(
        "mlops.state_identifier.src.data_asset_creation.data_asset_creation.download_file"
    )
    @patch(
        "mlops.state_identifier.src.data_asset_creation.data_asset_creation.create_data_asset"
    )
    @patch(
        "mlops.state_identifier.src.data_asset_creation.data_asset_creation.create_subsample_parquet"
    )
    @patch(
        "mlops.state_identifier.src.data_asset_creation.data_asset_creation.tempfile.TemporaryDirectory"
    )
    def test_main_success(
        self,
        mock_tempdir,
        mock_create_subsample_parquet,
        mock_create_data_asset,
        mock_download_file,
        mock_ml_client,
    ):

        temp_dir_instance = MagicMock()
        temp_dir_instance.__enter__.return_value = "file"
        mock_tempdir.return_value = temp_dir_instance

        sample_path = os.path.join("file", "si-sample.parquet")
        subsample_path = os.path.join("file", "si-sample_subsample.parquet")
        mock_create_subsample_parquet.return_value = subsample_path

        main(**self._args)

        mock_ml_client_args = mock_ml_client.call_args_list[0][1]

        self.assertEqual(
            mock_ml_client_args["subscription_id"], self._args["subscription_id"]
        )
        self.assertEqual(
            mock_ml_client_args["resource_group_name"],
            self._args["resource_group_name"],
        )
        self.assertEqual(
            mock_ml_client_args["workspace_name"], self._args["workspace_name"]
        )

        mock_download_file.assert_called_with(sample_path, self._args["github_url"])
        mock_create_subsample_parquet.called_with(
            subsample_path, sample_path, self._args["subsample_percentage"]
        )

        self.assertEqual(mock_create_data_asset.call_count, 2)
        first_call_args_mock_create = mock_create_data_asset.call_args_list[0][0]
        second_call_args_mock_create = mock_create_data_asset.call_args_list[1][0]

        self.assertEqual(
            first_call_args_mock_create[1:],
            (sample_path, AssetTypes.URI_FILE, self._args["asset_name_ci"]),
        )
        self.assertEqual(
            second_call_args_mock_create[1:],
            (subsample_path, AssetTypes.URI_FILE, self._args["asset_name_pr"]),
        )

    @patch(
        "mlops.state_identifier.src.data_asset_creation.data_asset_creation.create_data_asset"
    )
    @patch(
        "mlops.state_identifier.src.data_asset_creation.data_asset_creation.create_subsample_parquet"
    )
    def test_main_failure_wrong_url(
        self, mock_create_subsample_parquet, mock_create_data_asset
    ):

        with self.assertRaises(requests.exceptions.MissingSchema):
            main(**self._args)

        mock_create_subsample_parquet.assert_not_called()
        mock_create_data_asset.assert_not_called()

    @patch(
        "mlops.state_identifier.src.data_asset_creation.data_asset_creation.download_file"
    )
    @patch(
        "mlops.state_identifier.src.data_asset_creation.data_asset_creation.create_subsample_parquet"
    )
    @patch("mlops.state_identifier.src.data_asset_creation.data_asset_creation.Path")
    def test_main_failure_wrong_credentials(
        self, mock_path, mock_create_subsample_parquet, mock_download_file
    ):
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpdirname = Path(tmpdirname)
            tmpdirname.mkdir(parents=True, exist_ok=True)

            mock_path.return_value = tmpdirname

            f = open(os.path.join(tmpdirname, "si-sample.parquet"), "x")
            f.close()

            mock_create_subsample_parquet.return_value = "path"

            with self.assertRaises(CredentialUnavailableError):
                main(**self._args)
