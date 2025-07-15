import argparse

from mlops.common.src.base_logger import get_logger
from mlops.common.pipeline.get_compute import get_compute, compute_argument_parser
from mlops.common.pipeline.get_environment import (
    get_environment,
    environment_argument_parser,
)
from mlops.common.pipeline.pipeline_execution_utils import execute_pipeline

logger = get_logger(__name__)


class ArgRunner:
    def __init__(self):
        self.parser = argparse.ArgumentParser("build_environment")

        compute_argument_parser(self.parser)
        environment_argument_parser(self.parser)
        self.common_argument_parser()

    def add_arg(self, arg_name, **kwargs):
        logger.info("Adding argument %s", arg_name)
        if not any(
            arg_name in action.option_strings for action in self.parser._actions
        ):
            self.parser.add_argument(arg_name, **kwargs)

    def common_argument_parser(self):
        self.add_arg(
            "--build_reference",
            type=str,
            help="Unique identifier for Azure DevOps pipeline run",
        )
        self.add_arg(
            "--deploy_environment",
            type=str,
            help="execution and deployment environment. e.g. dev, prod, test",
        )
        self.add_arg(
            "--experiment_name", type=str, help="Job execution experiment name"
        )
        self.add_arg("--display_name", type=str, help="Job execution run name")
        self.add_arg(
            "--wait_for_completion",
            type=str,
            help="determine if pipeline to wait for job completion",
        )
        self.add_arg(
            "--output_file", type=str, required=False, help="A file to save run id"
        )
        self.add_arg(
            "--azureml_outputs",
            type=str,
            required=False,
            help="A file to save run id with results",
            default=None,
        )

    def prepare_and_execute(self, construct_pipeline):

        args = self.parser.parse_args()

        compute = get_compute(args)
        logger.info("Compute name {%s}", compute.name)

        environment = get_environment(args)
        logger.info(f"Environment: {environment.name}, version: {environment.version}")

        pipeline_job = construct_pipeline(args, compute, environment)

        execute_pipeline(args, pipeline_job)
