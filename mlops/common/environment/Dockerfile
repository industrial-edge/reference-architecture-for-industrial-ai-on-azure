FROM mcr.microsoft.com/azureml/openmpi5.0-ubuntu24.04:20250217.v1

COPY *.yml /tmp/

RUN conda env update -n base -f /tmp/delivery_conda.yml
