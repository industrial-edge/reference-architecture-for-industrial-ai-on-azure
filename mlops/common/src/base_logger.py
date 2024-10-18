# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import logging
import sys


def get_logger(name_of_module: str):
    """
    Instantiates a logger with default level INFO that outputs to stdout.

    Arguments:
    name_of_module: str
        Name of the module in which the function is called

    Retrun values:
    logger: logging.Logger
        Logger object
    """
    logger = logging.getLogger(name_of_module)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

    return logger
