# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

FROM mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04:latest

COPY *.whl /tmp/
COPY *.yml /tmp/

RUN conda env update -n base -f /tmp/conda.yml
