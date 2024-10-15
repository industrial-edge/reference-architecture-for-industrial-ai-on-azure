import argparse
import pickle
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from common.src.base_logger import get_logger
from sklearn.cluster import KMeans

logger = get_logger(__name__)


def main(training_data: str, model_output: str):

    lines = [
        f"Training data path: {training_data}",
        f"Model output path: {model_output}",
    ]

    for line in lines:
        logger.info(line)

    train_data = pd.read_csv((Path(training_data) / "transformed_data.csv"))

    train_model(train_data, model_output)


def train_model(train_data: np.array, model_output: str) -> None:
    """
    Train a KMeans model and store the resulting model and metadata.
    Initiates an mlflow tracking run, which logs information about the training
    process.

    Arguments:
    train_data: np.array
        A numpy array containing the training data for the KMeans model.
    model_output: str
        The path to the directory where the model will be stored.

    Returns:
    None
        This function does not return a value. The resulting model is
        written to Azure Blob Storage.
    """

    mlflow.autolog()

    model = KMeans(n_clusters=3, random_state=0)

    model.fit(train_data)

    pickle.dump(model, open((Path(model_output) / "model.sav"), "wb"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("train")
    parser.add_argument("--training_data", type=str, help="Path to training data")
    parser.add_argument("--model_output", type=str, help="Path of output model")

    args = parser.parse_args()

    training_data = args.training_data
    model_output = args.model_output

    main(training_data, model_output)
