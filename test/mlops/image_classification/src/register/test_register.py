from logging import getLogger
from unittest import TestCase
from unittest.mock import patch, MagicMock

from mlops.image_classification.src.register.register import main

logger = getLogger()


@patch("json.load")
@patch("mlops.image_classification.src.register.register.open", new_callable=MagicMock)
@patch("mlops.image_classification.src.register.register.mlflow")
class TestRegistration(TestCase):
    _mock_score_data = {
        "clf_report": {
            "accuracy": 0.365,
            "macro avg": {
                "precision": 0.368,
                "recall": 0.400,
                "f1-score": 0.374,
                "support": 266,
            },
        }
    }

    _mock_model_metadata = {"run_uri": "run_uri"}

    _mock_file_paths = {
        "score_report": "/path/to/score/report",
    }

    def test_main_register_model_success(
        self,
        mock_mlflow: MagicMock,
        mock_open: MagicMock,
        mock_json_load: MagicMock,
    ):
        # Arrange
        mock_file = MagicMock()
        mock_model_metadata = MagicMock()
        mock_model_version = MagicMock()
        mlflow_client_mock = MagicMock()

        mock_open.return_value.__enter__.return_value = mock_file
        mock_json_load.side_effect = [self._mock_model_metadata, self._mock_score_data]
        mock_model_version.version = "version_1"
        mock_mlflow.register_model.return_value = mock_model_version
        mock_mlflow.MlflowClient.return_value = mlflow_client_mock

        # Act
        main(
            mock_model_metadata,
            "model_name",
            self._mock_file_paths["score_report"],
            "build_reference",
            "mlops_results_path",
        )

        # Assert
        mock_mlflow.register_model.assert_called_once_with("run_uri", "model_name")
        mlflow_client_mock.set_model_version_tag.assert_any_call(
            name="model_name",
            version="version_1",
            key="accuracy",
            value=self._mock_score_data["clf_report"]["accuracy"],
        )

        macro_avg = self._mock_score_data["clf_report"]["macro avg"]

        mlflow_client_mock.set_model_version_tag.assert_any_call(
            name="model_name",
            version="version_1",
            key="avg_precision",
            value=macro_avg["precision"],
        )
        mlflow_client_mock.set_model_version_tag.assert_any_call(
            name="model_name",
            version="version_1",
            key="avg_recall",
            value=macro_avg["recall"],
        )
        mlflow_client_mock.set_model_version_tag.assert_any_call(
            name="model_name",
            version="version_1",
            key="avg_f1_score",
            value=macro_avg["f1-score"],
        )
        mlflow_client_mock.set_model_version_tag.assert_any_call(
            name="model_name",
            version="version_1",
            key="build_id",
            value="build_reference",
        )

    def test_main_register_model_with_exception(
        self,
        mock_mlflow: MagicMock,
        mock_open: MagicMock,
        mock_json_load: MagicMock,
    ):
        # Arrange
        mock_model_metadata = MagicMock()
        mock_file = MagicMock()
        mock_model_version = MagicMock()
        mlflow_client_mock = MagicMock()

        exception = Exception("Test")

        mock_open.side_effect = exception
        mock_open.return_value.__enter__.return_value = mock_file
        mock_json_load.return_value = self._mock_score_data
        mock_model_version.version = "version_1"
        mock_mlflow.register_model.return_value = mock_model_version
        mock_mlflow.MlflowClient.return_value = mlflow_client_mock

        # Act
        with self.assertRaises(Exception):
            main(
                mock_model_metadata,
                "model_name",
                self._mock_file_paths["score_report"],
                "build_reference",
                "mlops_results_path",
            )

        # Assert
        mock_open.assert_called_with(mock_model_metadata)
