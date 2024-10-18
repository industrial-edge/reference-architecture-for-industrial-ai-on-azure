REM SPDX-FileCopyrightText: Copyright (C) 2023 Siemens AG
REM SPDX-License-Identifier: MIT
REM Run devcontainer locally without VSCode
docker build -f Dockerfile . -t devcontainer-image:latest
docker run   -it --rm -v %~dp0/..:/aeworkspace -u vscode -w /aeworkspace --name devcontainer devcontainer-image:latest bash
