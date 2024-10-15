#!/bin/bash

# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

set -e -o pipefail

if ! command -v goimports &> /dev/null ; then
    echo "goimports not installed or available in the PATH" >&2
    exit 1
fi

output="$(goimports -l -w "$@")"

echo "$output"

[[ -z "$output" ]]
