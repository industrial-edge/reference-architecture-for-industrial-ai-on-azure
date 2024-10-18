# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

from abc import abstractmethod
from .message import Message


class BaseParser:
    @abstractmethod
    def can_parse(self, log_string: str) -> bool:
        pass

    @abstractmethod
    def parse(self, log_string: str, blob_name: str, source: str) -> Message:
        pass

    def _get_severity_string(self, severity: str):
        if severity == "[I]":
            severity = "INFO"
        elif severity == "[W]":
            severity = "WARNING"
        elif severity == "[E]":
            severity = "ERROR"
        elif severity == "[C]":
            severity = "CRITICAL"
        elif severity == "[D]":
            severity = "DEBUG"
        return severity
