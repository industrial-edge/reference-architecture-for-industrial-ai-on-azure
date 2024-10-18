# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

from functools import wraps
from unittest import TestCase
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest

from mlops.image_classification.src.train.train import train_model, main


def patch_train_model_all(f):
    """
    Patches all of the library calls that are required to
    make the train model function work.
    """

    @patch("mlops.image_classification.src.train.train.open")
    @patch("mlops.image_classification.src.train.train.json.dump")
    @patch("mlops.image_classification.src.train.train.tf.keras")
    @patch("mlops.image_classification.src.train.train.mlflow")
    @wraps(f)
    def functor(*args, **kwargs):
        return f(*args, **kwargs)

    return functor


class TestTrain(TestCase):
    _args = {
        "training_data": "./path/to/training_data",
        "image_width": 224,
        "image_height": 224,
        "dim": 3,
        "model_output": "./path/to/model_output",
        "model_metadata": "./path/to/model_metadata",
    }

    @patch(
        "mlops.image_classification.src.train.train.tf.keras.preprocessing.image.ImageDataGenerator"
    )
    @patch("mlops.image_classification.src.train.train.train_model")
    @pytest.mark.integtest
    def test_main_success(self, mock_train_model, mock_image_generator):
        main(**self._args)

        mock_image_generator.assert_called_once()
        mock_image_generator.return_value.flow_from_directory.assert_called_once_with(
            "./path/to/training_data", target_size=(224, 224)
        )
        mock_train_model.assert_called_once()

    @patch_train_model_all
    def test_train_model(self, mock_mlflow, mock_keras, mock_json_dump, mock_open):
        # Prepare
        training_set = MagicMock()
        model_metadata = "model_metadata.json"
        model_output = "model_output/"
        image_size = (244, 244)
        dim = 3

        mock_run = MagicMock()
        mock_run_id = MagicMock()
        mock_file_object = MagicMock()
        mock_run.info.run_id = mock_run_id
        mock_run.__enter__.return_value = mock_run
        mock_mlflow.start_run.return_value = mock_run
        mock_mlflow.active_run.return_value = mock_run
        mock_open.return_value.__enter__.return_value = mock_file_object

        _, label_batch = MagicMock(), MagicMock()
        training_set.next.return_value = _, label_batch

        mock_feature_extractor = MagicMock()
        mock_output = MagicMock()
        mock_feature_extractor.output = mock_output
        mock_keras.applications.MobileNet.return_value = mock_feature_extractor

        mock_average_pooling = MagicMock()
        mock_keras.layers.GlobalAveragePooling2D.return_value = mock_average_pooling

        # Act
        train_model(training_set, model_metadata, model_output, image_size, dim)

        # Assert
        mock_keras.applications.MobileNet.assert_called_once_with(
            weights="imagenet", include_top=False, input_shape=((244, 244) + (3,))
        )
        mock_keras.layers.Dense.assert_called_once_with(
            label_batch.shape[1], activation="softmax"
        )
        mock_keras.layers.Dense.return_value.assert_called_once_with(
            mock_average_pooling()
        )
        mock_keras.Model.assert_called_once_with(
            inputs=mock_feature_extractor.input,
            outputs=mock_keras.layers.Dense.return_value(mock_average_pooling()),
        )
        mock_keras.Model.return_value.compile.assert_called_once()
        mock_keras.Model.return_value.fit_generator.assert_called_once()

        mock_mlflow.start_run.assert_called_once()
        mock_mlflow.active_run.assert_called_once()
        expected_model_data = {
            "run_id": mock_run_id,
            "run_uri": f"runs:/{mock_run_id}/model",
        }
        mock_json_dump.assert_called_once_with(
            expected_model_data, mock_file_object, indent=4
        )
        mock_keras.Model.return_value.save.assert_called_once_with(
            Path("model_output/classification_mobilnet.h5")
        )

    @patch_train_model_all
    def test_train_model_exception(
        self, mock_mlflow, mock_keras, mock_json_dump, mock_open
    ):
        # Prepare
        training_set = MagicMock()
        model_metadata = "model_metadata.json"
        model_output = "model_output/"
        image_size = (244, 244)
        dim = 3

        mock_run = MagicMock()
        mock_run.__enter__.return_value = mock_run
        mock_mlflow.start_run.return_value = mock_run
        mock_mlflow.active_run.return_value = mock_run

        _, label_batch = MagicMock(), MagicMock()
        training_set.next.return_value = _, label_batch

        mock_feature_extractor = MagicMock()
        mock_output = MagicMock()
        mock_feature_extractor.output = mock_output
        mock_keras.applications.MobileNet.return_value = mock_feature_extractor

        mock_average_pooling = MagicMock()
        mock_keras.layers.GlobalAveragePooling2D.return_value = mock_average_pooling

        mock_keras.Model.side_effect = Exception("Invalid data")

        # Act
        with self.assertRaises(Exception):
            train_model(training_set, model_metadata, model_output, image_size, dim)

        # Assert
        mock_keras.applications.MobileNet.assert_called_once_with(
            weights="imagenet", include_top=False, input_shape=((244, 244) + (3,))
        )
        mock_keras.layers.Dense.assert_called_once_with(
            label_batch.shape[1], activation="softmax"
        )
        mock_keras.layers.Dense.return_value.assert_called_once_with(
            mock_average_pooling()
        )
        mock_keras.Model.assert_called_once_with(
            inputs=mock_feature_extractor.input,
            outputs=mock_keras.layers.Dense.return_value(mock_average_pooling()),
        )
        mock_keras.Model.return_value.compile.assert_not_called()
        mock_keras.Model.return_value.fit_generator.assert_not_called()

        mock_json_dump.assert_not_called()
        mock_keras.Model.return_value.save.assert_not_called()
