<!--
Copyright (C) 2023 Siemens AG

SPDX-License-Identifier: MIT
-->

## Getting started

### Cloning the repository
To clone the repository you could use ssh or https link

```
# using SSH
git clone git@github.com:industrial-edge/reference-architecture-for-industrial-ai-on-azure.git

# or HTTPs
git clone https://github.com/industrial-edge/reference-architecture-for-industrial-ai-on-azure.git
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
