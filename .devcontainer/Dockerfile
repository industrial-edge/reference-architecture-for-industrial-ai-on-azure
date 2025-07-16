# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.238.0/containers/python-3/.devcontainer/base.Dockerfile
# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.12-bullseye"
ARG PLATFORM="amd64"
# ARG PLATFORM="arm64"
FROM --platform=linux/${PLATFORM} mcr.microsoft.com/devcontainers/python:0-3.11-bullseye


RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends cmake dos2unix \
    ca-certificates \
    gnupg \
    lsb-release \
    dnsutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y gnupg dirmngr curl git ca-certificates gnupg lsb-release cmake dos2unix --no-install-recommends && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# # If your pip requirements rarely change, uncomment this section to add them to the image.
RUN mkdir -p /tmp/pip-tmp
COPY ./.devcontainer/requirements.txt /tmp/pip-tmp/
RUN python -m pip install --upgrade pip \
    && pip install --disable-pip-version-check --no-cache-dir -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp


RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

RUN curl -fsSL https://get.opentofu.org/install.sh | bash


ARG TERRAFORM_DOCS_VERSION=0.20.0

RUN curl -sSLo terraform-docs.tar.gz "https://github.com/terraform-docs/terraform-docs/releases/download/v${TERRAFORM_DOCS_VERSION}/terraform-docs-v${TERRAFORM_DOCS_VERSION}-linux-amd64.tar.gz" \
    && tar -xzf terraform-docs.tar.gz \
    && mv terraform-docs /usr/local/bin/terraform-docs \
    && chmod +x /usr/local/bin/terraform-docs \
    && rm terraform-docs.tar.gz


# Install OpenTofu
ENV OPENTOFU_VERSION=1.9.1

RUN curl -LO "https://github.com/opentofu/opentofu/releases/download/v${OPENTOFU_VERSION}/tofu_${OPENTOFU_VERSION}_amd64.deb" \
    && dpkg -i "tofu_${OPENTOFU_VERSION}_amd64.deb" \
    && rm "tofu_${OPENTOFU_VERSION}_amd64.deb"



# Install Go
ARG GO_VERSION=1.19

# Install Go
RUN curl -k -OL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" \
    && rm -rf /usr/local/go \
    && tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz" \
    && rm "go${GO_VERSION}.linux-amd64.tar.gz"

# Add Go to the PATH
ENV PATH="/usr/local/go/bin:/home/vscode/go/bin:${PATH}"
