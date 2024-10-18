# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from mlops.image_classification.src.package import packaging


class TestModelPackaging(TestCase):
    _args = {
        "model_name": "any_model_name",
        "model_version": "1",
        "package_name": "any_package_name",
        "package_version": "1",
        "package_id": "ffd6b8a0-10ad-401a-ad05-805cdf05ba7c",
        "package_path": "/tmp/package.zip",
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

        cls._package_dir = Path(cls._tempdir) / "image_classification/src/package/"
        Path(cls._package_dir / "classification_mobilnet.pb").touch()

        os.chdir(cls._tempdir)

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        os.chdir(cls._workdir)
        shutil.rmtree(cls._tempdir)
        return super().tearDownClass()

    @patch("mlops.image_classification.src.package.packaging.MLClient")
    @patch("mlflow.tensorflow.load_model")
    @patch("tensorflow.lite.TFLiteConverter.from_keras_model")
    def test_main_success(
        self, mock_tf_from_keras, mock_mlflow_load_model, mock_ml_client
    ):
        # GIVEN

        mock_model_object = MagicMock()
        mock_model_object.name = self._args["model_name"]
        mock_model_object.version = self._args["model_version"]
        mock_model_object.download_path = "azureml:.../datastore/../model"
        mock_model_object.return_value = mock_model_object

        mock_package_object = MagicMock()
        mock_package_object.name = self._args["package_name"]
        mock_package_object.version = 1
        mock_package_object.tags = {"packageid": self._args["package_id"]}
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

        mock_mlflow_load_model.return_value = b"tensorflow_model"
        mock_tf_converter = MagicMock()
        mock_tf_converter.convert.return_value = b"tflite_model_representation"

        mock_tf_from_keras.return_value = mock_tf_converter

        # WHEN
        packaging.main(
            self._args["model_name"],
            self._args["model_version"],
            self._args["package_name"],
            self._args["package_path"],
            self._args["resource_group_name"],
            self._args["workspace_name"],
            self._args["subscription_id"],
        )

        # THEN
        # now only the configuration package is created
        self.assertTrue(Path(self._args["package_path"]).is_file())

    @patch("mlops.image_classification.src.package.packaging.MLClient")
    @patch("mlflow.tensorflow.load_model")
    @patch("tensorflow.lite.TFLiteConverter.from_keras_model")
    def test_download_model(
        self,
        mock_tf_from_keras: MagicMock,
        mock_mlflow_load_model: MagicMock,
        mock_ml_client: MagicMock,
    ):

        # GIVEN
        mock_mlflow_load_model.return_value = b"tensorflow_model"
        mock_tf_converter = MagicMock()
        mock_tf_converter.convert.return_value = b"tflite_model_representation"

        mock_tf_from_keras.return_value = mock_tf_converter

        # WHEN
        model = packaging.download_model(
            mock_ml_client,
            self._args["model_name"],
            self._args["model_version"],
        )

        # THEN
        mock_ml_client.models.get.assert_called_once()
        mock_ml_client.models.download.assert_called_once()
        self.assertIsNotNone(model)

    @patch("mlops.image_classification.src.package.packaging.MLClient")
    def test_get_latest(self, mock_ml_client):
        # GIVEN

        mock_package_object = MagicMock()
        mock_package_object.name = self._args["package_name"]
        mock_package_object.version = int(self._args["package_version"])
        mock_package_object.tags = {"packageid": self._args["package_id"]}
        mock_package_object.return_value = mock_package_object
        expected_verson = int(self._args["package_version"]) + 1

        mock_ml_client_object = MagicMock()
        mock_ml_client_object.models.get.side_effect = [
            mock_package_object,
            mock_package_object,
        ]
        mock_ml_client_object.models.list.side_effect = [
            [mock_package_object],
            [mock_package_object],
        ]
        mock_ml_client.return_value = mock_ml_client_object

        # WHEN
        package_version, package_id = packaging.get_latest(
            mock_ml_client_object, self._args["package_name"]
        )

        # THEN
        self.assertEqual(int(package_version), expected_verson)
        self.assertEqual(package_id, self._args["package_id"])
