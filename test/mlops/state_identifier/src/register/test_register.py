from unittest import TestCase
from unittest.mock import ANY
from unittest.mock import patch, MagicMock

from mlops.state_identifier.src.register.register import main


@patch("json.dump")
@patch("json.load")
@patch("pickle.load")
@patch("mlops.state_identifier.src.register.register.open", new_callable=MagicMock)
@patch("mlops.state_identifier.src.register.register.load")
@patch("mlops.state_identifier.src.register.register.mlflow")
@patch("os.environ")
class TestRegistration(TestCase):
    _mock_score_data = {"silhouette": 0.4, "dunn_index": 2, "inertia": 80}

    _mock_file_paths = {
        "score_report": "/path/to/score/report",
        "preparation_path": "/path/to/preparation",
        "mlops_results_path": "/path/to/mlops_results",
    }

    _mock_os_env_values = {"AZUREML_ROOT_RUN_ID": "root-id"}

    def test_main_register_model_success(
        self,
        mock_os_env: MagicMock,
        mock_mlflow: MagicMock,
        mock_joblib_load: MagicMock,
        mock_open: MagicMock,
        mock_pickle_load: MagicMock,
        mock_json_load: MagicMock,
        mock_json_dump: MagicMock,
    ):
        # Arrange
        mock_score_file = MagicMock()
        mock_model = MagicMock()
        mock_data_transformation_pipeline = MagicMock()
        mock_run = MagicMock()
        mock_model_version = MagicMock()
        mlflow_client_mock = MagicMock()

        mock_os_env.return_value = self._mock_os_env_values
        mock_open.return_value.__enter__.return_value = mock_score_file
        mock_json_load.return_value = self._mock_score_data
        mock_pickle_load.return_value = mock_model
        mock_joblib_load.return_value = mock_data_transformation_pipeline
        mock_run.info.run_id = "run_id"
        mock_model_version.version = "version_1"
        mock_mlflow.start_run.return_value = mock_run
        mock_mlflow.active_run.return_value = mock_run
        mock_mlflow.register_model.return_value = mock_model_version
        mock_mlflow.MlflowClient.return_value = mlflow_client_mock

        # Act
        main(
            "model_name",
            self._mock_file_paths["score_report"],
            "build_reference",
            self._mock_file_paths["preparation_path"],
            mock_model,
            self._mock_file_paths["mlops_results_path"],
        )

        # Assert
        log_model_args = mock_mlflow.sklearn.log_model.call_args_list[0][0]
        (pipeline_arg, model_name_arg) = log_model_args
        mock_mlflow.sklearn.log_model.assert_called_once()
        self.assertEqual(model_name_arg, "model_name")
        self.assertEqual(
            pipeline_arg.named_steps["preprocessing"], mock_data_transformation_pipeline
        )
        self.assertEqual(pipeline_arg.named_steps["clustering"], mock_model)
        mock_mlflow.register_model.assert_called_once_with(
            "runs:/run_id/model_name", "model_name"
        )
        mlflow_client_mock.set_model_version_tag.assert_any_call(
            name="model_name",
            version="version_1",
            key="silhouette",
            value=self._mock_score_data["silhouette"],
        )
        mlflow_client_mock.set_model_version_tag.assert_any_call(
            name="model_name",
            version="version_1",
            key="dunn_index",
            value=self._mock_score_data["dunn_index"],
        )
        mlflow_client_mock.set_model_version_tag.assert_any_call(
            name="model_name",
            version="version_1",
            key="inertia",
            value=self._mock_score_data["inertia"],
        )
        mlflow_client_mock.set_model_version_tag.assert_any_call(
            name="model_name",
            version="version_1",
            key="build_id",
            value="build_reference",
        )
        mock_json_dump.assert_called_once_with(
            {
                "model_name": "model_name",
                "model_version": "version_1",
            },
            ANY,
            indent=ANY,
        )

    def test_main_register_model_with_exception(
        self,
        mock_os_env: MagicMock,
        mock_mlflow: MagicMock,
        mock_joblib_load: MagicMock,
        mock_open: MagicMock,
        mock_pickle_load: MagicMock,
        mock_json_load: MagicMock,
        mock_json_dump: MagicMock,
    ):
        with self.assertRaises(Exception):
            # Arrange
            mock_model = MagicMock()
            mock_data_transformation_pipeline = MagicMock()
            mock_run = MagicMock()
            mock_model_version = MagicMock()
            mlflow_client_mock = MagicMock()

            mock_os_env.return_value = self._mock_os_env_values
            mock_open.side_effect = Exception("Test")
            mock_json_load.return_value = self._mock_score_data
            mock_pickle_load.return_value = mock_model
            mock_joblib_load.return_value = mock_data_transformation_pipeline
            mock_run.info.run_id = "run_id"
            mock_model_version.version = "version_1"
            mock_mlflow.start_run.return_value = mock_run
            mock_mlflow.active_run.return_value = mock_run
            mock_mlflow.register_model.return_value = mock_model_version
            mock_mlflow.MlflowClient.return_value = mlflow_client_mock

            # Act
            main(
                "model_name",
                self._mock_file_paths["score_report"],
                "build_reference",
                self._mock_file_paths["preparation_path"],
                mock_model,
                self._mock_file_paths["mlops_results_path"],
            )

            # Assert
            mock_mlflow.sklearn.log_model.assert_called_once()
            mock_mlflow.register_model.assert_called_once_with(
                "runs:/run_id/model_name", "model_name"
            )
            mock_json_dump.assert_not_called()
