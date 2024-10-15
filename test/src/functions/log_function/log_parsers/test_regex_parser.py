import unittest

from datetime import datetime

from src.functions.log_function.log_parsers.regex_parser import RegexParser


class TestRegexParser(unittest.TestCase):

    # Executor sample log strings
    test_log1 = "[2023-06-12T13:44:37.950Z] [Log] [I] [thread 536] [inference] Python Executor is starting ... [State Identifier, 1.0.2, ID: 36e03b33-ed16-4a2b-a951-048e4b21e86e]"  # noqa
    test_log2 = (
        "[2023-06-12T13:44:37.787Z] [Log] [I] [thread 536] AI Python Runtime v1.4.0"
    )
    test_log3 = "[GCC 10.2.1 20210110]"
    test_log4 = "[2023-06-12T13:44:37.948Z] [Log] [I] [thread 536] YamlVesselConfigReader::fromFile. Pathname: /usr/sail/./runtime/cbe34fd8-b1d7-442c-b9de-9e884c464213/inference/1.0.0/inference_1.0.0.yaml"  # noqa
    test_log5 = '[2023-06-12T13:44:41.668Z] [Log] [I] [thread 668] [PreModelMonitor] [PY] [simaticai/runtime/monitoring/outputs.py] [Monitoring][PreModelMonitor] Data Quality Monitoring succeed. Output: {"ph1": 4.2, "ph2": 4.2, "ph3": 4.2, "timestamp": "2023-06-12T13:44:40.896Z", "number_of_missing_properties": "{\\"value\\": 0}", "number_of_data_type_errors": "{\\"value\\": 0}", "ratio_of_numerical_out_of_domain_features": "{\\"value\\": 1.0}", "ratio_of_numerical_outlier_features": "{\\"value\\": 0.0}", "ratio_of_categorical_out_of_domain_features": "{\\"value\\": 0}", "validity_flag": false} [State Identifier, 1.0.2, ID: 36e03b33-ed16-4a2b-a951-048e4b21e86e]'  # noqa

    # Maestro API sample log strings
    test_log6 = "[2023-06-21T00:01:00.019Z] [I] [Message: Remove old log files on path /usr/sail/logs/maestro_api/]"  # noqa
    test_log7 = "[2023-06-21T00:01:00.032Z] [I] [Message: Deleting file] [Extra Info: /usr/sail/logs/maestro_api/logfile_2023-05-22, ]"  # noqa

    # ModelDistributor sample log strings
    test_log8 = '{"createdOn":"2023-06-21T00:00:55.618Z","level":"debug","message":"Get log messages"}'  # noqa

    # Runtime Manager sample log strings
    test_log9 = "[2023-06-21T09:01:51.249Z] [Log] [I] [thread 10] Cleaned model version 1.0.0 from directory: /usr/sail/./runtime/715d6aec-ff83-4044-9091-0249bd3a68ed/inference/1.0.0"  # noqa

    def test_can_parse_return_true_for_test_log1(self):
        parser = RegexParser()
        assert parser.can_parse(self.test_log1)

    def test_can_parse_return_true_for_test_log2(self):
        parser = RegexParser()
        assert parser.can_parse(self.test_log2)

    def test_can_parse_return_false_for_test_log3(self):
        parser = RegexParser()
        assert parser.can_parse(self.test_log3) is False

    def test_can_parse_return_true_for_test_log4(self):
        parser = RegexParser()
        assert parser.can_parse(self.test_log4)

    def test_can_parse_return_true_for_test_log5(self):
        parser = RegexParser()
        assert parser.can_parse(self.test_log5)

    def test_can_parse_return_true_for_test_log6(self):
        parser = RegexParser()
        assert parser.can_parse(self.test_log6)

    def test_can_parse_return_true_for_test_log7(self):
        parser = RegexParser()
        assert parser.can_parse(self.test_log7)

    def test_can_parse_return_false_for_test_log8(self):
        parser = RegexParser()
        assert parser.can_parse(self.test_log8) is False

    def test_can_parse_return_true_for_test_log9(self):
        parser = RegexParser()
        assert parser.can_parse(self.test_log9)

    def test_parse_correctly_parses_test_log1(self):
        parser = RegexParser()
        message = parser.parse(self.test_log1, "blob", "source")

        assert message["Timestamp"] == "2023-06-12T13:44:37.950000Z"
        assert message["Severity"] == "INFO"
        assert message["Thread"] == "536"
        assert (
            message["Message"]
            == "[inference] Python Executor is starting ... [State Identifier, 1.0.2, ID: 36e03b33-ed16-4a2b-a951-048e4b21e86e]"  # noqa
        )

    def test_parse_correctly_parses_test_log2(self):
        parser = RegexParser()

        message = parser.parse(self.test_log2, "blob", "source")

        assert message["Timestamp"] == "2023-06-12T13:44:37.787000Z"
        assert message["Severity"] == "INFO"
        assert message["Thread"] == "536"
        assert message["Message"] == "AI Python Runtime v1.4.0"

    def test_parse_correctly_parses_test_log3(self):
        parser = RegexParser()

        message = parser.parse(self.test_log3, "blob", "source")

        # Cannot parse this string, so dumps the whole string into the message
        # Sets defaults for other fields.
        assert message["Message"] == self.test_log3
        assert message["Severity"] == "UNKNOWN"
        assert message["Thread"] == "-1"

        # Can't check exact time, but it should have been set to utc now, so at
        # least check the date component.
        assert datetime.utcnow().strftime("%Y-%m-%dT") in message["Timestamp"]

    def test_parse_correctly_parses_test_log4(self):
        parser = RegexParser()

        message = parser.parse(self.test_log4, "blob", "source")

        assert message["Timestamp"] == "2023-06-12T13:44:37.948000Z"
        assert message["Severity"] == "INFO"
        assert message["Thread"] == "536"
        assert (
            message["Message"]
            == "YamlVesselConfigReader::fromFile. Pathname: /usr/sail/./runtime/cbe34fd8-b1d7-442c-b9de-9e884c464213/inference/1.0.0/inference_1.0.0.yaml"  # noqa
        )  # noqa

    def test_parse_correctly_parses_test_log5(self):
        parser = RegexParser()

        message = parser.parse(self.test_log5, "blob", "source")

        assert message["Timestamp"] == "2023-06-12T13:44:41.668000Z"
        assert message["Severity"] == "INFO"
        assert message["Thread"] == "668"
        assert (
            message["Message"]
            == '[PreModelMonitor] [PY] [simaticai/runtime/monitoring/outputs.py] [Monitoring][PreModelMonitor] Data Quality Monitoring succeed. Output: {"ph1": 4.2, "ph2": 4.2, "ph3": 4.2, "timestamp": "2023-06-12T13:44:40.896Z", "number_of_missing_properties": "{\\"value\\": 0}", "number_of_data_type_errors": "{\\"value\\": 0}", "ratio_of_numerical_out_of_domain_features": "{\\"value\\": 1.0}", "ratio_of_numerical_outlier_features": "{\\"value\\": 0.0}", "ratio_of_categorical_out_of_domain_features": "{\\"value\\": 0}", "validity_flag": false} [State Identifier, 1.0.2, ID: 36e03b33-ed16-4a2b-a951-048e4b21e86e]'  # noqa
        )  # noqa

    def test_parse_correctly_parses_test_log6(self):
        parser = RegexParser()

        message = parser.parse(self.test_log6, "blob", "source")

        assert message["Timestamp"] == "2023-06-21T00:01:00.019000Z"
        assert message["Severity"] == "INFO"
        assert message["Thread"] == "-1"
        assert (
            message["Message"]
            == "Remove old log files on path /usr/sail/logs/maestro_api/]"
        )

    def test_parse_correctly_parses_test_log7(self):
        parser = RegexParser()

        message = parser.parse(self.test_log7, "blob", "source")

        assert message["Timestamp"] == "2023-06-21T00:01:00.032000Z"
        assert message["Severity"] == "INFO"
        assert message["Thread"] == "-1"
        assert (
            message["Message"]
            == "Deleting file] [Extra Info: /usr/sail/logs/maestro_api/logfile_2023-05-22, ]"  # noqa
        )

    def test_parse_correctly_parses_test_log8(self):
        parser = RegexParser()

        message = parser.parse(self.test_log8, "blob", "source")

        # Cannot parse this string, so dumps the whole string into the message
        # Sets defaults for other fields.
        assert message["Message"] == self.test_log8
        assert message["Severity"] == "UNKNOWN"
        assert message["Thread"] == "-1"

        # Can't check exact time, but it should have been set to utc now, so at
        # least check the date component.
        assert datetime.utcnow().strftime("%Y-%m-%dT") in message["Timestamp"]

    def test_parse_correctly_parses_test_log9(self):
        parser = RegexParser()

        message = parser.parse(self.test_log9, "blob", "source")

        assert message["Timestamp"] == "2023-06-21T09:01:51.249000Z"
        assert message["Severity"] == "INFO"
        assert message["Thread"] == "10"
        assert (
            message["Message"]
            == "Cleaned model version 1.0.0 from directory: /usr/sail/./runtime/715d6aec-ff83-4044-9091-0249bd3a68ed/inference/1.0.0"  # noqa
        )
