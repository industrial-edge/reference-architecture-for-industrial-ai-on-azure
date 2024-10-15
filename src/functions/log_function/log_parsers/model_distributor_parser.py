# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import re

from datetime import datetime
from .base_parser import BaseParser
from .message import Message
from .regexes import Regexes


class ModelDistributorParser(BaseParser):
    def can_parse(self, log_string: str) -> bool:
        matches = re.search(Regexes.created_on_regex, log_string)
        return matches is not None

    def parse(self, log_string: str, blob_name: str, source: str) -> Message:
        timestamp_matches = re.search(Regexes.created_on_regex, log_string)

        if timestamp_matches is not None:
            timestamp = timestamp_matches.group().replace("[", "").replace("]", "")
            remainder = re.split(Regexes.created_on_regex, log_string)[1]
        else:
            timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            remainder = log_string

        level_matches = re.search(Regexes.level_regex, remainder)
        if level_matches is not None:
            level = (
                level_matches.group().replace('"level":', "").replace('"', "").upper()
            )
            remainder = re.split(Regexes.level_regex, remainder)[2]
        else:
            level = "UNKNOWN"

        thread = "-1"

        message_matches = re.search(
            Regexes.model_distributor_message_regex, remainder, re.IGNORECASE
        )

        if message_matches is not None:
            message = (
                message_matches.group()
                .replace(
                    '"message":',
                    "",
                )
                .replace('"', "")
                .strip()
            )
        else:
            message = remainder.strip()

        return Message(
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ"),
            level,
            thread,
            "Model Distributor",
            message,
            blob_name,
            source,
        )
