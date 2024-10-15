import numpy
import tempfile
from pathlib import Path
from unittest import TestCase

import pandas as pd

from mlops.state_identifier.src.prep.payload import main


class TestPayload(TestCase):
    def mock_data_frame(self, length: int):
        df_test = pd.DataFrame(columns=["ph1", "ph2", "ph3", "class"])
        df_test["ph1"] = numpy.random.uniform(low=4000.0, high=6000.0, size=(length,))
        df_test["ph2"] = numpy.random.uniform(low=4000.0, high=6000.0, size=(length,))
        df_test["ph3"] = numpy.random.uniform(low=4000.0, high=6000.0, size=(length,))
        df_test["class"] = 0
        return df_test

    def test_main_success(self):
        with tempfile.TemporaryDirectory() as mock_data_path:
            assert Path(mock_data_path).is_dir()
            _mock_raw_data_path = Path(mock_data_path) / "state_identifier.parquet"
            _mock_payload_data_path = Path(mock_data_path) / "payload_data"

            df_test = self.mock_data_frame(300)
            df_test.to_parquet(_mock_raw_data_path)

            main(_mock_raw_data_path, _mock_payload_data_path)

            assert _mock_payload_data_path.is_file()
