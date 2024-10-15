<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

# Azure Enablement

The project is managed on Azure Devops at
- [Project overview on Azure DevOps](https://dev.azure.com/siemens-microsoft-iai/Siemens-Microsoft-IAI/)

Actual Sprint backlog is available on page
- [Actual Sprint backlog](https://dev.azure.com/siemens-microsoft-iai/Siemens-Microsoft-IAI/_sprints/backlog/Siemens-Microsoft-IAI%20Team/Siemens-Microsoft-IAI/)

We are using Azure Subscription **msa-001298** at
- [Azure Subscription msa-001298](https://portal.azure.com/#@siemens.onmicrosoft.com/resource/subscriptions/6f90d3be-aca6-4312-b4bc-d1d8dd8e65e4/overview)

Design decisions are documented on the
- [Project Wiki](https://dev.azure.com/siemens-microsoft-iai/Siemens-Microsoft-IAI/_wiki/wikis/Siemens-Microsoft-IAI.wiki/1/Design-Decisions)

## Getting started

### Cloning the repository
To clone the repository you could use ssh or https link

```
# using SSH
git clone git@code.siemens.com:di-fa-industrial-ai/partners/microsoft/azure-enablement/azure-enablement.git

# or HTTPs
git clone https://code.siemens.com/di-fa-industrial-ai/partners/microsoft/azure-enablement/azure-enablement.git
```

### Developing inside Dev Container
The repository contains .devcontainer/devcontainer.json file that sets up and configures your development container.

To use DevContainers from Windows host started through WSL2 (without Docker Desktop) there are some extra steps required to get  
the devcontainer running. Add this line to settings.json of vscode, which will execute the container build process inside a WSL session:  
`"dev.containers.executeInWSL": true`

At the end of the dev container build process the .ssh folder of the default WSL user is bind mounted into the dev container
to enable access to the repository, but this step fails because DevContainers started through WSL2 do not see environment variables.
To workaround this create a symlink to the user's .ssh folder at the root of the WSL filesystem:
```
sudo ln -s ~/.ssh /.ssh
```
## Contribution

Thank you for your interest in contributing. Anybody is free to report bugs, unclear documentation, and other problems regarding this repository in the Issues section.
Additionally everybody is free to propose any changes to this repository using Pull Requests.

If you haven't previously signed the [Siemens Contributor License Agreement](https://cla-assistant.io/industrial-edge/) (CLA), the system will automatically prompt you to do so when you submit your Pull Request. This can be conveniently done through the CLA Assistant's online platform. Once the CLA is signed, your Pull Request will automatically be cleared and made ready for merging if all other test stages succeed.

## License and Legal Information

Please read the [Legal information](LICENSE.md).
