# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import re

from datetime import datetime
from .base_parser import BaseParser
from .message import Message
from .regexes import Regexes


class RegexParser(BaseParser):
    def __init__(self) -> None:
        regexes = [
            Regexes.iso_datetime_regex,
            Regexes.severity_regex,
            Regexes.thread_regex,
        ]
        self._regex = re.compile("|".join(r for r in regexes))

    def can_parse(self, log_string: str) -> bool:
        matches = re.search(self._regex, log_string)
        return matches is not None

    def parse(self, log_string: str, blob_name: str, source: str) -> Message:

        timestamp_matches = re.search(Regexes.iso_datetime_regex, log_string)

        if timestamp_matches is not None:
            timestamp = timestamp_matches.group().replace("[", "").replace("]", "")
            remainder = re.split(Regexes.iso_datetime_regex, log_string)[1]
        else:
            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            remainder = log_string

        severity_matches = re.search(Regexes.severity_regex, remainder)

        if severity_matches is not None:
            severity = severity_matches.group()
            remainder = re.split(Regexes.severity_regex, remainder)[1]
        else:
            severity = "UNKNOWN"

        thread_matches = re.search(Regexes.thread_regex, remainder)

        if thread_matches is not None:
            thread = thread_matches.group().replace("[thread ", "").replace("]", "")
            remainder = re.split(Regexes.thread_regex, remainder)[1]
        else:
            thread = "-1"

        message_matches = re.search(Regexes.message_regex, remainder, re.IGNORECASE)

        if message_matches is not None:
            message = (
                message_matches.group()
                .replace(
                    "message:",
                    "",
                )
                .replace(
                    "Message:",
                    "",
                )
                .strip()
            )
        else:
            message = remainder.strip()

        return Message(
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"),
            self._get_severity_string(severity),
            thread,
            "",
            message,
            blob_name,
            source,
        )
