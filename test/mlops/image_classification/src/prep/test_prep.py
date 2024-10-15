import tensorflow as tf
import numpy as np
import os
import pytest
from unittest import TestCase, mock
from unittest.mock import patch, MagicMock
from functools import wraps
from PIL import Image

from mlops.image_classification.src.prep.prep import main, data_prep, save_to_dir


def patch_all_data_prep(f):
    """
    Patches all of the library calls that are required to
    make the data preparation function work.
    """

    @patch("mlops.image_classification.src.prep.prep.save_to_dir")
    @patch("mlops.image_classification.src.prep.prep.Path")
    @patch(
        "mlops.image_classification.src.prep.prep.tf.keras.preprocessing.image.ImageDataGenerator"
    )
    @patch(
        "mlops.image_classification.src.prep.prep.tf.keras.preprocessing.image.DirectoryIterator"
    )
    @wraps(f)
    def functor(*args, **kwargs):
        return f(*args, **kwargs)

    return functor


class TestPrep(TestCase):
    _args = {
        "raw_data": "./path/to/raw_data",
        "training_data": "./path/to/training_output",
        "test_data": "./path/to/test_data",
    }

    @patch("mlops.image_classification.src.prep.prep.data_prep")
    @pytest.mark.integtest
    def test_main_success(self, mock_data_prep):
        main(**self._args)
        mock_data_prep.assert_called_once()

    @patch_all_data_prep
    def test_data_prep_success(
        self,
        mock_directory_iterator,
        mock_image_data_generator,
        mock_pathlib,
        mock_save,
    ):
        # Prepare
        mock_path_instance_object = MagicMock()
        mock_path_instance_object.iterdir.return_value = [
            MagicMock(name="dir1", is_dir=MagicMock(return_value=True)),
            MagicMock(name="dir2", is_dir=MagicMock(return_value=True)),
        ]
        mock_pathlib.return_value = mock_path_instance_object

        mock_training_set = mock_directory_iterator.return_value
        mock_test_set = mock_directory_iterator.return_value
        mock_image_data_generator.return_value.flow_from_directory.side_effect = [
            mock_training_set,
            mock_test_set,
        ]

        raw_data_path = "dir1"
        training_data = "/path/to/training_data"
        test_data = "/path/to/test_data"

        # Act
        data_prep(raw_data_path, training_data, test_data)

        # Assert
        mock_image_data_generator.assert_called_with(
            rescale=1 / 255, validation_split=0.2
        )
        self.assertEqual(
            mock_image_data_generator.return_value.flow_from_directory.call_count, 2
        )
        self.assertEqual(mock_save.call_count, 2)

    @patch_all_data_prep
    def test_data_prep_exception(
        self,
        mock_directory_iterator,
        mock_image_data_generator,
        mock_pathlib,
        mock_save,
    ):
        # Prepare
        mock_path_instance_object = MagicMock()
        mock_path_instance_object.iterdir.return_value = [
            MagicMock(name="dir1", is_dir=MagicMock(return_value=True)),
            MagicMock(name="dir2", is_dir=MagicMock(return_value=True)),
        ]
        mock_pathlib.return_value = mock_path_instance_object
        mock_image_data_generator.side_effect = Exception("Invalid data")

        raw_data_path = "dir1"
        training_data = "/path/to/training_data"
        test_data = "/path/to/test_data"

        # Act
        with self.assertRaises(Exception):
            data_prep(raw_data_path, training_data, test_data)

            # Assert
            mock_image_data_generator.assert_called_with(
                rescale=1 / 255, validation_split=0.2
            )
            mock_image_data_generator.return_value.flow_from_directory.assert_not_called()
            mock_save.assert_not_called()

    @patch("mlops.image_classification.src.prep.prep.os.makedirs")
    @patch("mlops.image_classification.src.prep.prep.Image.fromarray")
    def test_save_to_dir(self, mock_fromarray, mock_makedirs):
        # Prepare
        mock_dataset = MagicMock(spec=tf.keras.preprocessing.image.DirectoryIterator)
        mock_dataset.__iter__.return_value = iter(
            [
                (np.array([[[0.1, 0.2, 0.3]]]), np.array([[1, 0]])),
                (np.array([[[0.4, 0.5, 0.6]]]), np.array([[0, 1]])),
            ]
        )
        mock_dataset.__len__.return_value = 2
        mock_pil_image = MagicMock(spec=Image.Image)
        mock_pil_image.save.return_value = None
        mock_fromarray.return_value = mock_pil_image

        save_dir = "/path/to/save_dir"
        class_labels = ["class1", "class2"]

        # Act
        save_to_dir(mock_dataset, save_dir, class_labels)

        # Assert
        expected_subdirs = [
            os.path.join(save_dir, class_labels[0]),
            os.path.join(save_dir, class_labels[1]),
        ]
        expected_image_paths = [
            os.path.join(expected_subdirs[0], "image_1_0.jpg"),
            os.path.join(expected_subdirs[1], "image_2_0.jpg"),
        ]

        mock_makedirs.assert_has_calls(
            [
                mock.call(expected_subdir, exist_ok=True)
                for expected_subdir in expected_subdirs
            ]
        )
        self.assertEqual(mock_makedirs.call_count, 2)
        self.assertEqual(mock_fromarray.call_count, 2)
        mock_pil_image.save.assert_has_calls(
            [
                mock.call(image_path, format="JPEG")
                for image_path in expected_image_paths
            ]
        )
        self.assertEqual(mock_pil_image.save.call_count, 2)
