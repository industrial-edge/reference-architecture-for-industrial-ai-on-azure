import argparse
from pathlib import Path
import os
import tensorflow as tf
import numpy as np
from PIL import Image
from typing import List

from common.src.base_logger import get_logger

logger = get_logger(__name__)
logger.info("tensorflow: {}".format(tf.__version__))


def main(raw_data: str, training_data: str, test_data: str):

    lines = [
        f"Raw data path: {raw_data}",
        f"Training output path: {training_data}",
        f"Test output path: {test_data}",
    ]

    for line in lines:
        logger.info(line)

    data_prep(raw_data, training_data, test_data)


def data_prep(
    raw_data,
    training_data,
    test_data,
    image_width=224,
    image_height=224,
    scale=255,
) -> None:
    """
    Prepare the data for model ingestion by extracting the training and test sets.

    This function carries out the following steps:
    1. Saves the training and test sets in separate folders in Azure Blob Storage.

    Arguments:
    raw_data: str
        File path to the raw data
    training_data: str
        File path to where the training data is written
    test_data: str
        File path to where the test data is written
    IMAGE_WIDTH: int
        Image width
    IMAGE_HEIGHT: int
        Image height
    SCALE: int
        Image scale

    Returns:
    None
        The function does not return any value.
        The results are saved in the 'prep_data' directory in Azure Blob Storage.
        Two separate folders are created for each extracted data set.
    """

    image_size = (image_width, image_height)
    image_dir = Path(raw_data)

    class_labels = []
    for path in image_dir.iterdir():
        if path.is_dir():
            class_labels.append(path.name)

    image_generator = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1 / scale, validation_split=0.2
    )

    training_set = image_generator.flow_from_directory(
        image_dir, target_size=image_size, subset="training"
    )
    test_set = image_generator.flow_from_directory(
        image_dir, target_size=image_size, subset="validation"
    )

    save_to_dir(training_set, training_data, class_labels)
    save_to_dir(test_set, test_data, class_labels)

    logger.info("Finish")


def save_to_dir(
    dataset: tf.keras.preprocessing.image.DirectoryIterator,
    save_dir: str,
    class_labels: List[str],
):
    batches = len(dataset)
    batch_count = 0
    for batch, classes in dataset:
        batch_count += 1
        for i in range(len(batch)):
            class_name = class_labels[np.array(classes[i]).argmax()]
            subdir = os.path.join(save_dir, class_name)
            os.makedirs(subdir, exist_ok=True)

            image = np.array(batch[i] * 255, dtype="uint8")
            pil_image = Image.fromarray(image, mode="RGB")
            image_path = os.path.join(subdir, f"image_{batch_count}_{i}.jpg")
            pil_image.save(image_path, format="JPEG")
        if batch_count == batches:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw_data",
        type=str,
        default="../data/raw_data",
        help="Path to raw data",
    )
    parser.add_argument(
        "--training_data",
        type=str,
        default="../data/training_data",
        help="Path to training data",
    )
    parser.add_argument(
        "--test_data", type=str, default="../data/test_data", help="Path to test data"
    )

    args = parser.parse_args()
    raw_data = args.raw_data
    training_data = args.training_data
    test_data = args.test_data

    main(raw_data, training_data, test_data)
