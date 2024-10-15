"""
Azure Function for Logs.
"""
import datetime
import json
import logging
import os
import uuid

import azure.functions as func

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobClient, BlobType
from azure.monitor.ingestion import LogsIngestionClient

from .log_parsers import message_factory


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    The main for the Azure Function to receive, parse and save Log data from the edge.

    Parameters
    ----------
    req: HttpRequest
        Incoming HTTP request.

    Returns
    -------
    HttpResponse
        HttpResponse containing the response code.

    """
    return LogFunc().execute(req)


class LogFunc:
    def execute(self, req: func.HttpRequest) -> func.HttpResponse:
        """
        The Azure Function to receive, parse and save Log data from the edge.

        Parameters
        ----------
        req: HttpRequest
            Incoming HTTP request.

        Returns
        -------
        HttpResponse
            HttpResponse containing the response code.
        """

        try:
            req_body = self._extract_request_body(req)
        except Exception as ex:
            logging.exception(ex)
            return func.HttpResponse("Unable to parse JSON payload", status_code=400)

        body_length = len(req_body)

        source_header = req.headers.get("X-LOGS-SOURCE")

        if source_header is None:
            return func.HttpResponse("Missing X-Log-Source header", status_code=400)

        source_machine = source_header.split(";")[0]
        message_id = req.headers.get("X-ARR-LOG-ID")

        self._key_vault_url = os.environ.get("LOGS_KEY_VAULT_URL")
        self._dcr_identifier_name = os.environ.get("LOG_ANALYTICS_DCR_IDENTIFIER_NAME")
        self._log_analytics_table_name = os.environ.get("LOG_ANALYTICS_TABLE_NAME")
        self._storage_connection_secret_name = os.environ.get(
            "STORAGE_CONNECTION_STRING_SECRET_NAME"
        )
        self._log_analytics_endpoint_secret_name = os.environ.get(
            "LOG_ANALYTICS_ENDPOINT_NAME"
        )

        container_name = "logs"

        if message_id is None:
            message_id = str(uuid.uuid4())

        credential = DefaultAzureCredential()

        validation_error = self._validate_requirements(
            body_length, source_machine, message_id, credential
        )

        if validation_error is not None:
            return validation_error

        blob_name = (
            f"{source_machine}/{datetime.datetime.utcnow().isoformat()}-{message_id}"
        )

        logging.info(
            f"logs called with body of {body_length} bytes from source"
            + f" {source_machine} writing to {blob_name}"
        )
        try:
            self._write_logs_to_blob(
                container_name,
                blob_name,
                req_body,
                body_length,
            )

        except Exception as ex:
            logging.exception(ex)
            return func.HttpResponse(
                f"Blob {blob_name} failed to write", status_code=500
            )

        try:
            self._write_logs_to_log_analytics(
                credential,
                blob_name,
                req_body,
                source_machine,
            )

        except Exception as ex:
            logging.exception(ex)
            return func.HttpResponse(
                "Logs failed to write to Log Analytics", status_code=500
            )

        return func.HttpResponse(
            f"Blob {blob_name} successfully written", status_code=200
        )

    def _write_logs_to_log_analytics(
        self,
        credential: DefaultAzureCredential,
        blob_name: str,
        logs_data: str,
        source_machine: str,
    ):
        logs_client = LogsIngestionClient(
            endpoint=self._log_analytics_endpoint,
            credential=credential,
            log_type="EdgeLogs",
            logging_enable=True,
        )

        lines = logs_data.splitlines()

        log_messages = []

        factory = message_factory.MessageFactory()

        for line in lines:
            if line.strip() != "":

                message = factory.build_message(line, blob_name, source_machine)
                log_messages.append(message)

        if log_messages != []:
            logs_client.upload(
                rule_id=self._dcr_identifier,
                stream_name=f"Custom-{self._log_analytics_table_name}",
                logs=log_messages,
            )

        logging.info("Upload successful")

    def _write_logs_to_blob(
        self,
        container_name: str,
        blob_name: str,
        logs_data: str,
        logs_length: int,
    ):
        blob_client = BlobClient.from_connection_string(
            self.storage_connection_string.value,
            container_name,
            f"{blob_name}",
        )
        blob_client.upload_blob(
            logs_data, blob_type=BlobType.BlockBlob, length=logs_length
        )

    def _validate_requirements(
        self,
        body_length: int,
        source_machine: str,
        message_id: str,
        credenials: DefaultAzureCredential,
    ) -> func.HttpResponse:
        if body_length == 0:
            logging.critical("Body cannot be empty")
            return func.HttpResponse("Body cannot be empty", status_code=400)

        if source_machine is None:
            logging.critical("Missing mandatory header: X-LOGS-SOURCE")
            return func.HttpResponse(
                "Missing mandatory header: X-LOGS-SOURCE", status_code=400
            )

        if self._key_vault_url is None:
            logging.critical("Missing environment variable LOGS_KEY_VAULT_URL")
            return func.HttpResponse("KeyVault URL error", status_code=500)

        if self._storage_connection_secret_name is None:
            logging.critical(
                "Missing environment variable STORAGE_CONNECTION_STRING_SECRET_NAME"
            )
            return func.HttpResponse(
                "Connection string secret name error", status_code=500
            )

        if self._dcr_identifier_name is None:
            logging.critical(
                "Missing environment variable LOG_ANALYTICS_DCR_IDENTIFIER_NAME"
            )
            return func.HttpResponse("DCR Identifier error", status_code=500)

        if self._log_analytics_table_name is None:
            logging.critical("Missing environment variable LOG_ANALYTICS_TABLE_NAME")
            return func.HttpResponse("Table Name error", status_code=500)

        if self._log_analytics_endpoint_secret_name is None:
            logging.critical("Missing environment variable LOG_ANALYTICS_ENDPOINT NAME")
            return func.HttpResponse(
                "Log Analytics Endpoint Name error", status_code=500
            )

        try:
            uuid.UUID(message_id)
        except ValueError:
            logging.critical("X-ARR-LOG-ID is not a valid UUID")
            return func.HttpResponse(
                "X-ARR-LOG-ID is not a valid UUID", status_code=400
            )

        key_vault_client = SecretClient(
            vault_url=self._key_vault_url, credential=credenials
        )

        self.storage_connection_string = key_vault_client.get_secret(
            self._storage_connection_secret_name
        )
        if self.storage_connection_string is None:
            logging.critical(f"Missing secret {self._storage_connection_secret_name}")
            return func.HttpResponse("Storage connection string error", status_code=500)

        self._dcr_identifier = key_vault_client.get_secret(self._dcr_identifier_name)

        self._log_analytics_endpoint = key_vault_client.get_secret(
            self._log_analytics_endpoint_secret_name
        )

        if self._log_analytics_endpoint is None:
            logging.critical(
                f"Missing secret {self._log_analytics_endpoint_secret_name}"
            )
            return func.HttpResponse("Log Analytics Endpoint error", status_code=500)

    def _extract_request_body(self, req: func.HttpRequest):
        req_body_string = req.get_body()

        req_body_json = json.loads(req_body_string)

        req_body_list = []
        for item in req_body_json:
            log = item.get("log")
            req_body_list.append(log)

        return "\n".join(req_body_list)
