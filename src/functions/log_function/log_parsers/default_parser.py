# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

from .base_parser import BaseParser
from .message import Message

from datetime import datetime


class DefaultParser(BaseParser):
    def can_parse(self, log_string: str) -> bool:
        return True

    def parse(self, log_string: str, blob_name: str, source: str) -> Message:
        return Message(datetime.utcnow(), "", "0", "", log_string, blob_name, source)
