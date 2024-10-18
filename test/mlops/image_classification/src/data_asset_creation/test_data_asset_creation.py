# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from azure.ai.ml.constants import AssetTypes
from image_classification.src.data_asset_creation.data_asset_creation import (
    create_subsample_folder,
    main,
)


class CustomMock:
    def __init__(self, *args, **kwargs):
        self.name = kwargs["name"]

    def __getattr__(self, attr):
        if attr == "name":
            return self.name

    def is_dir(self):
        return True


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
        "image_classification.src.data_asset_creation.data_asset_creation. \
            tf.keras.preprocessing.image.ImageDataGenerator"
    )
    @patch(
        "image_classification.src.data_asset_creation.data_asset_creation.save_to_dir"
    )
    def test_create_subsample_folder_success(
        self, mock_save_to_dir, mock_image_generator
    ):
        mock_save_to_dir.return_value = ""
        _function_args = {
            "dataset_path": Path("mock_dataset_path"),
            "subsample_folder_path": "mock_subsample_path",
            "percentage_of_data": "0.1",
            "class_labels": "mock_class_labels",
        }
        mock_image_generator.return_value.flow_from_directory.return_value = "path"

        create_subsample_folder(**_function_args)

        mock_image_generator.assert_called_with(
            rescale=1 / 255,
            validation_split=_function_args["percentage_of_data"],
        )

        mock_image_generator.return_value.flow_from_directory.assert_called_with(
            str(_function_args["dataset_path"]),
            target_size=(224, 224),
            subset="validation",
        )

        mock_save_to_dir.assert_called_with(
            "path",
            _function_args["subsample_folder_path"],
            _function_args["class_labels"],
        )

    @patch(
        "image_classification.src.data_asset_creation.data_asset_creation. \
            tf.keras.preprocessing.image.ImageDataGenerator"
    )
    @patch(
        "image_classification.src.data_asset_creation.data_asset_creation.save_to_dir"
    )
    def test_create_subsample_folder_failure(
        self, mock_save_to_dir, mock_image_generator
    ):
        mock_save_to_dir.return_value = ""
        _function_args = {
            "dataset_path": Path("mock_dataset_path"),
            "subsample_folder_path": "mock_subsample_path",
            "percentage_of_data": "0.1",
            "class_labels": "mock_class_labels",
        }
        mock_image_generator.return_value.flow_from_directory.side_effect = Exception(
            "Not a folder"
        )

        with self.assertRaises(Exception):
            create_subsample_folder(**_function_args)

        mock_image_generator.assert_called_with(
            rescale=1 / 255,
            validation_split=_function_args["percentage_of_data"],
        )

        mock_image_generator.return_value.flow_from_directory.assert_called_with(
            str(_function_args["dataset_path"]),
            target_size=(224, 224),
            subset="validation",
        )

        mock_save_to_dir.assert_not_called()

    @patch("image_classification.src.data_asset_creation.data_asset_creation.MLClient")
    @patch(
        "image_classification.src.data_asset_creation.data_asset_creation.create_data_asset"
    )
    @patch(
        "image_classification.src.data_asset_creation.data_asset_creation.create_subsample_folder"
    )
    @patch(
        "image_classification.src.data_asset_creation.data_asset_creation.Path.iterdir"
    )
    @patch(
        "image_classification.src.data_asset_creation.data_asset_creation.tf.keras.utils.get_file"
    )
    @patch(
        "image_classification.src.data_asset_creation.data_asset_creation.tempfile.TemporaryDirectory"
    )
    @patch("image_classification.src.data_asset_creation.data_asset_creation.os.mkdir")
    def test_main_success(
        self,
        mock_os_mkdir,
        mock_tempdir,
        mock_tf_get_file,
        mock_pathlib_iterdir,
        mock_create_subsample_folder,
        mock_create_data_asset,
        mock_ml_client,
    ):
        mock_tf_get_file.return_value = ""

        temp_dir_instance = MagicMock()
        temp_dir_instance.__enter__.return_value = "file"
        mock_tempdir.return_value = temp_dir_instance

        class_labels = ["dir1", "dir2"]

        mock_pathlib_iterdir.return_value = [
            CustomMock(name=class_labels[0]),
            CustomMock(name=class_labels[1]),
        ]

        destination_path = Path("file") / "processed"
        subsample_path = Path("file") / "subsample"

        main(**self._args)

        mock_tf_get_dict = mock_tf_get_file.call_args_list[0][1]

        self.assertEquals(mock_tf_get_dict["origin"], self._args["github_url"])
        self.assertEquals(mock_tf_get_dict["extract"], True)
        self.assertEquals(mock_tf_get_dict["cache_subdir"], "")

        self.assertEquals(mock_pathlib_iterdir.call_count, 2)

        mock_create_subsample_folder.assert_called_with(
            destination_path,
            subsample_path,
            self._args["subsample_percentage"],
            class_labels,
        )

        self.assertEqual(mock_create_data_asset.call_count, 2)
        first_call_args_mock_create = mock_create_data_asset.call_args_list[0][0]
        second_call_args_mock_create = mock_create_data_asset.call_args_list[1][0]

        self.assertEqual(
            first_call_args_mock_create[1:],
            (destination_path, AssetTypes.URI_FOLDER, self._args["asset_name_ci"]),
        )
        self.assertEqual(
            second_call_args_mock_create[1:],
            (subsample_path, AssetTypes.URI_FOLDER, self._args["asset_name_pr"]),
        )

    @patch("image_classification.src.data_asset_creation.data_asset_creation.MLClient")
    @patch(
        "image_classification.src.data_asset_creation.data_asset_creation.create_data_asset"
    )
    @patch(
        "image_classification.src.data_asset_creation.data_asset_creation.create_subsample_folder"
    )
    def test_main_failure_wrong_url(
        self, mock_create_subsample_folder, mock_create_data_asset, mock_ml_client
    ):

        with self.assertRaises(ValueError):
            main(**self._args)

        mock_create_subsample_folder.assert_not_called()
        mock_create_data_asset.assert_not_called()
        mock_ml_client.assert_called_once()
