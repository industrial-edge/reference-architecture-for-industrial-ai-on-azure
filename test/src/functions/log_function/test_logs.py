# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

"""
Tests for log_func Azure Function code.
"""

import unittest
import uuid
from functools import wraps
from unittest.mock import MagicMock, patch, ANY

import azure.functions as func
from _pytest.monkeypatch import MonkeyPatch
from azure.keyvault.secrets import KeyVaultSecret
from src.functions.log_function import LogFunc


def patch_all(f):
    """
    Patches all of the library calls that are required to
    make the logs write function work.
    """

    @patch("azure.monitor.ingestion.LogsIngestionClient.upload")
    @patch("azure.storage.blob.BlobClient.from_connection_string")
    @patch("azure.keyvault.secrets.SecretClient.get_secret")
    @wraps(f)
    def functor(*args, **kwargs):
        return f(*args, **kwargs)

    return functor


class TestLogFunc(unittest.TestCase):
    """
    Test class for the log_func method.
    """

    _function_path = "/api/logs"
    _logs_key_vault_uri_env_var = "LOGS_KEY_VAULT_URL"
    _storage_account_connection_string_name_env_var = (
        "STORAGE_CONNECTION_STRING_SECRET_NAME"
    )
    _log_analytics_dcr_identifier_name_envvar = "LOG_ANALYTICS_DCR_IDENTIFIER_NAME"
    _log_analytics_table_name_envvar = "LOG_ANALYTICS_TABLE_NAME"
    _log_analytics_endpoint_name_envvar = "LOG_ANALYTICS_ENDPOINT_NAME"
    _dcr_identifier_name_envvar = "LOG_ANALYTICS_DCR_IDENTIFIER_NAME"
    _log_analytics_table_name_envvar = "LOG_ANALYTICS_TABLE_NAME"

    _secret_connection_string_value = "secret_connection_string_value"
    _log_analytics_endpoint_name_value = "log_analytics_endpoint_name_value"
    _dcr_identifier_name_value = "dcr_identifier_name_value"
    _log_analytics_table_name_value = "log_analytics_table_name_value"

    _monkeypatch = MonkeyPatch()
    _log_func = LogFunc()

    def setUp(self):
        self._set_required_environment_variables()

    @patch_all
    def test_log_func_returns_200(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        """
        Tests the log_func returns 200 when called
        with a valid request.
        """

        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        resp = self._log_func.execute(req)

        # Check the output.
        self.assertEqual(
            resp.status_code,
            200,
        )

    @patch_all
    def test_returns_bad_request_if_x_log_source_header_is_missing(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        """
        Tests the log_func returns 400 when called
        without the x-logs-source header
        """

        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
        )

        # Call the function.
        resp = self._log_func.execute(req)

        # Check the output.
        self.assertEqual(
            resp.status_code,
            400,
        )

    @patch_all
    def test_returns_bad_request_if_x_arr_log_id_is_not_a_uuid(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        """
        Tests the log_func returns 400 when called
        with an x-arr-log-id header that does not contain a uuid.
        """

        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        headers = self._get_valid_headers()
        headers["X-ARR-LOG-ID"] = "hello world"

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=headers,
        )

        # Call the function.
        resp = self._log_func.execute(req)

        # Check the output.
        self.assertEqual(
            resp.status_code,
            400,
        )

    @patch_all
    def test_returns_bad_request_if_body_is_empty(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        """
        Tests the log_func returns 400 when called
        with an empty body.
        """

        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=bytearray(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        resp = self._log_func.execute(req)

        # Check the output.
        self.assertEqual(
            resp.status_code,
            400,
        )

    @patch_all
    def test_returns_internal_server_error_if_keyvault_url_envvar_is_missing(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        """
        Tests the log_func returns 500 when called
        and the logs_storage_account_name envvar
        is not set.
        """

        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        self._unset_required_environment_variables(self._logs_key_vault_uri_env_var)

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        resp = self._log_func.execute(req)

        # Check the output.
        self.assertEqual(
            resp.status_code,
            500,
        )

    @patch_all
    def test_returns_internal_server_error_if_storage_connection_string_envvar_is_missing(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        """
        Tests the log_func returns 500 when called
        and the logs_storage_account_name envvar
        is not set.
        """

        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        self._unset_required_environment_variables(
            self._storage_account_connection_string_name_env_var
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        resp = self._log_func.execute(req)

        # Check the output.
        self.assertEqual(
            resp.status_code,
            500,
        )

    @patch_all
    def test_returns_internal_server_error_if_log_analytics_dcr_identifier_envvar_is_missing(  # noqa
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        """
        Tests the log_func returns 500 when called
        and the logs_storage_account_name envvar
        is not set.
        """

        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        self._unset_required_environment_variables(
            self._log_analytics_dcr_identifier_name_envvar
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        resp = self._log_func.execute(req)

        # Check the output.
        self.assertEqual(
            resp.status_code,
            500,
        )

    @patch_all
    def test_returns_internal_server_error_if_log_analytics_table_name_envvar_is_missing(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        """
        Tests the log_func returns 500 when called
        and the logs_storage_account_name envvar
        is not set.
        """

        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        self._unset_required_environment_variables(
            self._log_analytics_table_name_envvar
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        resp = self._log_func.execute(req)

        # Check the output.
        self.assertEqual(
            resp.status_code,
            500,
        )

    @patch_all
    def test_returns_internal_server_error_if_log_analytics_endpoint_envvar_is_missing(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        """
        Tests the log_func returns 500 when called
        and the logs_storage_account_name envvar
        is not set.
        """

        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        self._unset_required_environment_variables(
            self._log_analytics_endpoint_name_envvar
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        resp = self._log_func.execute(req)

        # Check the output.
        self.assertEqual(
            resp.status_code,
            500,
        )

    @patch_all
    def test_writes_blob_to_storage(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        self._log_func.execute(req)

        self.mock_blob_client_upload_blob.upload_blob.assert_called()

    @patch_all
    def test_get_connection_string_from_key_vault(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        self._log_func.execute(req)

        mock_key_vault_client_get_secret.assert_called()

    @patch_all
    def test_builds_storage_client_with_secret_connection_string(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        self._log_func.execute(req)

        self.mock_blob_client_from_connection_string.assert_called_with(
            self._secret_connection_string_value, "logs", ANY
        )

    @patch_all
    def test_uploads_logs_to_log_analytics(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body=self._get_valid_body(),
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        self._log_func.execute(req)

        mock_log_ingestion_client_upload.assert_called()

    @patch_all
    def test_writes_bad_lines_to_blob(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        self._patch_dependencies(
            mock_key_vault_client_get_secret,
            mock_blob_client_from_connection_string,
            mock_log_ingestion_client_upload,
        )

        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method="POST",
            body='[{"log":"bad body"},{"log":"bad_two"}]',
            url=self._function_path,
            params={},
            headers=self._get_valid_headers(),
        )

        # Call the function.
        self._log_func.execute(req)

        self.mock_blob_client_upload_blob.upload_blob.assert_called()

    def _patch_dependencies(
        self,
        mock_key_vault_client_get_secret: MagicMock,
        mock_blob_client_from_connection_string: MagicMock,
        mock_log_ingestion_client_upload: MagicMock,
    ):
        self.mock_key_vault_client_get_secret = mock_key_vault_client_get_secret
        self.mock_blob_client_from_connection_string = (
            mock_blob_client_from_connection_string
        )
        self.mock_blob_client_upload_blob = MagicMock()

        self.mock_key_vault_client_get_secret.return_value = KeyVaultSecret(
            self._storage_account_connection_string_name_env_var,
            value=self._secret_connection_string_value,
        )

        self.mock_blob_client_from_connection_string.return_value = (
            self.mock_blob_client_upload_blob
        )

    def _set_required_environment_variables(self):
        self._monkeypatch.setenv(
            self._logs_key_vault_uri_env_var, "http://keyvault.com"
        )
        self._monkeypatch.setenv(
            self._storage_account_connection_string_name_env_var,
            self._secret_connection_string_value,
        )
        self._monkeypatch.setenv(
            self._log_analytics_endpoint_name_envvar,
            self._log_analytics_endpoint_name_value,
        )
        self._monkeypatch.setenv(
            self._dcr_identifier_name_envvar,
            self._dcr_identifier_name_value,
        )
        self._monkeypatch.setenv(
            self._log_analytics_table_name_envvar,
            self._log_analytics_table_name_value,
        )

    def _unset_required_environment_variables(self, envvar_to_remove: str):
        self._monkeypatch.delenv(envvar_to_remove)

    def _get_valid_headers(self):
        valid_headers = {
            "X-LOGS-SOURCE": "machine-a",
            "X-ARR-LOG-ID": str(uuid.uuid4()),
        }
        return valid_headers

    def _get_valid_body(self):
        logs = """
        [{"date":1686655026.344064,"log":"[2023-05-23T00:01:56.449Z] [Log] [I] [thread 724] [inference] Status has been changed. Pipeline ID: f6c7374b-90fb-4cd8-becb-227cbcf45197:1.0.666, Name: inference, Status: Running"},
        {"date":1686655026.344068,"log":"[2023-05-23T00:01:57.466Z] [Log] [I] [thread 724] [inference] Status has been changed. Pipeline ID: f6c7374b-90fb-4cd8-becb-227cbcf45197:1.0.666, Name: inference, Status: Waiting"},
        {"date":1686655026.34407,"log":"[2023-05-23T00:13:12.793Z] [Log] [I] [thread 724] [inference] Status has been changed. Pipeline ID: f6c7374b-90fb-4cd8-becb-227cbcf45197:1.0.666, Name: inference, Status: Running"},
        {"date":1686655026.344071,"log":"[2023-05-23T00:13:13.794Z] [Log] [I] [thread 724] [inference] Status has been changed. Pipeline ID: f6c7374b-90fb-4cd8-becb-227cbcf45197:1.0.666, Name: inference, Status: Waiting"}]
        """  # noqa
        return logs
