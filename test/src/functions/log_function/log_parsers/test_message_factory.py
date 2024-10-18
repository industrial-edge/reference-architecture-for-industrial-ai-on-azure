# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import unittest

from src.functions.log_function.log_parsers.message_factory import MessageFactory


class TestMessageFactory(unittest.TestCase):

    model_distributor_parser_log = '{"createdOn":"2023-06-21T00:00:55.618Z","level":"debug","message":"Get log messages"}'  # noqa
    regex_parser_log = "[2023-06-12T13:44:37.950Z] [Log] [I] [thread 536] [inference] Python Executor is starting ... [State Identifier, 1.0.2, ID: 36e03b33-ed16-4a2b-a951-048e4b21e86e]"  # noqa

    def test_build_message_parses_regex_parser_log(self):
        message_factory = MessageFactory()

        message = message_factory.build_message(
            self.regex_parser_log, "blob_name", "source"
        )

        assert message["Timestamp"] == "2023-06-12T13:44:37.950000Z"
        assert message["Severity"] == "INFO"
        assert message["Thread"] == "536"
        assert (
            message["Message"]
            == "[inference] Python Executor is starting ... [State Identifier, 1.0.2, ID: 36e03b33-ed16-4a2b-a951-048e4b21e86e]"  # noqa
        )

    def test_build_message_model_distributor_parser_log(self):
        message_factory = MessageFactory()

        message = message_factory.build_message(
            self.model_distributor_parser_log, "blob_name", "source"
        )

        assert message["Timestamp"] == "2023-06-21T00:00:55.618000Z"
        assert message["Severity"] == "DEBUG"
        assert message["Thread"] == "-1"
        assert message["Message"] == "Get log messages"
