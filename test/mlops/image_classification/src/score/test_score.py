import numpy as np
import os

from unittest import TestCase

from unittest.mock import patch, MagicMock
from functools import wraps
from pathlib import Path

import tempfile
import pandas as pd
from pandas.testing import assert_frame_equal
from numpy.testing import assert_array_equal

from mlops.image_classification.src.score.score import (
    main,
    encoded_predictions_for_entire_dataset,
    evaluate,
    write_results,
)


def patch_all_data_score(f):
    """
    Patches all of the library calls that are required to
    make the data preparation function work.
    """

    @patch(
        "mlops.image_classification.src.score.score.encoded_predictions_for_entire_dataset"
    )
    @patch("mlops.image_classification.src.score.score.Path")
    @patch("mlops.image_classification.src.score.score.write_results")
    @patch("mlops.image_classification.src.score.score.tf.keras.models.load_model")
    @wraps(f)
    def functor(*args, **kwargs):
        return f(*args, **kwargs)

    return functor


class TestScore(TestCase):
    _TEST_METRICS = {
        "clf_report": {
            "CLASS1": {
                "precision": 0.5,
                "recall": 1.0,
                "f1-score": 0.6666666666666666,
                "support": 2,
            },
            "CLASS2": {"precision": 0.0, "recall": 0.0, "f1-score": 0.0, "support": 2},
            "accuracy": 0.5,
            "macro avg": {
                "precision": 0.25,
                "recall": 0.5,
                "f1-score": 0.3333333333333333,
                "support": 4,
            },
            "weighted avg": {
                "precision": 0.25,
                "recall": 0.5,
                "f1-score": 0.3333333333333333,
                "support": 4,
            },
        },
        "confusion_m": {
            "CLASS1": {"CLASS1": 2, "CLASS2": 2},
            "CLASS2": {"CLASS1": 0, "CLASS2": 0},
        },
    }

    _target_test = [0, 1, 0, 1]
    _target_pred = [0, 0, 0, 0]
    _classes = ["CLASS1", "CLASS2"]

    _confusion_m_df_mock = pd.DataFrame(
        _TEST_METRICS["confusion_m"], index=_classes, columns=_classes
    )

    _mock_dataset = [
        (
            np.array([[0.1, 0.2, 0.3], [0.1, 0.8, 0.1]]),
            np.array([[1, 0, 0], [0, 1, 0]]),
        ),
        (
            np.array([[0.4, 0.5, 0.6], [0.3, 0.2, 0.5]]),
            np.array([[0, 1, 0], [0, 0, 1]]),
        ),
    ]

    _args = {
        "test_data": "mock_path",
        "model": "mock_model",
        "score_report": "mock_score_report",
        "image_width": 224,
        "image_height": 224,
    }

    def return_values_predict_mock(self):
        yield self._mock_dataset[0][0]
        yield self._mock_dataset[1][0]

    def return_values_predict_mock_nan(self):
        yield None

    @patch("mlops.image_classification.src.score.score.mlflow")
    def test_evaluate_success(self, mock_mlflow):
        _expected_mlflow_log_metric_calls = [
            ("CLASS1", 0),
            ("CLASS2", 1),
            ("accuracy", 0.5),
            ("macro avg", 2),
            ("weighted avg", 3),
        ]
        _expected_mlflow_log_metrics_calls = self._TEST_METRICS["clf_report"].copy()

        del _expected_mlflow_log_metrics_calls["accuracy"]

        _expected_mlflow_log_metrics_calls = list(
            _expected_mlflow_log_metrics_calls.values()
        )

        metrics, confusion_m_df, clf_report = evaluate(
            self._target_test, self._target_pred, self._classes
        )

        mlflow_log_metric_calls = sorted(
            [call_args[0] for call_args in mock_mlflow.log_metric.call_args_list]
        )

        mlflow_log_metrics_calls = [
            call_args[0][0] for call_args in mock_mlflow.log_metrics.call_args_list
        ]

        self.assertEqual(mlflow_log_metric_calls, _expected_mlflow_log_metric_calls)
        self.assertEqual(mlflow_log_metrics_calls, _expected_mlflow_log_metrics_calls)
        self.assertEqual(metrics, self._TEST_METRICS)
        self.assertEqual(clf_report, self._TEST_METRICS["clf_report"])
        assert_frame_equal(confusion_m_df, self._confusion_m_df_mock)

    def test_evaluate_length_mismatch(self):
        _target_pred_mismatch = self._target_pred.copy()
        _target_pred_mismatch.append(0)

        with self.assertRaises(ValueError) as context:
            evaluate(self._target_test, _target_pred_mismatch, self._classes)

        self.assertTrue(
            "Found input variables with inconsistent numbers of samples"
            in str(context.exception)
        )

    def test_evaluate_pred_nan(self):

        with self.assertRaises(ValueError) as context:
            evaluate(self._target_test, None, self._classes)

            expected_exception_message = "The 'y_pred' parameter of classification_report \
                                must be an array-like or a sparse matrix. Got None instead."
            self.assertEqual(expected_exception_message, str(context.exception))

    def test_evaluate_true_nan(self):

        with self.assertRaises(ValueError) as context:
            evaluate(None, self._target_pred, self._classes)

            expected_exception_message = "The 'y_true' parameter of classification_report \
                                must be an array-like or a sparse matrix. Got None instead."
            self.assertEqual(expected_exception_message, str(context.exception))

    def test_write_results_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            write_results(
                self._TEST_METRICS,
                self._confusion_m_df_mock,
                self._TEST_METRICS["clf_report"],
                output_folder=tmpdir,
            )
            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 3)
            self.assertEqual(
                sorted(files), sorted(["cfm.png", "clf_report.png", "metrics.json"])
            )

    def test_write_results_failure(self):
        mock_folder = "mock_folder"

        with self.assertRaises(FileNotFoundError) as context:
            write_results(
                self._TEST_METRICS,
                self._confusion_m_df_mock,
                self._TEST_METRICS["clf_report"],
                output_folder=mock_folder,
            )

        self.assertTrue(
            "No such file or directory: 'mock_folder/cfm.png'" in str(context.exception)
        )

    def test_encoded_predictions_for_entire_dataset_success(self):
        mock_dataset = MagicMock()
        mock_model = MagicMock()
        mock_model.predict.side_effect = self.return_values_predict_mock()
        mock_dataset.__iter__.return_value = iter(self._mock_dataset)
        mock_dataset.__len__.return_value = 2
        _expected_encoded_predictions = np.array([2, 1, 2, 2])
        _expected_encoded_labels = np.array([0, 1, 1, 2])

        encoded_predictions, encoded_labels = encoded_predictions_for_entire_dataset(
            mock_model, mock_dataset
        )

        self.assertEqual(mock_model.predict.call_count, 2)
        assert_array_equal(encoded_predictions, _expected_encoded_predictions)
        assert_array_equal(encoded_labels, _expected_encoded_labels)

    def test_encoded_predictions_for_entire_dataset_failure(self):
        mock_dataset = MagicMock()
        mock_model = MagicMock()
        mock_model.predict.side_effect = self.return_values_predict_mock_nan()
        mock_dataset.__iter__.return_value = iter([(None, None)])
        mock_dataset.__len__.return_value = 1

        with self.assertRaises(np.AxisError) as context:
            encoded_predictions_for_entire_dataset(mock_model, mock_dataset)

        self.assertTrue(
            "axis 1 is out of bounds for array of dimension 1" in str(context.exception)
        )

    @patch_all_data_score
    @patch(
        "mlops.image_classification.src.score.score.tf.keras.preprocessing.image.ImageDataGenerator"
    )
    @patch("mlops.image_classification.src.score.score.evaluate")
    def test_main_success(
        self,
        mock_evaluate,
        mock_tf_generator,
        mock_load_model,
        mock_write_results,
        mock_path,
        mock_encoded_predictions_for_entire_dataset,
    ):

        mock_path.iterdir.return_value = [
            MagicMock(name="dir1", is_dir=MagicMock(return_value=True)),
            MagicMock(name="dir2", is_dir=MagicMock(return_value=True)),
        ]

        mock_tf_generator.return_value = MagicMock(flow_from_directory=MagicMock())

        mock_load_model.return_value = "mock_model"

        mock_encoded_return_values = np.array([1, 2, 3, 4]), np.array([1, 2, 3, 4])
        mock_encoded_predictions_for_entire_dataset.return_value = (
            mock_encoded_return_values
        )

        mock_evaluate_return_values = "metrics", "clf_report", "confusion_m_df"
        mock_evaluate.return_value = mock_evaluate_return_values

        main(**self._args)

        mock_load_model.called_once_with(
            Path(self._args["model"]) / "classification_mobilnet.h5"
        )
        mock_encoded_predictions_for_entire_dataset.called_once_with(
            "mock_model", mock_tf_generator.return_value
        )
        mock_evaluate.called_once_with(
            mock_encoded_return_values, mock_tf_generator.return_value.class_indices
        )
        mock_write_results.called_once_with(
            mock_evaluate_return_values, self._args["score_report"]
        )

    @patch_all_data_score
    @patch("mlops.image_classification.src.score.score.evaluate")
    def test_main_failure_invalid_data(
        self,
        mock_evaluate,
        mock_load_model,
        mock_write_results,
        mock_path,
        mock_encoded_predictions_for_entire_dataset,
    ):

        mock_path.iterdir.return_value = [
            MagicMock(name="dir1", is_dir=MagicMock(return_value=True)),
            MagicMock(name="dir2", is_dir=MagicMock(return_value=True)),
        ]

        with self.assertRaises(FileNotFoundError) as context:
            main(**self._args)

        self.assertTrue(
            "No such file or directory: 'mock_path'" in str(context.exception)
        )
        mock_load_model.assert_not_called()
        mock_encoded_predictions_for_entire_dataset.assert_not_called()
        mock_evaluate.assert_not_called()
        mock_write_results.assert_not_called()

    @patch_all_data_score
    @patch(
        "mlops.image_classification.src.score.score.tf.keras.preprocessing.image.ImageDataGenerator"
    )
    # Added the patch here because the evaluate function what picking up calls
    # from other tests. This is a workaround to avoid that.
    @patch("mlops.image_classification.src.score.score.evaluate")
    def test_main_failure_invalid_model(
        self,
        mock_evaluate,
        mock_tf_generator,
        mock_load_model,
        mock_write_results,
        mock_path,
        mock_encoded_predictions_for_entire_dataset,
    ):

        mock_path.iterdir.return_value = [
            MagicMock(name="dir1", is_dir=MagicMock(return_value=True)),
            MagicMock(name="dir2", is_dir=MagicMock(return_value=True)),
        ]

        mock_load_model.side_effect = Exception("Wrong model provided")

        mock_tf_generator.return_value = MagicMock(flow_from_directory=MagicMock())

        with self.assertRaises(Exception) as context:
            main(**self._args)

        self.assertTrue("Wrong model provided" in str(context.exception))

        mock_encoded_predictions_for_entire_dataset.assert_not_called()
        # print(mock_evaluate.call_args_list)
        mock_evaluate.assert_not_called()
        mock_write_results.assert_not_called()
