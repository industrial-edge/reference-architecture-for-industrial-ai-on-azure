# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

import json
import datetime
import uuid
import logging
import sys

from azure.iot.hub import IoTHubRegistryManager
from azure.eventhub import EventData
from azure.eventhub import EventHubConsumerClient

from azure.eventhub.aio._eventprocessor.partition_context import PartitionContext
from azure.identity import ChainedTokenCredential
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat() + "Z"


class DeliveryFinished(Exception):  # noqa: N818
    # the class is used as an event to stop messaging even if it is failed or successful
    def __init__(self, message):
        super().__init__(message)


class ModelManager:
    """
    A class to manage communication with AI Model Manager (= IoT Hub device)
    by acting as a IoT Hub and IoT Event client Hub with aim of providing a presigned link.
    """

    def __init__(
        self,
        iot_event_hub_con_str: str,
        iot_hub_con_str: str,
        device_id: str,
        storage_account_name: str,
        container_name: str,
        blob_name: str,
        azure_credential: ChainedTokenCredential,
        package_id: str,
        package_name: str,
        package_version: str,
    ):
        """
        Constructs all the necessary attributes for the azuredelivery object.
        Parameters:
                iot_event_hub_con_str : str
                    Primary connection string which allows reading events from Event Hub default endpoint
                iot_hub_con_str : str
                    Primary connection string which allows sending messages to IoT Hub
                device_id : str
                    name of the registered IoT Hub device (= AI Model Manager Azure ws)
                storage_account_name : str
                    Storage account name under which the package to be delivered is stored
                container_name : str
                    Container name under which the package to be delivered is stored
                blob_name : str
                    Blob name under which the package to be delivered is found
                azure_credential: azure.identity.ChainedTokenCredential
                    Azure credential required to generate Shared Access Signature link
                    pointing to the package being delivered
        """
        self.iot_event_hub_con_str = iot_event_hub_con_str
        self.iot_hub_con_str = iot_hub_con_str
        self.device_id = device_id
        self.storage_account_name = storage_account_name
        self.container_name = container_name
        self.blob_name = blob_name
        self.azure_credential = azure_credential

        self.registry_manager = IoTHubRegistryManager.from_connection_string(
            self.iot_hub_con_str
        )

        # a dedicated consumer group can be created on IoTHub and then assigned here
        # that can be useful when the eventhub is already used on other purpose
        self.consumer_group = ("$Default", "modelmanager", "mlops_target")  
        self.event_hub_client = EventHubConsumerClient.from_connection_string(
            self.iot_event_hub_con_str, consumer_group=self.consumer_group[0]
        )

        self.state = "NewDelivery"  # new delivery starts by sending NewDelivery message from Cloud to ModelManager (C2D)
        self.time_out = 60  # maximum time in seconds waiting between two messages from Model Manager

        self.package_id = package_id or str(uuid.uuid4())  # an older version of pipeline package might not have package id
        self.package_name = package_name
        self.package_version = package_version

        self.delivery_id = str(uuid.uuid4())  # unique id for the current delivery communication
        self.project_id = str(uuid.uuid4())
        self.event_id = str(uuid.uuid4())

    def on_event(self, partition_context: PartitionContext, event: EventData):
        """
        Callback function triggered by an EventHub message
        - Timeout cause a None event, and the messaging workflow can be stopped
        - Only events with the initiated delivery id will be processed, others will be ignored
        - In case the delivery state is changed to 'Success' or 'Error', the messaging is stopped
        """
        if event is None:
            logger.error("Actual delivery has been timed out")
            self.event_hub_client.close()
            raise TimeoutError("Actual delivery has been timed out")

        logger.debug(
            "event received on partition '%s', consumer group '%s'",
            partition_context.partition_id,
            partition_context.consumer_group,
        )

        message_body = self._process_event_hub_event(partition_context, event)
        logger.debug("Actual delivery state: %s", self.state)

        if self.state in ["Success", "Error"]:
            self.event_hub_client.close()
            raise DeliveryFinished(
                f"Actual delivery has been finished with state '{self.state}' and message {message_body}"
            )

    def start_event_hub_loop(self):
        """
        Initiates and manages the communication with AI Model Manager
        by acting as a IoT Hub and IoT Event Hub client.
        The callback function "on_event" will be triggered when message event arrives.
        Events will be processed with timestamp after `start_time`
        """
        try:
            start_time = datetime.datetime.now()
            self._initiate_delivery()
            logger.debug("initiative message has been sent to the device")

            self.event_hub_client.receive(
                on_event=self.on_event,
                starting_position=start_time,
                max_wait_time=self.time_out,
            )

        except DeliveryFinished as finished:
            logger.debug("Actual delivery has been finished with state %s", finished)

        except Exception as err:
            self.event_hub_client.close()
            logger.error("Unknown error occurred during package delivery: %s", err)

        finally:
            logger.debug("IoT Hub event loop thread exited.")

    def _process_event_hub_event(
        self, partition_context: PartitionContext, event: EventData
    ):
        """
        Processes events arriving from Event Hub (or an Evnet Hub compatible endpoint)
        The events are filtered by deliveryId - only messages which match the class attribute deliveryId are considered.
        """
        body = event.body_as_json(encoding="UTF-8")

        application_properties = {
            k.decode("ascii"): v.decode("ascii") for k, v in event.properties.items()
        }

        # check if message has same 'deliveryId', otherwise skip message
        if "deliveryId" in application_properties:
            logger.debug("Event body: %s", body)
            logger.debug(
                "Event application properties: %s from group %s",
                application_properties,
                partition_context.consumer_group,
            )
            if self.delivery_id != application_properties["deliveryId"]:
                logger.debug(
                    "Event does not match deliveryId %s. Received deliveryId %s. Skipped.",
                    self.delivery_id,
                    application_properties["deliveryId"],
                )
                return body
        else:
            logger.debug(
                "Event message has no 'deliveryId' in application properties. Skipped."
            )
            return body

        # check message purpose e.g. 'kind' (action required) or 'state' update message
        if "type" in application_properties:
            if application_properties["type"] == "event":
                if application_properties["kind"] == "presignedUrlRequest":
                    self.state = "PresignedUrlRequested"

                    presigned_link = self._create_presigned_link()
                    self._send_presigned_link(presigned_link=presigned_link)

                    self.state = "PresignedUrlCreated"
            elif application_properties["type"] == "state":
                self.state = body["state"]
                logger.debug("Delivery state has been changed: %s", self.state)

        return body

    def _initiate_delivery(self):
        """
        Sends the first c2d message to AI Model Manager that a new edge config package is ready
        to be downloaded.
        """
        logger.debug(
            "Sending c2d message to %s in order to initiate new delivery %s ...",
            self.device_id,
            self.delivery_id,
        )
        data = {
            "packageId": self.package_id,
            "packageVersion": self.package_version,
            "eventId": self.event_id,
            "timestamp": datetime.datetime.now(),
        }

        message_body = json.dumps(data, indent=4, cls=DateTimeEncoder)
        logger.debug("message_body: %s", message_body)

        props = {}
        props.update(contentType="application/json")
        props.update(type="event")
        props.update(kind="newDelivery")
        props.update(deliveryId=self.delivery_id)
        props.update(projectId=self.project_id)

        try:
            self.registry_manager.send_c2d_message(
                self.device_id, message_body, properties=props
            )
            logger.debug(
                f"New delivery {self.delivery_id} to {self.device_id} initiated."
            )
        except Exception as exp:
            logger.error("An error occurred while sending message: %s", exp)
            raise exp

    def _create_presigned_link(self):
        """
        Creates a Shared Access Signature link based on storage account name,
        container name and blob name.
        Returns:
            sas_url (str): presigned link as url with SAS token
        """
        url = f"https://{self.storage_account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(url, credential=self.azure_credential)
        udk = blob_service_client.get_user_delegation_key(
            key_start_time=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
            key_expiry_time=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        )

        sas = generate_blob_sas(
            account_name=self.storage_account_name,
            container_name=self.container_name,
            blob_name=self.blob_name,
            user_delegation_key=udk,
            permission=BlobSasPermissions(read=True),
            start=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        )
        sas_url = (
            f"https://{self.storage_account_name}.blob.core.windows.net/"
            f"{self.container_name}/{self.blob_name}?{sas}"
        )
        return sas_url

    def _send_presigned_link(self, presigned_link):
        """
        Sends presigned link as c2d message to AI Model Manager.
        Parameter:
            presigned_link (str): presigned link as url with SAS token
        """
        logger.debug(f"Presigned link created for delivery {self.delivery_id}")
        # create presigned link message
        data = {
            "timestamp": datetime.datetime.now(),
            "attributes": {"presignedUrl": presigned_link},
        }
        message_body = json.dumps(data, indent=4, cls=DateTimeEncoder)

        props = {}
        props.update(contentType="application/json")
        props.update(type="data")
        props.update(kind="presignedUrlResponse")
        props.update(deliveryId=self.delivery_id)
        props.update(projectId=self.project_id)

        self.registry_manager.send_c2d_message(
            self.device_id, message_body, properties=props
        )
        logger.debug(
            f"Presigned link sent for delivery {self.delivery_id} to {self.device_id}"
        )
