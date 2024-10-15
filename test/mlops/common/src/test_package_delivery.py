# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import copy
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import ANY, patch, MagicMock

from mlops.common.src.package_delivery import main


class TestPackageDelivery(TestCase):
    _args = {
        "keyvault_name": "any_keyvault",
        "iot_hub_connection_string_secret_name": "iot_hub_secret_name",
        "event_hub_connection_string_secret_name": "event_hub_secret_name",
        "device_id": "any_device_id",
        "edge_package_name": "any_package_name",
        "edge_package_version": "123",
        "deploy_environment": "dev",
    }

    @patch("mlops.common.src.package_delivery.ModelManager")
    @patch("mlops.common.src.package_delivery.MLClient")
    @patch("mlops.common.src.package_delivery.SecretClient")
    @patch("mlops.common.src.package_delivery.ChainedTokenCredential")
    def test_main_success(
        self, mock_credential, mock_secret_client, mock_ml_client, mock_model_manager
    ):
        # GIVEN
        iot_hub_secret = "secret1"
        event_hub_secret = "secret2"
        mock_secret_client_object = MagicMock()
        mock_secret_client_object.get_secret.side_effect = {
            self._args["iot_hub_connection_string_secret_name"]: SimpleNamespace(
                value=iot_hub_secret
            ),
            self._args["event_hub_connection_string_secret_name"]: SimpleNamespace(
                value=event_hub_secret
            ),
        }.get
        mock_secret_client.return_value = mock_secret_client_object

        mock_datastore_name = "any_datastore_name"
        mock_blob_name = "any_blob_name"
        mock_datastore = MagicMock()
        mock_datastore.account_name = "any_datastore_account_name"
        mock_datastore.container_name = "any_datastore_container_name"

        mock_model = MagicMock()
        mock_model.name = self._args["edge_package_name"]
        mock_model.path = (
            f"azureml:.../datastores/{mock_datastore_name}/paths/{mock_blob_name}"
        )
        mock_model.version = self._args["edge_package_version"]

        mock_ml_client_object = MagicMock()
        mock_ml_client_object.datastores.get.return_value = mock_datastore
        mock_ml_client_object.models.get.return_value = mock_model
        mock_ml_client.return_value = mock_ml_client_object

        mock_model_manager_object = MagicMock()
        mock_model_manager_object.state = "Success"
        mock_model_manager.return_value = mock_model_manager_object

        # WHEN
        main(**self._args)

        # THEN
        mock_model_manager.assert_called_once_with(
            iot_hub_con_str=iot_hub_secret,
            iot_event_hub_con_str=event_hub_secret,
            device_id=self._args["device_id"],
            storage_account_name=mock_datastore.account_name,
            container_name=mock_datastore.container_name,
            blob_name=mock_blob_name,
            azure_credential=mock_credential.return_value,
            package_id=ANY,
            package_name=self._args["edge_package_name"],
            package_version=self._args["edge_package_version"]
        )
        mock_model_manager_object.start_event_hub_loop.assert_called_once()

    @patch("mlops.common.src.package_delivery.ModelManager")
    @patch("mlops.common.src.package_delivery.MLClient")
    @patch("mlops.common.src.package_delivery.SecretClient")
    def test_main_with_latest_version(self, _, mock_ml_client, mock_model_manager):
        # GIVEN
        blob_name_of_latest_model = "blob_name_of_latest"

        mock_model_manager_object = MagicMock()
        mock_model_manager_object.state = "Success"
        mock_model_manager.return_value = mock_model_manager_object

        mock_model1 = MagicMock()
        mock_model1.version = 1
        mock_model2 = MagicMock()
        mock_model2.version = 321
        mock_model2.path = (
            f"azureml:.../datastores/.../paths/{blob_name_of_latest_model}"
        )
        mock_model3 = MagicMock()
        mock_model3.version = 2
        mock_ml_client_object = MagicMock()
        mock_ml_client_object.models.list.return_value = [
            mock_model1,
            mock_model2,
            mock_model3,
        ]
        mock_ml_client.return_value = mock_ml_client_object

        # WHEN
        args_with_latest_version = copy.deepcopy(self._args)
        args_with_latest_version.update({"edge_package_version": "latest"})

        main(**args_with_latest_version)

        # THEN
        mock_ml_client_object.models.list.assert_called_once()

        mock_model_manager.assert_called_once_with(
            iot_hub_con_str=ANY,
            iot_event_hub_con_str=ANY,
            device_id=self._args["device_id"],
            storage_account_name=ANY,
            container_name=ANY,
            blob_name=blob_name_of_latest_model,
            azure_credential=ANY,
            package_id=ANY,
            package_name=ANY,
            package_version=ANY
        )
        mock_model_manager_object.start_event_hub_loop.assert_called_once()
