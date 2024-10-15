# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import json
import pickle
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from common.src.base_logger import get_logger
from sklearn.metrics import silhouette_score
from state_identifier.src.score.scoring_utils import dunn_index

logger = get_logger(__name__)


def main(prep_data: str, model: str, score_report: str):

    lines = [
        f"Prep data path: {prep_data}",
        f"Model path: {model}",
        f"Scoring output path: {score_report}",
    ]

    for line in lines:
        logger.info(line)

    # Load the test data with predicted values
    prep_data_dataframe = pd.read_csv((Path(prep_data) / "transformed_data.csv"))

    prep_data_numpy = prep_data_dataframe.values

    # Load the model from input port
    model = pickle.load(open((Path(model) / "model.sav"), "rb"))

    write_results(model, prep_data_numpy, score_report)


def write_results(model: KMeans, prep_data: np.array, score_report: str) -> None:
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

    labels = model.labels_

    silhouette_score_value = silhouette_score(prep_data, labels)

    mlflow.log_metric("silhouette", silhouette_score_value)
    logger.info(f"silhouette: {silhouette_score_value}")

    dunn_index_value = dunn_index(prep_data, labels)

    mlflow.log_metric("dunn_index", dunn_index_value)
    logger.info(f"dunn_index: {dunn_index_value}")

    inertia = model.inertia_

    mlflow.log_metric("inertia", inertia)
    logger.info(f"inertia: {inertia}")

    # Print score report to a text file
    model_score = {
        "silhouette": silhouette_score_value,
        "dunn_index": dunn_index_value,
        "inertia": inertia,
    }

    logger.info("Writing to score.txt")
    with open((Path(score_report) / "score.txt"), "w") as json_file:
        json.dump(model_score, json_file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("score")
    parser.add_argument("--prep_data", type=str, help="Path to the prepared data")
    parser.add_argument("--model", type=str, help="Path to model")
    parser.add_argument("--score_report", type=str, help="Path to score report")

    args = parser.parse_args()

    prep_data = args.prep_data
    model = args.model
    score_report = args.score_report

    main(prep_data, model, score_report)
