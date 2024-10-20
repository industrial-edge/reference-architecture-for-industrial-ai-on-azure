# Copyright (C) 2023 Siemens AG
# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.
#
# SPDX-License-Identifier: MIT

from log_module import LogModule

logger = LogModule()

import inference  # should adapt to your code

logger.info("entrypoint imported")


def process_input(data: dict):

    return inference.process_data(data)


def update_parameters(params: dict):

    inference.update_parameters(params)
