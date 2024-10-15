import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from mlops.common.src.data_asset_creation_utils import create_data_asset


class TestDataAssetCreationUtils(TestCase):
    def test_create_data_asset_success(self):
        create_or_update_mock = MagicMock()
        client = MagicMock(data=MagicMock(create_or_update=create_or_update_mock))
        _create_args_list = ["path", "file", "asset"]

        create_data_asset(client, *_create_args_list)

        call_args_create = create_or_update_mock.call_args_list[0][0][0]

        self.assertEqual(call_args_create.name, _create_args_list[2])
        self.assertEqual(call_args_create.description, "Data Asset")
        self.assertEqual(call_args_create.type, _create_args_list[1])
        self.assertEqual(
            call_args_create.path, Path(os.path.join(os.getcwd(), _create_args_list[0]))
        )
        create_or_update_mock.assert_called_once()
