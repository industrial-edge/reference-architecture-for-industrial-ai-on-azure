# SPDX-FileCopyrightText: 2025 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import json
from pathlib import Path
import joblib
import mlflow
import numpy as np
import pandas
from sklearn.metrics import silhouette_score
from state_identifier.src.score.scoring_utils import dunn_index
from sklearn.pipeline import Pipeline
from state_identifier.src.si.preprocessing import (
    SumColumnsTransformer,
)
from azureml.core import Run

from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(raw_data: str, prep_data: str, model: str, score_report: str):

    run = Run.get_context()
    mlflow.set_tracking_uri(run.experiment.workspace.get_mlflow_tracking_uri())
    mlflow.autolog()

    with mlflow.start_run():

        lines = [
            f"raw_data path: {raw_data}",
            f"prep_data path: {prep_data}",
            f"model path: {model}",
            f"Scoring output path: {score_report}",
        ]

        for line in lines:
            logger.info(line)

        # Load the model
        models_file_path = Path(model) / "models" / "clustering-model.joblib"
        logger.info(f"models_file_path: {models_file_path}")
        model_instance = joblib.load(models_file_path)
        logger.info(f"Pipeline steps: {model_instance.named_steps.keys()}")

        # prepare data
        raw_data_frame = pandas.read_parquet(raw_data)

        input_columns = ["ph1", "ph2", "ph3"]
        raw_data_frame["ph_sum"] = (
            SumColumnsTransformer()
            .transform(raw_data_frame[input_columns].values)
            .flatten()
        )

        data_preparation_pipeline = model_instance.named_steps["preprocessing"]

        raw_data_numpy_filtered = raw_data_frame[input_columns].values
        data_preparation_pipeline.fit(raw_data_numpy_filtered)

        transformed_data = data_preparation_pipeline.transform(raw_data_numpy_filtered)
        transformed_data_frame = pandas.DataFrame(transformed_data)

        write_results(model_instance, transformed_data_frame, score_report)


def write_results(model: Pipeline, prep_data: np.array, score_report: str) -> None:
    """
    Log clustering metrics for a trained model and write them to a file.

    Arguments:
    model: KMeans
        A trained model object.
    prep_data: np.array
        The data that the model was trained on.
    score_report: str
        The directory where the score report should be written. The scores will be written
        to a file named 'score.txt' in this directory.

    Returns:
    None
        The resulting metrics are written to mlflow and to a text file.
    """

    logger.info(f"model: {model}")
    logger.info(f"prep_data: {prep_data}")

    kmeans_clustering = model.named_steps["clustering"]

    labels = kmeans_clustering.labels_
    logger.info(f"labels: {labels}")

    silhouette_score_value = silhouette_score(prep_data, labels)
    mlflow.log_metric("silhouette", silhouette_score_value)
    logger.info(f"silhouette: {silhouette_score_value}")

    dunn_index_value = dunn_index(prep_data, labels)
    mlflow.log_metric("dunn_index", dunn_index_value)
    logger.info(f"dunn_index: {dunn_index_value}")

    inertia = kmeans_clustering.inertia_
    mlflow.log_metric("inertia", inertia)
    logger.info(f"inertia: {inertia}")

    # Print score report to a text file
    model_score = {
        "silhouette": silhouette_score_value,
        "dunn_index": dunn_index_value,
        "inertia": inertia,
    }

    logger.info("Writing to score.txt")
    with open((Path(score_report) / "score.json"), "w") as json_file:
        json.dump(model_score, json_file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("score")
    parser.add_argument("--model", type=str, help="Path to model")
    parser.add_argument("--score_report", type=str, help="Path to score report")
    parser.add_argument("--prep_data", type=str, help="Path to the prepared data")
    parser.add_argument(
        "--raw_data",
        type=str,
        default="../data/raw_data",
        help="Path to raw data",
    )

    args = parser.parse_args()

    main(
        raw_data=args.raw_data,
        prep_data=args.prep_data,
        model=args.model,
        score_report=args.score_report,
    )
