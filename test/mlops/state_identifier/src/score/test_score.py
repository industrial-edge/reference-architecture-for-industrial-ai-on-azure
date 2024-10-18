# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression

from mlops.state_identifier.src.score.score import dunn_index, main, write_results


class TestScore(TestCase):
    _mock_input_data = np.array(
        [[1, 1, 0, 0], [1, 2, 0, 0], [0, 0, 6, 7], [0, 0, 3, 3]]
    )
    _labels = np.array([0, 0, 1, 1])
    _mock_score_results_dict = {"silhouette": 0.5, "dunn_index": 2, "inertia": 100}

    def test_dunn_index_value_correctly_computed(self):
        dunn_index_value = dunn_index(self._mock_input_data, self._labels)

        dunn_index_value_3_decimals = "%.3f" % (dunn_index_value)

        self.assertEqual(dunn_index_value_3_decimals, str(0.894))

    @patch("mlops.state_identifier.src.score.score.mlflow")
    @patch("mlops.state_identifier.src.score.score.json.dump")
    @patch("mlops.state_identifier.src.score.score.silhouette_score")
    @patch("mlops.state_identifier.src.score.score.dunn_index")
    def test_write_results_to_json_and_logged_to_mlflow(
        self,
        mock_dunn_index,
        mock_silhouette_score,
        mock_json_dump,
        mock_mlflow,
    ):
        mock_model = MagicMock()
        mock_model.inertia_ = 100
        mock_silhouette_score.return_value = 0.5
        mock_dunn_index.return_value = 2
        mock_model.labels_ = self._labels

        with tempfile.TemporaryDirectory() as mock_score_report:
            write_results(mock_model, self._mock_input_data, mock_score_report)

        mock_json_dump_call_args = mock_json_dump.call_args_list[0][0]

        mock_silhouette_score.assert_called_with(self._mock_input_data, self._labels)
        mock_dunn_index.assert_called_with(self._mock_input_data, self._labels)

        # Ensure that the metrics are logged correctly
        mock_mlflow.log_metric.assert_any_call("silhouette", 0.5)
        mock_mlflow.log_metric.assert_any_call("dunn_index", 2)
        mock_mlflow.log_metric.assert_any_call("inertia", 100)

        # Ensure that json.dump is called with the correct arguments
        mock_json_dump.assert_called_once()
        self.assertEquals(mock_json_dump_call_args[0], self._mock_score_results_dict)
        self.assertEquals(
            Path(mock_json_dump_call_args[1].name),
            Path(f"{mock_score_report}/score.txt"),
        )

    @patch("mlops.state_identifier.src.score.score.pickle.load")
    @patch("mlops.state_identifier.src.score.score.pd.read_csv")
    @patch("mlops.state_identifier.src.score.score.write_results")
    @patch("mlops.state_identifier.src.score.score.open")
    def test_main_correct_calls_to_write_results_and_pickle(
        self, mock_open, mock_write_results, mock_read_csv, mock_pickle
    ):
        mock_open.return_value = "sample_model"
        mock_read_csv.return_value = pd.DataFrame(self._mock_input_data)
        mock_pickle.return_value = "mocked_model"

        main("mock_prep_data_path", "mock_model", "mock_score_report")

        # Ensure that write_results is called with the correct arguments
        mock_write_results_call_args = mock_write_results.call_args_list[0][0]
        (
            call_arg_1_write_results,
            call_arg_2_write_results,
            call_arg_3_write_results,
        ) = mock_write_results_call_args

        self.assertEqual(call_arg_1_write_results, "mocked_model")
        np.testing.assert_array_equal(call_arg_2_write_results, self._mock_input_data)
        self.assertEqual(call_arg_3_write_results, "mock_score_report")

        mock_read_csv.assert_called_with(
            Path("mock_prep_data_path", "transformed_data.csv")
        )
        mock_open.assert_called_with(Path("mock_model", "model.sav"), "rb")
        mock_pickle.assert_called_with("sample_model")

    def test_write_results_fail_untrained_kmeans(self):
        mock_model = KMeans(n_clusters=3, random_state=0)

        with tempfile.TemporaryDirectory() as mock_score_report:
            with self.assertRaises(AttributeError) as context:
                write_results(mock_model, self._mock_input_data, mock_score_report)

        expected_error = "'KMeans' object has no attribute 'labels_'"
        self.assertEqual(expected_error, context.exception.args[0])

    def test_write_results_fail_trained_linear_regression(self):
        # Check if the code will fail when using a trained model of
        # different type. Chose linear regression arbitrarily.
        mock_model = LinearRegression()
        mock_targets = np.array([1, 2, 3, 4])
        mock_model.fit(self._mock_input_data, mock_targets)

        with tempfile.TemporaryDirectory() as mock_score_report:
            with self.assertRaises(AttributeError) as context:
                write_results(mock_model, self._mock_input_data, mock_score_report)

        expected_error = "'LinearRegression' object has no attribute 'labels_'"
        self.assertEqual(expected_error, context.exception.args[0])

    def test_main_fail_read_csv_no_file(self):

        with self.assertRaises(FileNotFoundError) as context:
            main("mock_prep_data_path", "mock_model", "mock_score_report")

        expected_error = "No such file or directory"
        self.assertEqual(expected_error, context.exception.args[1])

    @patch("mlops.state_identifier.src.score.score.pd.read_csv")
    def test_main_fail_open_no_file(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(self._mock_input_data)

        with self.assertRaises(FileNotFoundError) as context:
            main("mock_prep_data_path", "mock_model", "mock_score_report")

        expected_error = "No such file or directory"
        self.assertEqual(expected_error, context.exception.args[1])
