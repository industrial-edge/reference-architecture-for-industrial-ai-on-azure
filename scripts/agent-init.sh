#!/bin/sh

# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

### This script installs the microsoft agent software in the deployed linux VMs for pipeline agents ###

sudo apt-get install gcc
sudo apt-get install build-essential
sudo apt-get install -y wget jq apt-transport-https software-properties-common

# Get the version of Ubuntu
source /etc/os-release

# Download and register the Microsoft repository keys
wget -q https://packages.microsoft.com/config/ubuntu/$VERSION_ID/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
rm packages-microsoft-prod.deb

# Update the list of packages after we added packages.microsoft.com
sudo apt-get update

###################################
# Install PowerShell
sudo apt-get install -y powershell


###################################
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash


###################################
# Install Terraform
sudo apt install unzip
curl -LO "https://releases.hashicorp.com/terraform/1.3.6/terraform_1.3.6_linux_amd64.zip" \
    && unzip -o "terraform_1.3.6_linux_amd64.zip" -d "/usr/local/bin" \
    && chmod +x /usr/local/bin/terraform \
    && rm "terraform_1.3.6_linux_amd64.zip"


###################################
# Creates directory and downloads Azure DevOps agent installation files
sudo mkdir /myagent
cd /myagent
sudo wget https://vstsagentpackage.azureedge.net/agent/2.194.0/vsts-agent-linux-x64-2.194.0.tar.gz
sudo tar zxvf ./vsts-agent-linux-x64-2.194.0.tar.gz
sudo chmod -R 777 /myagent

# Unattended installation
sudo runuser -l ${AGENT_NAME} -c '/myagent/config.sh --unattended  --url ${AZDO_ORG_SERVICE_URL} --auth pat --token ${AZDO_PAT} --pool ${AGENT_POOL}'

cd /myagent
#Configure as a service
sudo ./svc.sh install ${AGENT_NAME}
#Start service
sudo ./svc.sh start
