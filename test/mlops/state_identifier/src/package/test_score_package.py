# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import pandas as pd
import numpy as np
from unittest import TestCase
from unittest.mock import patch, MagicMock
from io import StringIO

from mlops.state_identifier.src.package.score_package import main


class TestScore(TestCase):
    mock_csv_string = """prediction,ph1,ph2,ph3
        0,{"value": 0.9653744591191317},{"value": 0.9103093273310903},{"value": 0.9160740737383725}
        1,{"value": 0.8337116571601987},{"value": 0.2910117797976617},{"value": 0.4643202400319436}
        1,{"value": 0.017005223211057907},{"value": 0.03912395364098775},{"value": 0.018224047592233172}
        """

    @patch("mlops.state_identifier.src.package.score_package.pd.read_csv")
    @patch("mlops.state_identifier.src.package.score_package.silhouette_score")
    @patch("mlops.state_identifier.src.package.score_package.dunn_index")
    @patch("mlops.state_identifier.src.package.score_package.json.dump")
    @patch("mlops.state_identifier.src.package.score_package.open")
    def test_main_success(
        self,
        mock_open,
        mock_json_dump,
        mock_dunn_index,
        mock_silhouette_score,
        mock_read_csv,
    ):
        mock_validation_df = pd.read_csv(StringIO(self.mock_csv_string))
        mock_prep_data_df = MagicMock(spec=pd.DataFrame)
        mock_prep_data_df.values = np.array(
            [[1, 1, 0, 0], [1, 2, 0, 0], [0, 0, 6, 7], [0, 0, 3, 3]]
        )
        mock_read_csv.side_effect = [mock_validation_df, mock_prep_data_df]

        mock_silhouette_score.return_value = 0.5
        mock_dunn_index.return_value = 2
        mock_file_object = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file_object

        main("test_validation_file.csv", "mock_prep_data_path", "mock_metrics_results")

        mock_dunn_index.assert_called_once()
        mock_silhouette_score.assert_called_once()
        mock_json_dump.assert_called_once()
