# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

from unittest import TestCase

import numpy as np

from mlops.state_identifier.src.prep.preprocessing_utils import (
    FeatureTransformer,
    WindowTransformer,
    FillMissingValues,
    SumColumnsTransformer,
    positive_sum_of_changes,
    negative_sum_of_changes,
)


class TestPrep(TestCase):

    _mock_list = [[1], [None], [3]]
    _mock_array_windowing_one_variable = np.array(
        [[1], [2], [3], [4], [5], [6], [7], [8], [9]]
    )

    _mock_mixed_data_sum_of_changes = np.array([-100, 3, 4, -30])

    _mock_data_with_nan_sum_of_changes = np.array([-100, 3, 4, -30, np.NaN])

    _mock_array_three_variables = np.array(
        [
            [11, 12, 13],
            [21, 22, 23],
            [31, 32, 33],
            [41, 42, 43],
            [51, 52, 53],
            [61, 62, 63],
            [71, 72, 73],
            [81, 82, 83],
            [91, 92, 93],
        ]
    )

    def test_feature_transformer_correct_aggregation(self):

        feature_blocks = [
            (2, [np.mean, np.mean, np.mean]),
            (1, [np.min, np.max]),
        ]

        agg = FeatureTransformer(feature_blocks)

        assert len(agg.function_list) == 8
        for fn in agg.function_list:
            assert callable(fn)

        windowed_data = [
            # windowed data with 2 variables
            [  # variable 1
                [10, 20, 10, 20],  # window 1 with 4 data points
                [30, 40, 30, 40],  # window 2 with 4 data points
                [50, 60, 50, 60],  # window 3 with 4 data points
            ],
            [  # variable 2
                [70, 80, 70, 80],  # window 1 with 4 data points
                [80, 90, 80, 90],  # window 2 with 4 data points
                [10, 100, 10, 100],  # window 3 with 4 data points
            ],
        ]

        extracted = [
            [
                15.0,
                15.0,
                15.0,
                15.0,
                15.0,
                15.0,
                10.0,
                20.0,
                75.0,
                75.0,
                75.0,
                75.0,
                75.0,
                75.0,
                70.0,
                80.0,
            ],  # window 1
            [
                35.0,
                35.0,
                35.0,
                35.0,
                35.0,
                35.0,
                30.0,
                40.0,
                85.0,
                85.0,
                85.0,
                85.0,
                85.0,
                85.0,
                80.0,
                90.0,
            ],  # window 2
            [
                55.0,
                55.0,
                55.0,
                55.0,
                55.0,
                55.0,
                50.0,
                60.0,
                55.0,
                55.0,
                55.0,
                55.0,
                55.0,
                55.0,
                10.0,
                100.0,
            ],
        ]  # window 3

        result = agg.transform(windowed_data)

        np.testing.assert_array_equal(result, extracted)

    def test_window_transformer_with_one_variable_win3_nostep_correct_value(self):
        win3_nostep_transformed_array = WindowTransformer(3).transform(
            self._mock_array_windowing_one_variable
        )

        np.testing.assert_array_equal(
            win3_nostep_transformed_array, [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]]
        )

    def test_window_transformer_with_one_variable_win4_nostep_correct_value(self):
        win4_nostep_transformed_array = WindowTransformer(4).transform(
            self._mock_array_windowing_one_variable
        )

        np.testing.assert_array_equal(
            win4_nostep_transformed_array, [[[1, 2, 3, 4], [5, 6, 7, 8]]]
        )

    def test_window_transformer_with_one_var_win3_step3_equals_win3_step3_correct_value(
        self,
    ):
        win3_step3_transformed_array = WindowTransformer(3, 3).transform(
            self._mock_array_windowing_one_variable
        )
        win3_nostep_transformed_array = WindowTransformer(3).transform(
            self._mock_array_windowing_one_variable
        )

        np.testing.assert_array_equal(
            win3_step3_transformed_array, win3_nostep_transformed_array
        )

    def test_window_transformer_with_one_variable_win4_step3_correct_value(
        self,
    ):
        win4_step3_transformed_array = WindowTransformer(4, 3).transform(
            self._mock_array_windowing_one_variable
        )

        np.testing.assert_array_equal(
            win4_step3_transformed_array, [[[1, 2, 3, 4], [4, 5, 6, 7]]]
        )

    def test_window_transformer_win3_nostep_with_three_variables_correct_value(
        self,
    ):
        win3_nostep_transformed_array = WindowTransformer(3, None).transform(
            self._mock_array_three_variables
        )

        np.testing.assert_array_equal(
            win3_nostep_transformed_array,
            [
                [[11, 21, 31], [41, 51, 61], [71, 81, 91]],
                [[12, 22, 32], [42, 52, 62], [72, 82, 92]],
                [[13, 23, 33], [43, 53, 63], [73, 83, 93]],
            ],
        )

    def test_window_transformer_win4_nostep_with_three_variables_correct_value(self):
        win4_nostep_transformed_array = WindowTransformer(4, None).transform(
            self._mock_array_three_variables
        )
        np.testing.assert_array_equal(
            win4_nostep_transformed_array,
            [
                [[11, 21, 31, 41], [51, 61, 71, 81]],
                [[12, 22, 32, 42], [52, 62, 72, 82]],
                [[13, 23, 33, 43], [53, 63, 73, 83]],
            ],
        )

    def test_window_transformer_win3_step3_with_three_variables_correct_value(self):
        win3_step3_transformed_array = WindowTransformer(3, 3).transform(
            self._mock_array_three_variables
        )
        win3_nostep_transformed_array = WindowTransformer(3, None).transform(
            self._mock_array_three_variables
        )

        np.testing.assert_array_equal(
            win3_step3_transformed_array, win3_nostep_transformed_array
        )

    def test_window_transformer_win4_step3_with_three_variables_correct_value(self):
        win4_step3_transformed_array = WindowTransformer(4, 3).transform(
            self._mock_array_three_variables
        )

        np.testing.assert_array_equal(
            win4_step3_transformed_array,
            [
                [[11, 21, 31, 41], [41, 51, 61, 71]],
                [[12, 22, 32, 42], [42, 52, 62, 72]],
                [[13, 23, 33, 43], [43, 53, 63, 73]],
            ],
        )

    def test_fill_with_zeroes(self):
        fill_missing_object = FillMissingValues(0)

        result = fill_missing_object.transform(self._mock_list)

        np.testing.assert_array_equal(result, [[1], [0], [3]])

    def test_fill_missing_values_with_previous_non_nan_value(self):
        fill_missing_object = FillMissingValues("ffill")

        result = fill_missing_object.transform(self._mock_list)

        np.testing.assert_array_equal(result, [[1], [1], [3]])

    def test_fill_missing_values_with_next_non_nan_value(self):
        fill_missing_object = FillMissingValues("bfill")

        result = fill_missing_object.transform(self._mock_list)

        np.testing.assert_array_equal(result, [[1], [3], [3]])

    def test_fill_missing_values_with_previous_is_nan(self):
        fill_missing_object = FillMissingValues("ffill")

        _mock_array_prev_nan = [[None], [None], [3]]
        result = fill_missing_object.transform(_mock_array_prev_nan)

        np.testing.assert_array_equal(result, [[np.NaN], [np.NaN], [3]])

    def test_fill_missing_values_with_next_is_nan(self):
        fill_missing_object = FillMissingValues("bfill")

        _mock_array_next_nan = [[1], [None], [None]]
        result = fill_missing_object.transform(_mock_array_next_nan)

        np.testing.assert_array_equal(result, [[1], [np.NaN], [np.NaN]])

    def test_fill_2d_bext_and_prev(self):
        _mock_list_2d = [
            [1, 10, None, 1000],
            [2, None, None, None],
            [3, None, 300, 3000],
        ]
        _mock_list_ffill = [
            [1, 10, np.NaN, 1000],
            [2, 10, np.NaN, 1000],
            [3, 10, 300, 3000],
        ]
        _mock_list_bfill = [
            [1, 10, 300, 1000],
            [2, np.NaN, 300, 3000],
            [3, np.NaN, 300, 3000],
        ]

        filled_next = FillMissingValues("ffill").transform(_mock_list_2d)
        filled_previous = FillMissingValues("bfill").transform(_mock_list_2d)

        np.testing.assert_array_equal(filled_next, _mock_list_ffill)
        np.testing.assert_array_equal(filled_previous, _mock_list_bfill)

    def test_sum_columns_transformer_correct_sum_3_columns(self):
        _mock_array_3_cols = np.array(
            [
                [11, 12, 4],
                [21, 22, 4],
                [31, 32, 4],
            ]
        )

        sum_column_transformer = SumColumnsTransformer()

        result = sum_column_transformer.transform(_mock_array_3_cols)

        np.testing.assert_array_equal(result, [[27], [47], [67]])

    def test_sum_columns_transformer_result_4_columns_equals_3_columns(self):
        _mock_array_4_cols = np.array(
            [
                [11, 12, 4, 12],
                [21, 22, 4, 56],
                [31, 32, 4, 67],
            ]
        )

        sum_column_transformer = SumColumnsTransformer()

        result = sum_column_transformer.transform(_mock_array_4_cols)

        np.testing.assert_array_equal(result, [[27], [47], [67]])

    def test_sum_columns_transformer_correct_sum_3_columns_with_nan(self):

        _mock_array_3_cols_with_nan = np.array(
            [
                [11, np.NaN, 4],
                [21, 22, 4],
                [31, 32, 4],
            ]
        )

        sum_column_transformer = SumColumnsTransformer()

        result = sum_column_transformer.transform(_mock_array_3_cols_with_nan)

        np.testing.assert_array_equal(result, [[np.NaN], [47], [67]])

    def test_positive_sum_of_changes_correct_value(self):
        result = positive_sum_of_changes(self._mock_mixed_data_sum_of_changes)

        self.assertEqual(result, 104)

    def test_negative_sum_of_changes_correct_value(self):
        result = negative_sum_of_changes(self._mock_mixed_data_sum_of_changes)

        self.assertEqual(result, -34)

    def test_negative_sum_of_changes_with_nan(self):
        result = negative_sum_of_changes(self._mock_data_with_nan_sum_of_changes)

        np.testing.assert_equal(result, np.NaN)

    def test_positive_sum_of_changes_with_nan(self):
        result = positive_sum_of_changes(self._mock_data_with_nan_sum_of_changes)

        np.testing.assert_equal(result, np.NaN)
