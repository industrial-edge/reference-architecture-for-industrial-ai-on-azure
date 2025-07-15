FROM mcr.microsoft.com/azureml/openmpi5.0-ubuntu24.04:20250217.v1

COPY *.whl /tmp/
COPY *.yml /tmp/

RUN conda env update -n base -f /tmp/conda.yml \
    && conda run -n base pip install /tmp/simaticai-2.4.0-py3-none-any.whl
