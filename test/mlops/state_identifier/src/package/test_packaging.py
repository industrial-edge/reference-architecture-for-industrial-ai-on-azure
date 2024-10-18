# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from azure.core.exceptions import ResourceNotFoundError

from mlops.state_identifier.src.package import packaging


class TestModelPackaging(TestCase):
    _args = {
        "model_name": "any_model_name",
        "model_version": "1",
        "package_name": "any_package_name",
        "package_path": "tempfile",
        "resource_group_name": "any_resource_group",
        "workspace_name": "any_workspace",
        "subscription_id": "any_subscription",
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls._workdir = Path(".").resolve()
        cls._tempdir = Path(tempfile.mkdtemp()).resolve()
        cls._tempdir.mkdir(parents=True, exist_ok=True)

        cls._src_dir = Path("mlops").resolve()

        shutil.copytree(cls._src_dir, cls._tempdir, dirs_exist_ok=True)

        cls._package_dir = Path(cls._tempdir) / "state_identifier/src/package/"
        Path(cls._package_dir / "model.pkl").touch()

        os.chdir(cls._tempdir)

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        os.chdir(cls._workdir)
        shutil.rmtree(cls._tempdir)
        return super().tearDownClass()

    @patch("mlops.state_identifier.src.package.packaging.MLClient")
    def test_main_success(self, mock_ml_client):
        # GIVEN

        mock_model_object = MagicMock()
        mock_model_object.name = self._args["model_name"]
        mock_model_object.version = self._args["model_version"]
        mock_model_object.download_path = "azureml:.../datastore/../model"
        mock_model_object.return_value = mock_model_object

        mock_package_object = MagicMock()
        mock_package_object.name = self._args["package_name"]
        mock_package_object.version = 1
        mock_package_object.tags = {"packageid": "ffd6b8a0-10ad-401a-ad05-805cdf05ba7c"}
        mock_package_object.return_value = mock_package_object

        mock_ml_client_object = MagicMock()
        mock_ml_client_object.models.get.side_effect = [
            mock_model_object,
            mock_package_object,
        ]
        mock_ml_client_object.models.list.side_effect = [
            [mock_model_object],
            [mock_package_object],
        ]
        mock_ml_client.return_value = mock_ml_client_object

        # WHEN
        packaging.main(**self._args)

        # THEN
        # now only the configuration package is saved in target directory
        # (Pipeline Config Package)

        assert Path(self._args["package_path"]).is_file()

    @patch("mlops.state_identifier.src.package.packaging.MLClient")
    def test_main_fails_already_exists(self, mock_ml_client):
        # GIVEN

        mock_ml_client_object = MagicMock()
        mock_ml_client_object.models.get.side_effect = ResourceNotFoundError

        mock_ml_client.return_value = mock_ml_client_object

        # WHEN method called, THEN ResourceNotFoundError raised
        with self.assertRaises(ResourceNotFoundError):
            packaging.main(**self._args)
