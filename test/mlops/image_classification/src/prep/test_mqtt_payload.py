# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY
from PIL import Image

from mlops.image_classification.src.prep.mqtt_payload import main


class TestPayload(TestCase):
    _args = {
        "raw_data": "./path/to/raw_data",
        "payload_data": "./path/to/payload_data",
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls._workdir = Path(".").resolve()
        cls._tempdir = Path(tempfile.mkdtemp()).resolve()

        cls._args["raw_data"] = Path(cls._tempdir / cls._args["raw_data"]).resolve()
        cls._image_path = Path(cls._args["raw_data"] / "classA/image.png").resolve()

        cls._image_path.parent.mkdir(parents=True, exist_ok=True)
        pil_image = Image.new("RGB", (224, 224), (255, 255, 255))
        pil_image.save(cls._image_path)

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        os.chdir(cls._workdir)
        shutil.rmtree(cls._tempdir)
        return super().tearDownClass()

    @patch("joblib.dump")
    def test_main_success(self, mock_joblib_dump: MagicMock):

        main(**self._args)

        mock_joblib_dump.assert_called_once_with(
            ANY, self._args["payload_data"], compress=9
        )
