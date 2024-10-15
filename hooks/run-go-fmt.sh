#!/bin/bash

# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

set -e -o pipefail

if ! command -v gofmt &> /dev/null ; then
    echo "gofmt not installed or available in the PATH" >&2
    exit 1
fi

output="$(gofmt -l -w "$@")"

echo "$output"

[[ -z "$output" ]]
