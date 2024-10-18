# Copyright (C) 2023 Siemens AG
# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.
#
# SPDX-License-Identifier: MIT

import json
import logging
import sys

from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sys.path.insert(0, str(Path(".").resolve()))
import vision_classifier as classifier
import payload


def process_input(data: dict):
    """
    Entry point function for AI Inference Server.
    First, this method creates PIL image object, resized to the input shape of the network.
    Then returns a prediction from the created pillow image.

    Args:
        data (dict): Dictionary that should contain a single key 'vision_payload' that holds the Vision Connector MQTT payload.  # noqa: E501
    Returns:
        dict: A dictionary with a single key 'prediction' that holds the index of the predicted class as an integer string.  # noqa: E501
    """
    vision_payload = json.loads(data["vision_payload"])
    pil_image = payload.get_image_from_vision_mqtt_payload(vision_payload)
    if pil_image is None:
        return None

    prediction, probability = classifier.predict_from_image(pil_image)
    logger.debug(f"Predicted class: {prediction} (probability: {probability})")

    return {
        "prediction": str(prediction),
        "ic_probability": metric_output(probability),
    }


def metric_output(v: int or float):
    return json.dumps({"value": v})
