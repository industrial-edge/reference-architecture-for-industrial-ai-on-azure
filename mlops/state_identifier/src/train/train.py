import argparse
from pathlib import Path
import pandas
import numpy as np
import joblib
import json
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
import seaborn as sns
from matplotlib import pyplot
from state_identifier.src.si.preprocessing import (
    positive_sum_of_changes,
    negative_sum_of_changes,
    SumColumnsTransformer,
)
from state_identifier.src.si.pipeline import (
    WindowTransformer,
    FeatureTransformer,
    FillMissingValues,
    back_propagate_labels,
)
import tsfresh.feature_extraction.feature_calculators as fc
import mlflow
from azureml.core import Run

from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(raw_data: str, training_data: str, model_output: str, model_metadata: str):

    run = Run.get_context()
    mlflow.set_tracking_uri(run.experiment.workspace.get_mlflow_tracking_uri())
    mlflow.autolog()

    with mlflow.start_run():

        run_id = run.info.run_id
        logger.info(f"run_id: {run_id}")
        model_uri = f"runs:/{run_id}/model"
        model_data = {"run_id": run_id, "run_uri": model_uri}

        lines = [
            f"Training data path: {raw_data}",
            f"Training data path: {training_data}",
            f"Model output path: {model_output}",
            f"model_metadata: {model_metadata}",
        ]

        for line in lines:
            logger.info(line)

        train_model(raw_data, training_data, model_output, model_metadata)

        logger.info("Saving model_metadata...")
        logger.info("model_metadata:\n%s", json.dumps(model_data, indent=4))

        with open(Path(model_metadata), "w") as json_file:
            json.dump(model_data, json_file, indent=4)


def train_model(
    raw_data: str,
    training_data: np.array,
    model_output: str,
    model_metadata: str,
) -> None:

    logger.info("Starting training")

    logger.info(f"raw_data: {raw_data}")
    logger.info(f"training_data: {training_data}")
    logger.info(f"model_output: {model_output}")
    logger.info(f"model_metadata: {model_metadata}")

    df = pandas.read_parquet(raw_data)

    input_columns = ["ph1", "ph2", "ph3"]

    logger.info("creating ph_sum column")
    df["ph_sum"] = SumColumnsTransformer().transform(df[input_columns].values).flatten()

    logger.info("creating weighted_feature_list column")
    weighted_feature_list = [
        (2, [fc.maximum, fc.minimum, fc.mean]),
        (1, [fc.variance, fc.standard_deviation]),
        (1, [fc.sum_values]),
        (1, [fc.absolute_sum_of_changes]),
        (1, [positive_sum_of_changes, negative_sum_of_changes]),
        (
            1,
            [
                fc.count_above_mean,
                fc.longest_strike_above_mean,
                fc.longest_strike_below_mean,
            ],
        ),
    ]

    logger.info("creating pipeline")
    pipe = Pipeline(
        [
            (
                "preprocessing",
                Pipeline(
                    [
                        ("fillmissing", FillMissingValues("ffill")),
                        (
                            "summarization",
                            SumColumnsTransformer(),
                        ),  # summarizes the variables into one variable
                        (
                            "windowing",
                            WindowTransformer(window_size=300, window_step=300),
                        ),
                        (
                            "featurization",
                            FeatureTransformer(function_list=weighted_feature_list),
                        ),
                        ("scaling", MinMaxScaler(feature_range=(0, 1))),
                    ]
                ),
            ),
            ("clustering", KMeans(n_clusters=3, random_state=0)),
        ]
    )

    x = df[input_columns].values  # transforming training data
    logger.info(f"x shape: {x.shape}")

    logger.info("Fitting pipeline")
    pipe.fit(x)

    logger.info("predicting pipeline")
    x_classes = pipe.predict(x)

    logger.info("df")
    df = back_propagate_labels(df, pipe["preprocessing"], x_classes)

    colormap = {
        -1: "white",
        0: "red",
        1: "green",
        2: "blue",
        3: "orange",
        4: "purple",
        5: "yellow",
    }
    _, ax = pyplot.subplots(figsize=(24, 12))
    sns.scatterplot(
        x=df.index, y="ph_sum", data=df, hue="class", palette=colormap, ax=ax
    )

    logger.info("Saving model")
    models_folder = Path(model_output) / "models"
    models_folder.mkdir(parents=True, exist_ok=True)

    model_output = Path(models_folder) / "clustering-model.joblib"
    with open(model_output, "wb"):
        joblib.dump(pipe, model_output, compress=9)

    logger.info("Finished training")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("train")
    parser.add_argument("--training_data", type=str, help="Path to training data")
    parser.add_argument(
        "--raw_data",
        type=str,
        default="../data/raw_data",
        help="Path to raw data",
    )
    parser.add_argument("--model_output", type=str, help="Path of output model")
    parser.add_argument("--model_metadata", type=str, help="Path of model metadata")

    args = parser.parse_args()

    training_data = args.training_data
    raw_data = args.raw_data
    model_output = args.model_output
    model_metadata = args.model_metadata

    main(raw_data, training_data, model_output, model_metadata)
