#!/bin/bash

# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

set -e
BASH_SCRIPT=`readlink -f "$0"`
BASH_DIR=`dirname "$BASH_SCRIPT"`
# Run devcontainer locally without VSCode
docker build -f Dockerfile . -t devcontainer-image:latest
docker run   -it --rm -v ${BASH_DIR}/..:/aeworkspace -u vscode -w /aeworkspace --name devcontainer devcontainer-image:latest bash
