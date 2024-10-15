# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import json
from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch, MagicMock
from uuid import UUID, uuid4

from mlops.common.src.package_delivery_mm import ModelManager


def is_valid_uuid(uuid_to_test: str, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def convert_to_datetime(time_in: str):
    return datetime.strptime(time_in, "%Y-%m-%dT%H:%M:%S.%fZ")


class TestPackageDelivery(TestCase):
    _args = {
        "iot_event_hub_con_str": "event_hub_secret",
        "iot_hub_con_str": "iot_hub_secret",
        "device_id": "any_device_id",
        "storage_account_name": "any_storage_account_name",
        "container_name": "any_container_name",
        "blob_name": "any_blob_name",
        "azure_credential": MagicMock(),
        "package_id": uuid4().__str__(),
        "package_name": "any_package_name",
        "package_version": "1",
    }

    @patch("mlops.common.src.package_delivery_mm.EventHubConsumerClient")
    @patch(
        "mlops.common.src.package_delivery_mm.IoTHubRegistryManager.from_connection_string"
    )
    def test_if_delivery_started(
        self,
        mock_iot_hub_registry_manager,
        mock_event_hub_consumer_client,
    ):
        # GIVEN
        mock_delivery_id = "any-uuid"

        mock_iot_hub_registry_manager_object = MagicMock()
        mock_iot_hub_registry_manager.return_value = (
            mock_iot_hub_registry_manager_object
        )

        ut = ModelManager(**self._args)
        ut.delivery_id = mock_delivery_id

        # WHEN
        ut.start_event_hub_loop()

        # THEN
        mock_event_hub_consumer_client.from_connection_string.assert_called_once()

        ut.registry_manager.send_c2d_message.assert_called_once()
        (
            c2d_msg_device_id,
            raw_c2d_msg_body,
        ), kwargs = ut.registry_manager.send_c2d_message.call_args

        self.assertEqual(c2d_msg_device_id, self._args["device_id"])
        c2d_msg_body = json.loads(raw_c2d_msg_body)
        self.assertTrue(is_valid_uuid(c2d_msg_body["packageId"]))
        self.assertTrue(is_valid_uuid(c2d_msg_body["eventId"]))
        self.assertTrue(
            datetime.now() - timedelta(seconds=5)
            < convert_to_datetime(c2d_msg_body["timestamp"])
            <= datetime.now()
        )
        self.assertEqual(kwargs["properties"]["type"], "event")
        self.assertEqual(kwargs["properties"]["kind"], "newDelivery")
        self.assertEqual(kwargs["properties"]["deliveryId"], mock_delivery_id)
        self.assertTrue(is_valid_uuid(kwargs["properties"]["projectId"]))

    @patch("mlops.common.src.package_delivery_mm.generate_blob_sas")
    @patch("mlops.common.src.package_delivery_mm.BlobServiceClient")
    @patch("mlops.common.src.package_delivery_mm.EventHubConsumerClient")
    @patch(
        "mlops.common.src.package_delivery_mm.IoTHubRegistryManager.from_connection_string"
    )
    def test_event_processing_presigned_url_response(
        self,
        mock_iot_hub_registry_manager,
        _,
        mock_blob_service_client,
        mock_generate_blob_sas,
    ):
        # GIVEN
        mock_delivery_id = "any-uuid"
        mock_iot_hub_registry_manager_object = MagicMock()
        mock_iot_hub_registry_manager.return_value = (
            mock_iot_hub_registry_manager_object
        )

        mock_sas = "any_sas"
        mock_generate_blob_sas.return_value = mock_sas

        mock_partition_context = MagicMock()

        mock_url_request_event = MagicMock()
        mock_url_request_event.properties = {
            str.encode("deliveryId"): str.encode(mock_delivery_id),
            str.encode("type"): str.encode("event"),
            str.encode("kind"): str.encode("presignedUrlRequest"),
        }

        ut = ModelManager(**self._args)
        ut.delivery_id = mock_delivery_id

        # WHEN
        ut._process_event_hub_event(mock_partition_context, mock_url_request_event)

        # THEN
        mock_blob_service_client.assert_called_once()
        expected_package_url = (
            f'https://{self._args["storage_account_name"]}.blob.core.windows.net/'
            f'{self._args["container_name"]}/{self._args["blob_name"]}?{mock_sas}'
        )

        ut.registry_manager.send_c2d_message.assert_called_once()

        (
            c2d_msg_device_id,
            raw_c2d_msg_body,
        ), kwargs = ut.registry_manager.send_c2d_message.call_args

        self.assertEqual(c2d_msg_device_id, self._args["device_id"])
        c2d_msg_body = json.loads(raw_c2d_msg_body)
        self.assertTrue(
            datetime.now() - timedelta(seconds=5)
            < convert_to_datetime(c2d_msg_body["timestamp"])
            <= datetime.now()
        )
        self.assertEqual(
            c2d_msg_body["attributes"]["presignedUrl"], expected_package_url
        )

        self.assertEqual(kwargs["properties"]["type"], "data")
        self.assertEqual(kwargs["properties"]["kind"], "presignedUrlResponse")
        self.assertEqual(kwargs["properties"]["deliveryId"], mock_delivery_id)
        self.assertTrue(is_valid_uuid(kwargs["properties"]["projectId"]))

    @patch("mlops.common.src.package_delivery_mm.EventHubConsumerClient")
    @patch("mlops.common.src.package_delivery_mm.IoTHubRegistryManager")
    def test_event_processing_state_report(self, mock_iot_hub_registry_manager, _):
        # GIVEN
        mock_delivery_id = "any-uuid"
        mock_delivery_state_from_mm = "any_state"

        mock_iot_hub_registry_manager_object = MagicMock()
        mock_iot_hub_registry_manager.return_value = (
            mock_iot_hub_registry_manager_object
        )

        mock_partition_context = MagicMock()

        mock_state_report_event = MagicMock()
        mock_state_report_event.body_as_json.return_value = {
            "state": mock_delivery_state_from_mm
        }
        mock_state_report_event.properties = {
            str.encode("deliveryId"): str.encode(mock_delivery_id),
            str.encode("type"): str.encode("state"),
        }

        ut = ModelManager(**self._args)
        ut.delivery_id = mock_delivery_id

        # WHEN
        ut._process_event_hub_event(mock_partition_context, mock_state_report_event)

        # THEN
        self.assertEqual(ut.state, mock_delivery_state_from_mm)
