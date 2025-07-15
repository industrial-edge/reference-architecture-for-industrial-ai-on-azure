#!/bin/bash
set -e

echo "Running onCreateCommand.sh ..."

# git config
# mkdir -p /home/$(id -un)/.ssh
# touch /home/$(id -un)/.ssh/config

# pip install -r /tmp/pip-tmp/requirements.txt


# Allow docker to be run as non-root
# sudo chmod 666 /var/run/docker.sock

# Install goimports tool
# go install -v golang.org/x/tools/cmd/goimports@latest

# pre-commit install
repoRoot="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
if [[ ! -f "$repoRoot"/.git/hooks/pre-commit ]] ;
then
     pre-commit install
fi

# adding pathes to parents of Python modules
echo  'export PATH=${PATH}:/home/vscode/bin:/home/vscode/.local/bin:/aeworkspace:/aeworkspace/mlops:/usr/local/go/bin:/home/vscode/go/bin' >> ~/.bashrc
echo  'export PYTHONPATH=${PYTHONPATH}:/aeworkspace:/aeworkspace/mlops' >> ~/.bashrc

# echo "alias python3=python3.11" >> ~/.bashrc

echo 'source /usr/share/bash-completion/completions/git' >> /home/vscode/.bashrc

# find . -name "requirements.txt" -exec cat {} \; | tee /tmp/combined_requirements.txt | pip install -r /tmp/combined_requirements.txt && rm /tmp/combined_requirements.txt
