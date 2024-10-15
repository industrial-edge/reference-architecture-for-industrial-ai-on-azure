REM Run devcontainer locally without VSCode
docker build -f Dockerfile . -t devcontainer-image:latest
docker run   -it --rm -v %~dp0/..:/aeworkspace -u vscode -w /aeworkspace --name devcontainer devcontainer-image:latest bash
