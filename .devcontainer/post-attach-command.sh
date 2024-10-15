#!/bin/bash

# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

set -e

# git config
mkdir -p /home/$(id -un)/.ssh
touch /home/$(id -un)/.ssh/config

sudo chown -R vscode:vscode /var/run/docker.sock
sudo chown -R vscode:vscode /content

# Install goimports tool
go install -v golang.org/x/tools/cmd/goimports@latest

# pre-commit install
repoRoot="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
if [[ ! -f "$repoRoot"/.git/hooks/pre-commit ]] ;
then
     pre-commit install
fi

# adding pathes to parents of Python modules
echo  'export PATH=${PATH}:/home/vscode/bin:/home/vscode/.local/bin:/aeworkspace:/aeworkspace/mlops' >> ~/.bashrc
echo  'export PYTHONPATH=${PYTHONPATH}:/aeworkspace:/aeworkspace/mlops' >> ~/.bashrc
