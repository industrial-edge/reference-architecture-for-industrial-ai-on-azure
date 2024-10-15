# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

import pandas as pd

from mlops.image_classification.src.package.score_package import main


class TestScorePackage(TestCase):
    _args = {
        "subscription_id": "subscription_id",
        "resource_group_name": "resource_group_name",
        "workspace_name": "workspace_name",
        "asset_name": "mock_name",
        "asset_version": "mock_version",
    }

    @patch("mlops.image_classification.src.package.score_package.MLClient")
    @patch("mlops.image_classification.src.package.score_package.pd.read_csv")
    @patch("mlops.image_classification.src.package.score_package.json.dump")
    def test_main_success(self, mock_json_dump, mock_read_csv, mock_ml_client):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            _classes = ["class1", "class2"]

            os.mkdir(f"{temp_dir_name}/{_classes[0]}")
            open(f"{temp_dir_name}/{_classes[0]}/1.jpg", "w").close()
            os.mkdir(f"{temp_dir_name}/{_classes[1]}")
            open(f"{temp_dir_name}/{_classes[1]}/2.jpg", "w").close()

            _validation_results_data = [
                ["prediction", "probability"],
                ["0", 1],
                ["1", 1],
            ]
            _validation_results_data_df = pd.DataFrame(
                data=_validation_results_data[1:], columns=_validation_results_data[0]
            )
            _validation_results = f"{temp_dir_name}/validation_results.csv"
            _validation_results_data_df.to_csv(_validation_results, index=False)

            self._args["validation_results"] = _validation_results
            self._args["metrics_results"] = f"{temp_dir_name}/metrics_results.json"
            self._args["raw_data"] = temp_dir_name

            mock_ml_client.return_value.data.get.return_value.tags = {
                class_name: i for i, class_name in enumerate(sorted(_classes))
            }

            mock_read_csv.return_value = _validation_results_data_df

            _metrics_to_tag = {
                "accuracy_validation": 1.0,
                "avg_precision_validation": 1.0,
                "avg_recall_validation": 1.0,
                "avg_f1_score_validation": 1.0,
            }

            main(**self._args)

            self.assertEqual(mock_read_csv.call_count, 1)
            mock_read_csv.assert_called_with(_validation_results)
            mock_ml_client.return_value.data.get.assert_called_once_with(
                name=self._args["asset_name"], version=self._args["asset_version"]
            )
            self.assertEqual(mock_json_dump.call_args_list[0][0][0], _metrics_to_tag)

    def test_main_failure_wrong_classes(self):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            open(f"{temp_dir_name}/1.jpg", "w").close()
            open(f"{temp_dir_name}/2.jpg", "w").close()

            self._args["validation_results"] = "mock"
            self._args["metrics_results"] = f"{temp_dir_name}/metrics_results.json"
            self._args["raw_data"] = temp_dir_name

            with self.assertRaises(ValueError):
                main(**self._args)
