from unittest import TestCase
from unittest.mock import patch, MagicMock

from mlops.common.src.package_validation import main


@patch("joblib.load")
@patch("mlops.common.src.package_validation.Path")
@patch("mlops.common.src.package_validation.LocalPipelineRunner")
class TestPackageValidation(TestCase):
    _args = {
        "payload_data": "/path/to/payload/data",
        "package_path": "/path/to/package/origin",
        "validation_results": "/path/to/validation/results",
    }

    def test_main_package_validation_success(
        self,
        mock_joblib_load: MagicMock,
        mock_path: MagicMock,
        mock_pipeline_runner: MagicMock,
    ):
        mock_joblib_load.return_value = [{"ph1": 1.0, "ph2": 1.0, "ph3": 1.0}]
        mock_path.resolve.return_value = "."

        main(**self._args)

        mock_pipeline_runner.assert_called_once()

    def test_main_package_validation_fails(
        self,
        mock_joblib_load: MagicMock,
        mock_path: MagicMock,
        mock_pipeline_runner: MagicMock,
    ):
        mock_joblib_load.return_value = [{"ph1": 1.0, "ph2": 1.0, "ph3": 1.0}]
        mock_path.resolve.return_value = "."

        mock_pipeline_runner.return_value.__enter__.side_effect = RuntimeError

        main(**self._args)

        mock_pipeline_runner.run_pipeline.assert_not_called()
