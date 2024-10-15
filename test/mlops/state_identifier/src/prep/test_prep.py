import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

from mlops.state_identifier.src.prep.prep import data_prep, main


class TestPrep(TestCase):
    _mock_input_data = pd.DataFrame(
        [[1, 1, 0], [1, 2, 0], [0, 0, 6], [0, 0, 3]], columns=["ph1", "ph2", "ph3"]
    )

    _mock_data_frame = pd.DataFrame(
        {
            "0": [0.0, 1.0],
            "1": [0.0, 1.0],
            "2": [0.0, 1.0],
            "3": [0.0, 1.0],
            "4": [0.0, 1.0],
            "5": [0.0, 1.0],
            "6": [0.0, 1.0],
            "7": [0.0, 1.0],
            "8": [0.0, 1.0],
            "9": [0.0, 1.0],
            "10": [1.0, 0.0],
            "11": [1.0, 0.0],
            "12": [0.0, 0.0],
            "13": [0.0, 0.0],
            "14": [0.0, 0.0],
        }
    )
    _expected_steps_names = [
        "fillmissing",
        "summarization",
        "windowing",
        "featurization",
        "scaling",
    ]

    @patch("mlops.state_identifier.src.prep.prep.joblib.dump")
    def test_data_prep_correct_transformation(self, mock_joblib_dump):
        with tempfile.TemporaryDirectory() as mock_data_path:
            _mock_prep_data_full_path = os.path.join(
                mock_data_path, "transformed_data.csv"
            )
            _mock_preparation_pipeline_path = Path(
                mock_data_path, "preparation_pipeline.joblib"
            )

            _mock_input_data_copy = self._mock_input_data.copy()

            data_prep(
                _mock_input_data_copy,
                mock_data_path,
                mock_data_path,
                window_size=2,
                window_step=2,
            )

            transformed_data = pd.read_csv(_mock_prep_data_full_path)

            joblib_dump_call_args = mock_joblib_dump.call_args_list[0][0]
            pipeline_dump_path = joblib_dump_call_args[1]
            pipeline_steps = joblib_dump_call_args[0].steps
            piepline_steps_names = [step[0] for step in pipeline_steps]

        mock_joblib_dump.called_once()

        assert_frame_equal(transformed_data, self._mock_data_frame)

        self.assertEqual(piepline_steps_names, self._expected_steps_names)
        self.assertEqual(pipeline_dump_path, _mock_preparation_pipeline_path)

    @patch("mlops.state_identifier.src.prep.prep.pd.read_parquet")
    @patch("mlops.state_identifier.src.prep.prep.data_prep")
    def test_main_success(self, mock_data_prep, mock_read_parquet):
        mock_read_parquet.return_value = self._mock_data_frame

        main("data_path", "prep_data_path", "prep_pipeline_path")

        main_call_args = mock_data_prep.call_args_list[0][0]
        called_dataframe = main_call_args[0]
        called_data_path = main_call_args[1]
        called_prep_data_path = main_call_args[2]

        mock_data_prep.called_once()

        assert_frame_equal(called_dataframe, self._mock_data_frame)
        self.assertEqual(called_data_path, "prep_data_path")
        self.assertEqual(called_prep_data_path, "prep_pipeline_path")

    def test_data_prep_failure_wrong_columns(self):
        _mock_input_data_one_less_column = self._mock_input_data.drop("ph2", axis=1)

        with self.assertRaises(Exception) as context:
            data_prep(
                _mock_input_data_one_less_column,
                "data_path",
                "prep_data_path",
            )

        expected_exception = "['ph2'] not in index"
        self.assertEqual(expected_exception, context.exception.args[0])

    def test_data_prep_failure_wrong_format(self):
        # Needed because changes are made in-place to the dataframe
        _mock_input_data_string_row = self._mock_input_data.copy()
        _mock_input_data_string_row.loc[4] = ["a", "b", "c"]

        with self.assertRaises(Exception) as context:
            data_prep(
                _mock_input_data_string_row,
                "data_path",
                "prep_data_path",
                window_size=1,
                window_step=1,
            )

        expected_exception = "invalid literal for int() with base 10: 'abc'"
        self.assertEqual(expected_exception, context.exception.args[0])

    def test_data_prep_failure_window_too_big(self):
        # Needed because changes are made in-place to the dataframe
        _mock_input_data_copy = self._mock_input_data.copy()

        with self.assertRaises(Exception) as context:
            data_prep(
                _mock_input_data_copy,
                "data_path",
                "prep_data_path",
                window_size=300,
                window_step=300,
            )

        expected_exception = (
            "Cannot apply_along_axis when any iteration dimensions are 0"
        )
        self.assertEqual(expected_exception, context.exception.args[0])
