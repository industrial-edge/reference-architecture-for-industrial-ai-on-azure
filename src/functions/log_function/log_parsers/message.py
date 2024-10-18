# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

from datetime import datetime


class Message(dict):
    def __init__(
        self,
        timestamp: datetime,
        severity: str,
        thread: str,
        workload: str,
        message: str,
        blob_name: str,
        source: str,
    ):
        dict.__init__(
            self,
            Timestamp=timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            Severity=severity,
            Thread=thread,
            Workload=workload,
            Message=message,
            Blob_name=blob_name,
            Source=source,
        )
