from functools import wraps
from unittest import TestCase
from unittest.mock import patch, MagicMock

import numpy as np
import pytest

from mlops.state_identifier.src.train.train import train_model, main


def patch_all(f):
    """
    Patches all of the library calls that are required to
    make the train model function work.
    """

    @patch("mlops.state_identifier.src.train.train.mlflow")
    @patch("mlops.state_identifier.src.train.train.KMeans")
    @patch("mlops.state_identifier.src.train.train.open")
    @patch("mlops.state_identifier.src.train.train.pickle.dump")
    @wraps(f)
    def functor(*args, **kwargs):
        return f(*args, **kwargs)

    return functor


class TestTrain(TestCase):
    _args = {
        "training_data": "./path/to/training_data",
        "model_output": "./path/to/model_output",
    }
    _mock_model_output = "./path/to/model_output"

    @patch("mlops.state_identifier.src.train.train.pd.read_csv")
    @patch("mlops.state_identifier.src.train.train.train_model")
    @pytest.mark.integtest
    def test_main_success(self, mock_train_model, mock_read_csv):
        main(**self._args)

        mock_read_csv.assert_called_once()
        mock_train_model.assert_called_once()

    @patch_all
    def test_train_model(self, mock_pickle_dump, mock_open, mock_kmeans, mock_mlflow):
        mock_run_id = MagicMock()
        mock_model = MagicMock()
        mock_run = MagicMock()
        mock_file_object = MagicMock()
        mock_input_data = np.array(
            [[0, 1, 2, 3], [3, 2, 1, 0], [4, 5, 6, 7], [3, 3, 3, 3]]
        )

        mock_run.info.run_id = mock_run_id
        mock_run.__enter__.return_value = mock_run
        mock_kmeans.return_value = mock_model
        mock_mlflow.active_run.return_value = mock_run
        mock_open.return_value.__enter__.return_value = mock_file_object

        train_model(mock_input_data, self._mock_model_output)

        # Assertions for mock calls
        mock_mlflow.autolog.assert_called_once()
        mock_kmeans.assert_called_once_with(n_clusters=3, random_state=0)
        mock_kmeans.return_value.fit.assert_called_once_with(mock_input_data)
        mock_pickle_dump.assert_called_once()
        mock_open.assert_called_once()

        mock_pickle_dump.assert_called_once_with(mock_model, mock_open.return_value)

    @patch_all
    def test_train_model_exception(
        self, mock_pickle_dump, mock_open, mock_kmeans, mock_mlflow
    ):
        mock_run_id = MagicMock()
        mock_model = MagicMock()
        mock_model_info = MagicMock()
        mock_run = MagicMock()

        mock_run.info.run_id = mock_run_id
        mock_run.__enter__.return_value = mock_run
        mock_mlflow.active_run.return_value = mock_model_info
        mock_kmeans.return_value = mock_model

        mock_train_data = np.array([[1, 2], [3, 4]])

        mock_model.fit.side_effect = Exception("Invalid data")

        with self.assertRaises(Exception):
            train_model(mock_train_data, self._mock_model_output)

        # Assertions
        mock_model.fit.assert_called_once_with(mock_train_data)
        mock_pickle_dump.assert_not_called()
        mock_open.assert_not_called()
