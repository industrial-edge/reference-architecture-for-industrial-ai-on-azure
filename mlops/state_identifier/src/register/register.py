# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import json
import os
import pickle
from pathlib import Path

import mlflow
from common.src.base_logger import get_logger
from joblib import load
from sklearn.pipeline import Pipeline

logger = get_logger(__name__)


def main(
    model_name: str,
    score_report: str,
    build_reference: str,
    preparation_pipeline_path: str,
    model: str,
    mlops_results_path: str,
):
    try:
        score_file = open(Path(score_report) / "score.txt")
        score_data = json.load(score_file)
        silhouette = score_data["silhouette"]
        dunn_index = score_data["dunn_index"]
        inertia = score_data["inertia"]

        model = pickle.load(open((Path(model) / "model.sav"), "rb"))

        data_transformation_pipeline = load(
            (Path(preparation_pipeline_path) / "preparation_pipeline.joblib")
        )

        sklearn_pipeline = Pipeline(
            [("preprocessing", data_transformation_pipeline), ("clustering", model)]
        )

        with mlflow.start_run(run_id=os.environ["AZUREML_ROOT_RUN_ID"], nested=True):
            mlflow.sklearn.log_model(sklearn_pipeline, model_name)

            run_id = mlflow.active_run().info.run_id

            run_uri = f"runs:/{run_id}/{model_name}"

            model_version = mlflow.register_model(run_uri, model_name)

            client = mlflow.MlflowClient()
            client.set_model_version_tag(
                name=model_name,
                version=model_version.version,
                key="silhouette",
                value=silhouette,
            )
            client.set_model_version_tag(
                name=model_name,
                version=model_version.version,
                key="dunn_index",
                value=dunn_index,
            )
            client.set_model_version_tag(
                name=model_name,
                version=model_version.version,
                key="inertia",
                value=inertia,
            )

            client.set_model_version_tag(
                name=model_name,
                version=model_version.version,
                key="build_id",
                value=build_reference,
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
        "--preparation_pipeline_path",
        type=str,
        help="Path to the folder where the pipeline is stored",
    )
    parser.add_argument("--model", type=str, help="Path to model")
    parser.add_argument(
        "--mlops_results",
        type=str,
        help="UriFile output with results of the model registration",
    )

    args = parser.parse_args()

    main(
        model_name=args.model_name,
        score_report=args.score_report,
        build_reference=args.build_reference,
        preparation_pipeline_path=args.preparation_pipeline_path,
        model=args.model,
        mlops_results_path=args.mlops_results,
    )
