# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import json
import logging
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.metrics import silhouette_score
from state_identifier.src.score.scoring_utils import dunn_index

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main(validation_results, prep_data_path, metrics_results):
    """Compute clustering metrics for packaged model:
    - reads prediction labels, inertia from validation_results
    - loads prep_data
    - computes the following metrics: silhouette, dunn_index
    - metrics are written to an output file
    """
    metrics_results = Path(metrics_results)
    validation_file = Path(validation_results)
    validation_file = (
        validation_file / "validation_file"
        if validation_file.is_dir()
        else validation_file
    )

    logger.info(
        "validation_file exists, dir, file: %s %s %s \n%s",
        validation_file.exists(),
        validation_file.is_dir(),
        validation_file.is_file(),
        validation_file,
    )

    validation_df = pd.read_csv(validation_file)
    validation_labels = np.array(validation_df["prediction"])

    prep_data_df = pd.read_csv((Path(prep_data_path) / "transformed_data.csv"))
    prep_data = prep_data_df.values

    inertia = validation_df["model_inertia"].iloc[0]
    logger.info(f"inertia: {inertia}")

    silhouette_score_value = silhouette_score(prep_data, validation_labels)
    logger.info(f"silhouette: {silhouette_score_value}")

    dunn_index_value = dunn_index(prep_data, validation_labels)
    logger.info(f"dunn_index: {dunn_index_value}")

    metrics_dict = {
        "silhouette": silhouette_score_value,
        "dunn_index": dunn_index_value,
        "inertia": inertia,
    }

    logger.info("Writing to metrics_results")
    with open(metrics_results, "w") as file:
        json.dump(metrics_dict, file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--validation_results",
        type=str,
        help="Validation results file",
    )
    parser.add_argument(
        "--prep_data",
        type=str,
        help="Path to prep data",
    )
    parser.add_argument(
        "--metrics_results",
        type=str,
        help="Metrics results file",
    )

    args = parser.parse_args()

    main(args.validation_results, args.prep_data, args.metrics_results)
