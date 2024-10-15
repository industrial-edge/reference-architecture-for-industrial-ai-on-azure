# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.238.0/containers/python-3/.devcontainer/base.Dockerfile
# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.8-bullseye"
FROM --platform=linux/amd64 mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}
# ARG TERRAGRUNT_VERSION="0.42.2"
ARG TERRAGRUNT_VERSION="0.57.13"
ARG GO_VERSION="1.19.3"

# If your pip requirements rarely change, uncomment this section to add them to the image.
RUN /usr/local/bin/python -m pip install --proxy $HTTP_PROXY --upgrade pip
COPY ./.devcontainer/requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir --proxy=$HTTP_PROXY install -r /tmp/pip-tmp/requirements.txt \
#     && rm -rf /tmp/pip-tmp
RUN pip install --proxy $HTTP_PROXY -r /tmp/pip-tmp/requirements.txt
# RUN pip3 install --proxy=$HTTP_PROXY -r /tmp/pip-tmp/requirements.txt
RUN rm -rf /tmp/pip-tmp

# install npm, typscript, webpack
RUN apt-get update \
    && apt-get install -y git

# Install Azure CLI
RUN  curl -sL https://aka.ms/InstallAzureCLIDeb  | bash

# Install Docker CLI
RUN apt-get update \
    && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    dnsutils
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Docker version for bullseye not yet available fall back to eoan
# RUN echo \
#  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
#  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  eoan stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN  apt-get update \
      && apt-get install -y docker-ce-cli

# install Go
RUN curl -OL https://golang.org/dl/go"${GO_VERSION}".linux-amd64.tar.gz
RUN tar -C /usr/local -xvf go"${GO_VERSION}".linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin:/home/vscode/go/bin

## Install Azure func tools
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg \
    && mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg \
    && sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/debian/$(lsb_release -rs | cut -d'.' -f 1)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends cmake dos2unix

# install shellcheck
RUN wget -qO- "https://github.com/koalaman/shellcheck/releases/download/stable/shellcheck-stable.linux.x86_64.tar.xz" | tar -xJv \
    && mv "shellcheck-stable/shellcheck" /usr/bin/ \
    && rm -r "shellcheck-stable"

# # Install Terraform-docs
RUN curl -sSLo ./terraform-docs.tar.gz "https://terraform-docs.io/dl/v0.16.0/terraform-docs-v0.16.0-linux-amd64.tar.gz" \
    && tar -xzf terraform-docs.tar.gz \
    && chmod +x terraform-docs \
    && mv terraform-docs /usr/local/bin/terraform-docs

# Install OpenTofu
RUN curl -LO https://github.com/opentofu/opentofu/releases/download/v1.6.2/tofu_1.6.2_amd64.deb \
    && dpkg -i tofu_1.6.2_amd64.deb \
    && rm tofu_1.6.2_amd64.deb

# Install Terragrunt
RUN curl -LO "https://github.com/gruntwork-io/terragrunt/releases/download/v${TERRAGRUNT_VERSION}/terragrunt_linux_amd64" \
    && mv -f "terragrunt_linux_amd64" "/usr/local/bin/terragrunt" \
    && chmod +x /usr/local/bin/terragrunt

RUN echo 'source /usr/share/bash-completion/completions/git' >> /home/vscode/.bashrc
