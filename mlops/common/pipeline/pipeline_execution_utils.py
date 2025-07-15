# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

import time
from typing import List
from pathlib import Path

from azure.ai.ml import MLClient
from azure.ai.ml.dsl import pipeline
from azure.identity import DefaultAzureCredential

from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)


def execute_pipeline(args: dict, pipeline_job: pipeline):

    azureml_outputs = None
    if args.azureml_outputs is None:
        azureml_outputs = [args.azureml_outputs]

    execute(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.experiment_name,
        pipeline_job,
        args.wait_for_completion,
        args.output_file,
        azureml_outputs,
    )


def execute(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    experiment_name: str,
    pipeline_job: pipeline,
    wait_for_completion: str,
    output_file: str = None,
    azureml_outputs: List[str] = None,
):
    """
    Executes an Azure Machine Learning pipeline job and optionally waits for completion.

    Arguments:
    subscription_id : str
        The ID of the Azure subscription.
    resource_group_name : str
        The name of the Azure resource group.
    workspace_name : str
        The name of the Azure Machine Learning workspace.
    experiment_name : str
        The name of the experiment associated with the pipeline job.
    pipeline_job : pipeline
        The pipeline job to be executed.
    wait_for_completion : str
        If "True", the function will wait for the pipeline to complete before returning.
    output_file : str
        The path of a file where the pipeline job name will be written.

    Returns:
        None
    """
    try:
        logger.info("Started execution")
        client = MLClient(
            DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )
        logger.info(f"Experiment name {experiment_name}")
        pipeline_job = client.jobs.create_or_update(
            pipeline_job, experiment_name=experiment_name
        )

        logger.info(f"The job {pipeline_job.name} has been submitted!")
        if output_file is not None:
            with open(output_file, "w", encoding="utf-8") as out_file:
                out_file.write(f"job_id={pipeline_job.name}\n")

        if wait_for_completion == "True":
            wait_for_pipeline_completion(pipeline_job, azureml_outputs, client)

    except Exception as _e:
        logger.critical(f"Error occurred while creating ML environment..\n{_e}")
        raise _e


def wait_for_pipeline_completion(pipeline_job, azureml_outputs, client):
    total_wait_time = 3600
    current_wait_time = 0
    job_status = [
        "NotStarted",
        "Queued",
        "Starting",
        "Preparing",
        "Running",
        "Finalizing",
        "Provisioning",
        "CancelRequested",
        "Failed",
        "Canceled",
        "NotResponding",
    ]

    try:
        while pipeline_job.status in job_status:
            if current_wait_time > total_wait_time:
                break

            time.sleep(20)
            pipeline_job = client.jobs.get(pipeline_job.name)

            logger.info(f"Job Status: {str(pipeline_job.status)}")

            current_wait_time = current_wait_time + 15

            if pipeline_job.status in [
                "Failed",
                "NotResponding",
                "CancelRequested",
                "Canceled",
            ]:
                break

        if pipeline_job.status in ["Completed", "Finished"]:
            logger.info("job completed, downloading outputs if any...")
            if azureml_outputs is not None:
                for output_name in azureml_outputs or []:
                    download_output(client, pipeline_job.name, output_name)
        else:
            raise RuntimeError("Sorry, exiting job with failure..")

    except Exception as _e:
        logger.critical(f"Error occurred while waiting for pipeline completion..\n{_e}")
        raise _e


def download_output(ml_client: MLClient, pipeline_job_name: str, output_name: str):
    """
    Downloads the outputs of the AzureML job, if any, and writes them to an output file

    Arguments:
    ml_client: MLClient
        The ML CLient connected to the AzureML workspace
    pipeline_job_name: str
        Name of the pipeline for which we want to download the results.
    output_name: str
        Path to the file where the results will be written.

    Returns:
        None
    """
    if output_name:
        logger.info(f"downloading {output_name} output of {pipeline_job_name} pipeline")
        ml_client.jobs.download(name=pipeline_job_name, output_name=output_name)

        output_folder = Path(f"named-outputs/{output_name}")
        download_timeout = time.time() + 60 * 5  # 5 minutes from now
        retry_timeout = time.time() + 30  # 30 sec from now
        wait_step = 10  # sec

        while time.time() < download_timeout:
            files = [f for f in output_folder.glob("**/*") if f.is_file()]
            logger.info(f"files under {output_folder.resolve()} subtree: {files}")

            if files:
                # Files have been downloaded, exit the loop
                break

            if time.time() > retry_timeout:
                ml_client.jobs.download(name=pipeline_job_name, output_name=output_name)
                retry_timeout = time.time() + 30  # 30 sec from now

            time.sleep(wait_step)
    else:
        logger.info("No outputs to be downloaded.")
