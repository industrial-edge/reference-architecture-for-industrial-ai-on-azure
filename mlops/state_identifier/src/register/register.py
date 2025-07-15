import argparse
import json
from pathlib import Path
import mlflow
from azureml.core import Run

from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(
    model_metadata: str,
    model_name: str,
    score_report: str,
    build_reference: str,
    azureml_outputs: str,
):

    lines = [
        f"model_metadata: {model_metadata}",
        f"model_name: {model_name}",
        f"score_report: {score_report}",
        f"build_reference: {build_reference}",
        f"azureml_outputs: {azureml_outputs}",
    ]

    for line in lines:
        logger.info(line)

    run = Run.get_context()
    mlflow.set_tracking_uri(run.experiment.workspace.get_mlflow_tracking_uri())

    try:

        if score_report:
            score_file_path = str(Path(score_report) / "score.json")
            score_file = open(score_file_path)
            score_data = json.load(score_file)

            tags = {
                "silhouette": score_data["silhouette"],
                "dunn_index": score_data["dunn_index"],
                "inertia": score_data["inertia"],
                "build_id": build_reference,
            }

        run_file = open(model_metadata)
        model_metadata = json.load(run_file)
        run_uri = model_metadata["run_uri"]

        model_version = mlflow.register_model(run_uri, model_name)

        client = mlflow.MlflowClient()

        if score_report:
            for key, value in tags.items():
                client.set_model_version_tag(
                    name=model_name,
                    version=model_version.version,
                    key=key,
                    value=value,
                )
                # logger.info(
                #     f"name: {model_name}, version: {model_version.version}, key: {key}, value: {value}"
                # )

        logger.info(str(model_version))

        mlops_results = {
            "model_name": model_name,
            "model_version": model_version.version,
        }

        path_azureml_outputs = str(Path(azureml_outputs))
        logger.info(f"path_azureml_outputs: {path_azureml_outputs}")
        with open(path_azureml_outputs, "w") as json_file:
            json.dump(mlops_results, json_file, indent=4)

    except Exception as ex:
        logger.exception(ex)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser("register_model")
    parser.add_argument(
        "--model_metadata",
        type=str,
        help="model metadata on Machine Learning Workspace",
    )
    parser.add_argument("--model_name", type=str, help="model name to be registered")
    parser.add_argument(
        "--score_report",
        type=str,
        help="file containing metrics",
    )
    parser.add_argument(
        "--build_reference",
        type=str,
        help="Original AzDo build id that initiated experiment",
    )
    parser.add_argument(
        "--azureml_outputs",
        type=str,
        required=False,
        help="UriFile output with results of the model registration",
    )

    args = parser.parse_args()

    main(
        model_metadata=args.model_metadata,
        model_name=args.model_name,
        score_report=args.score_report,
        build_reference=args.build_reference,
        azureml_outputs=args.azureml_outputs,
    )
