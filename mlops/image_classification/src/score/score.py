import argparse
import json
import os
from pathlib import Path
from typing import List, Optional, Tuple
import mlflow
import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix

from azureml.core import Run

from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(test_data, model, score_report, image_width, image_height):

    run = Run.get_context()
    mlflow.set_tracking_uri(run.experiment.workspace.get_mlflow_tracking_uri())
    mlflow.autolog()

    with mlflow.start_run():

        lines = [
            f"Model path: {model}",
            f"Test data path: {test_data}",
            f"Scoring output path: {score_report}",
        ]

        for line in lines:
            logger.info(line)

        image_size = (image_width, image_height)

        class_labels = [
            path.name for path in Path(test_data).iterdir() if path.is_dir()
        ]
        class_labels.sort()

        image_generator = tf.keras.preprocessing.image.ImageDataGenerator()
        test_data_tf = image_generator.flow_from_directory(
            test_data, target_size=image_size
        )
        # Load the model from input port
        model = tf.keras.models.load_model((Path(model) / "classification_mobilnet.h5"))
        encoded_preds, encoded_labels = encoded_predictions_for_entire_dataset(
            model, test_data_tf
        )

        metrics, confusion_m_df, clf_report = evaluate(
            encoded_preds, encoded_labels, class_labels
        )

        write_results(metrics, confusion_m_df, clf_report, score_report)


def encoded_predictions_for_entire_dataset(
    model: tf.keras.Model, data: tf.data.Dataset
) -> Tuple[np.array, np.array]:
    """
    Predict the labels for all the batches and replace the outputs
    of the softmax layer with the class that has the maximum probability.
    Same change for the one-hot encoded labels.
    The change in the input shape is as follows:
    (N, c) -> (N,1)
    with N being the number of samples and c the number of classes

    Arguments:
    model: tf.keras.Model
        The loaded model which will makes the predictions
    data: tf.data.Dataset
        Dataset containing test data

    Returns:
    encoded_predictions, encoded_labels: Tuple(np.array, np.array)
        The encoded predictions and labels
    """
    predictions = None
    labels = None
    batches = len(data)

    for batch_counter, (batch, labels_batch) in enumerate(data):
        predictions_batch = model.predict(batch)

        if predictions is None:
            predictions = predictions_batch
            labels = labels_batch
        else:
            predictions = np.concatenate((predictions, predictions_batch), axis=0)
            labels = np.concatenate((labels, labels_batch), axis=0)

        # Needed to avoid an infinite loop
        if batch_counter == batches - 1:
            break

    encoded_predictions = np.argmax(np.array(predictions), axis=1)
    encoded_labels = np.argmax(np.array(labels), axis=1)

    return encoded_predictions, encoded_labels


def evaluate(
    targets_data: List[float],
    targets_predicted: List[float],
    classes: Optional[List[str]] = None,
) -> Tuple[dict, pd.DataFrame, dict]:
    """
    Evaluates model and returns a dictionary with the following reports:
    * Classification report (sklearn classification report)
    * Confusion Matrix

    Arguments:
    targets_data : List[float]
        Actual values vector
    targets_predicted : List[float]
        Predicted values vector
    classes : List[str], optional
        Classes, by default None

    Returns:
    metrics : dict
        A dictionary, containing reports
    confusion_m_df : pd.DataFrame
        A dataframe containing the confusion matrix
    classification_report : dict
        A dictionary containing the classification report

    """
    metrics = {}

    # Create classification report
    clf_report = classification_report(
        targets_data, targets_predicted, output_dict=True, target_names=classes
    )
    metrics["clf_report"] = clf_report
    step = 0

    for name_of_metric in clf_report.keys():
        if name_of_metric == "accuracy":
            mlflow.log_metric("accuracy", clf_report[name_of_metric])
        elif name_of_metric != "confusion_m":
            mlflow.log_metric(name_of_metric, step)
            mlflow.log_metrics(clf_report[name_of_metric])
            step += 1

    # Calculate confusion matrix
    confusion_m = confusion_matrix(targets_data, targets_predicted)
    confusion_m_df = pd.DataFrame(confusion_m, index=classes, columns=classes)

    metrics["confusion_m"] = confusion_m_df.to_dict()

    return metrics, confusion_m_df, clf_report


def write_results(
    metrics: dict,
    confusion_m_df: pd.DataFrame,
    classification_report: dict,
    output_folder: str,
) -> None:
    """
    Write the results of the evaluation to a folder.

    Parameters
    ----------
    metrics : dict
        A dictionary, containing reports
    confusion_m_df : pd.DataFrame
        A dataframe containing the confusion matrix
    classification_report : dict
        A dictionary containing the classification report
    output_folder : str
        Folder where all the results will be written


    Returns
    -------
    None

    """

    cfm_png = "cfm.png"

    confusion_m_plot = sns.heatmap(confusion_m_df, annot=True, fmt="g")
    confusion_m_plot.figure.savefig(os.path.join(output_folder, cfm_png))

    mlflow.log_image(
        Image.open(os.path.join(output_folder, cfm_png)), "confusion_matrix.png"
    )

    plt.clf()

    clf_plot = sns.heatmap(
        pd.DataFrame(classification_report).iloc[:-1, :].T, annot=True, fmt=".3f"
    )
    clf_report_png = "clf_report.png"

    clf_plot.figure.savefig(os.path.join(output_folder, clf_report_png))

    mlflow.log_image(
        Image.open(os.path.join(output_folder, clf_report_png)), clf_report_png
    )

    # Save evaluation results
    with open(os.path.join(output_folder, "score.json"), "w") as json_file:
        json.dump(metrics, json_file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("score")
    parser.add_argument("--test_data", type=str, help="Path to the test data")
    parser.add_argument("--model", type=str, help="Path to model")
    parser.add_argument("--score_report", type=str, help="Path to score report")
    parser.add_argument(
        "--image_width",
        type=int,
        default=224,
        help="Width of the images used for training",
    )
    parser.add_argument(
        "--image_height",
        type=int,
        default=224,
        help="Height of the images used for training",
    )

    args = parser.parse_args()

    main(
        args.test_data,
        args.model,
        args.score_report,
        args.image_width,
        args.image_height,
    )
