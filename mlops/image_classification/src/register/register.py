import argparse
import json
from pathlib import Path
import mlflow
from azureml.core import Run

from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(
    model_metadata,
    model_name,
    score_report,
    build_reference,
    azureml_outputs,
):

    run = Run.get_context()
    logger.info(f"run: {run}")

    tracking_uri = run.experiment.workspace.get_mlflow_tracking_uri()
    logger.info(f"tracking_uri: {tracking_uri}")
    logger.info(f"calling set_tracking_uri with {tracking_uri}")
    mlflow.set_tracking_uri(tracking_uri)

    try:

        logger.info("Registering model")

        model_metadata_str = str(Path(model_metadata))
        logger.info(f"Model metadata str: {model_metadata}")

        run_file = open(model_metadata_str)

        logger.info(f"Run file: {run_file}")

        model_metadata = json.load(run_file)
        run_uri = model_metadata["run_uri"]

        score_file_path = str(Path(score_report) / "score.json")
        # logger.info(f"------>>> Score file path: {score_file_path}")

        score_file = open(score_file_path)
        score_data = json.load(score_file)
        macro_avg = score_data["clf_report"]["macro avg"]

        tags = {
            "accuracy": score_data["clf_report"]["accuracy"],
            "avg_precision": macro_avg["precision"],
            "avg_recall": macro_avg["recall"],
            "avg_f1_score": macro_avg["f1-score"],
            "build_id": build_reference,
        }

        model_version = mlflow.register_model(run_uri, model_name)

        client = mlflow.MlflowClient()

        for key, value in tags.items():
            client.set_model_version_tag(
                name=model_name,
                version=model_version.version,
                key=key,
                value=value,
            )

            # logger.info(f"Tag {key} set to {value} for model version {model_version.version}")

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
    parser.add_argument("--score_report", type=str, help="score report for the model")
    parser.add_argument(
        "--build_reference",
        type=str,
        help="Original AzDo build id that initiated experiment",
    )
    parser.add_argument(
        "--azureml_outputs",
        type=str,
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
