from unittest import TestCase
from unittest.mock import patch, MagicMock

from azure.core.exceptions import ResourceExistsError

from mlops.common.src.package_registration import main


class MockZipfile:
    def __init__(self):  # ["pipeline_config.yml"]
        self.files = [MagicMock(filename='"pipeline_config.yml"')]

    def __iter__(self):
        return iter(self.files)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

    def infolist(self):
        return self.files

    def extractall(self):
        return True


@patch("yaml.safe_load")
@patch("mlops.common.src.package_registration.Path")
@patch("mlops.common.src.package_registration.list")
@patch("mlops.common.src.package_registration.open")
@patch("mlops.common.src.package_registration.zipfile")
@patch("mlops.common.src.package_registration.shutil")
@patch("mlops.common.src.package_registration.deployment")
@patch("json.dump")
@patch("mlops.common.src.package_registration.MLClient")
@patch("mlops.common.src.package_registration.register_package")
class TestPackageRegistration(TestCase):
    _args = {
        "resource_group_name": "any_resource_group",
        "workspace_name": "any_workspace",
        "subscription_id": "any_subscription",
        "validation_results": "/path/to/validation/results",
        "package_path": "/path/to/package/origin",
        "registry_results": "/path/to/registry/results",
    }

    def test_main_package_registration_success(
        self,
        mock_yaml_load: MagicMock,
        mock_path: MagicMock,
        mock_list: MagicMock,
        mock_open: MagicMock,
        mock_zipfile: MagicMock,
        mock_shutil: MagicMock,
        mock_deployment: MagicMock,
        mock_json_dump: MagicMock,
        mock_ml_client: MagicMock,
        mock_register_package: MagicMock,
    ):
        mock_ml_client_object = MagicMock()
        mock_ml_client.return_value = mock_ml_client_object

        mock_path.resolve.return_value = "."

        mock_zipfile.ZipFile.return_value = MockZipfile()
        mock_shutil.copy.return_value = self._args["package_path"]
        mock_deployment.convert_package.return_value = self._args["package_path"]

        mock_list.return_value = ["./pipeline-config.yml"]

        mock_config_yaml = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_config_yaml

        mock_yaml_load.return_value = {
            "dataFlowPipelineInfo": {
                "projectName": "projectName",
                "dataFlowPipelineVersion": "dataFlowPipelineVersion",
                "packageId": "packageId",
            }
        }

        main(**self._args)

        mock_json_dump.assert_called_once()
        mock_register_package.assert_called_once()

    def test_main_package_registration_fails(
        self,
        mock_yaml_load: MagicMock,
        mock_path: MagicMock,
        mock_list: MagicMock,
        mock_open: MagicMock,
        mock_zipfile: MagicMock,
        mock_shutil: MagicMock,
        mock_deployment: MagicMock,
        mock_json_dump: MagicMock,
        mock_ml_client: MagicMock,
        mock_register_package: MagicMock,
    ):
        mock_ml_client_object = MagicMock()
        mock_ml_client.return_value = mock_ml_client_object

        mock_path.resolve.return_value = "."

        mock_zipfile.ZipFile.return_value = MockZipfile()
        mock_shutil.copy.return_value = self._args["package_path"]
        mock_deployment.convert_package.return_value = self._args["package_path"]

        mock_list.return_value = ["./pipeline-config.yml"]

        mock_config_yaml = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_config_yaml

        mock_yaml_load.return_value = {
            "dataFlowPipelineInfo": {
                "projectName": "projectName",
                "dataFlowPipelineVersion": "dataFlowPipelineVersion",
                "packageId": "packageId",
            }
        }

        mock_register_package.side_effect = ResourceExistsError

        main(**self._args)

        mock_json_dump.assert_called_once()
        mock_register_package.assert_not_called()
