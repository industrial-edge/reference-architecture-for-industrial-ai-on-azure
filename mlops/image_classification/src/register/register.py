import mlflow
import argparse
import json
from pathlib import Path

from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(
    model_metadata,
    model_name,
    score_report,
    build_reference,
    mlops_results_path,
):
    try:
        run_file = open(model_metadata)
        model_metadata = json.load(run_file)
        run_uri = model_metadata["run_uri"]

        score_file = open(Path(score_report) / "metrics.json")
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

        logger.info(str(model_version))

        mlops_results = {
            "model_name": model_name,
            "model_version": model_version.version,
        }
        with open(Path(mlops_results_path), "w") as json_file:
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
        "--mlops_results",
        type=str,
        help="UriFile output with results of the model registration",
    )

    args = parser.parse_args()

    main(
        model_metadata=args.model_metadata,
        model_name=args.model_name,
        score_report=args.score_report,
        build_reference=args.build_reference,
        mlops_results_path=args.mlops_results,
    )
