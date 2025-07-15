import argparse
import json
from pathlib import Path
from typing import Tuple

import mlflow
from azureml.core import Run

import tensorflow as tf

from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(
    training_data: str,
    model_output: str,
    model_metadata: str,
    image_width: int,
    image_height: int,
    dim: int,
):
    run = Run.get_context()
    mlflow.set_tracking_uri(run.experiment.workspace.get_mlflow_tracking_uri())
    mlflow.autolog()

    lines = [
        f"Training data path: {training_data}",
        f"Model output path: {model_output}",
        f"Model metadata path: {model_metadata}",
    ]

    for line in lines:
        logger.info(line)

    with mlflow.start_run():

        image_size = (image_width, image_height)

        image_generator = tf.keras.preprocessing.image.ImageDataGenerator()
        logger.info(f"image_generator: {image_generator}")

        training_set = image_generator.flow_from_directory(
            training_data, target_size=image_size
        )

        logger.info(f"training_set: {training_set}")

        train_model(training_set, model_metadata, model_output, image_size, dim)

        logger.info("Saving model_metadata...")
        run_id = run.info.run_id
        model_uri = f"runs:/{run_id}/model"
        model_data = {"run_id": run_id, "run_uri": model_uri}

        logger.info("model_metadata:\n%s", json.dumps(model_data, indent=4))

        with open(model_metadata, "w") as json_file:
            json.dump(model_data, json_file, indent=4)


def train_model(
    training_set: tf.data.Dataset,
    model_metadata: str,
    model_output: str,
    image_size: Tuple[int, int],
    dim: int,
) -> None:
    """
    Trains a MobileNet network and stores the corresponding model and metadata.
    Initiates an mlflow tracking run, which logs information about the training
    process.

    Arguments:
    train_data: np.array
        A numpy array containing the training data for the KMeans model.

    Returns:
    None
        This function does not return a value. The resulting model and metadata are
        written to Azure Blob Storage.
    """

    logger.info("Started training")
    logger.info(f"model_metadata: {model_metadata}")

    feature_extractor = tf.keras.applications.MobileNet(
        weights="imagenet", include_top=False, input_shape=(image_size + (dim,))
    )
    feature_extractor.trainable = False
    logger.info(f"Type of feature extractor: {type(feature_extractor)}")

    logger.info(f"training_set: {training_set}")
    _, label_batch = next(iter(training_set))

    output = feature_extractor.output
    feature_extractor_output = tf.keras.layers.GlobalAveragePooling2D()(output)

    classifier = tf.keras.layers.Dense(label_batch.shape[1], activation="softmax")(
        feature_extractor_output
    )

    model = tf.keras.Model(inputs=feature_extractor.input, outputs=classifier)
    model.build((None,) + image_size + (3,))

    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
        metrics=["acc"],
    )

    model.fit(
        training_set,
        epochs=4,
        steps_per_epoch=training_set.num_batches,
        callbacks=[],
    )

    logger.info("Saving model")
    temp_model_path = Path(model_output) / "classification_mobilnet.h5"
    logger.info("temp_model_path: %s", temp_model_path)

    model.save(temp_model_path)

    logger.info("Finished training")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("train")
    parser.add_argument("--training_data", type=str, help="Path to training data")
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
    parser.add_argument(
        "--dim", type=int, default=3, help="Channels used for the image"
    )
    parser.add_argument("--model_output", type=str, help="Path of output model")
    parser.add_argument("--model_metadata", type=str, help="Path of model metadata")

    args = parser.parse_args()

    main(
        args.training_data,
        args.model_output,
        args.model_metadata,
        args.image_width,
        args.image_height,
        args.dim,
    )
