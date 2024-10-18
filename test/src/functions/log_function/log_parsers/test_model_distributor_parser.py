# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import unittest

from src.functions.log_function.log_parsers.model_distributor_parser import (
    ModelDistributorParser,
)


class TestModelDistributorParser(unittest.TestCase):

    # ModelDistributor sample log strings
    test_log1 = '{"createdOn":"2023-06-21T00:00:55.618Z","level":"debug","message":"Get log messages"}'  # noqa

    def test_can_parse_return_true_for_test_log1(self):
        parser = ModelDistributorParser()
        assert parser.can_parse(self.test_log1)

    def test_parse_correctly_parses_test_log1(self):
        parser = ModelDistributorParser()

        message = parser.parse(self.test_log1, "blob", "source")

        assert message["Timestamp"] == "2023-06-21T00:00:55.618000Z"
        assert message["Severity"] == "DEBUG"
        assert message["Thread"] == "-1"
        assert message["Message"] == "Get log messages"
