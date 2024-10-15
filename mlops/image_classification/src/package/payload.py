# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

"""
Create Vision Connector MQTT payload from image file

"""

import base64
import datetime
import io
import json
import logging
from itertools import chain
from pathlib import Path
from urllib.request import urlopen

from PIL import Image

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
counter = 0
width = 0
height = 0


def create_mqtt_payload(filepath):

    with open(filepath, "rb") as image_file:
        content = image_file.read()
    image = base64.b64encode(content).decode("ascii")

    extension = Path(filepath).suffix
    extension_lower = extension.lower()
    if extension_lower == ".png":
        image_prefix = "data:image/png;base64,"
    elif extension_lower in [".jpg", ".jpeg"]:
        image_prefix = "data:image/jpeg;base64,"
    else:
        assert False, f"Unsupported image file suffix {extension}"

    timestamp = datetime.datetime.now().isoformat()
    sensor_id = "a204dba4-274e-43ce-9a71-55de9e715e72"
    status = {"genicam_signal": {"code": 3}}

    vision_connector_data = json.dumps(
        {
            "timestamp": timestamp,
            "sensor_id": sensor_id,
            "image": image_prefix + image,
            "status": status,
        }
    )

    return vision_connector_data


def get_image_from_vision_mqtt_payload(vision_payload):
    """
    Takes a Vision Connector JSON payload, decodes the image and returns it as
    PIL image object resized to the input shape of the network.
    Returns None if decoding fails.
    """

    try:
        image_string = vision_payload["image"]
        with urlopen(image_string) as response:
            assert response.headers["Content-type"] in ["image/png", "image/jpeg"]
            logger.debug("Verified image type is PNG or JPEG")
            image_bytes = response.read()
            pil_image = Image.open(io.BytesIO(image_bytes)).resize(IMAGE_SIZE)
            logger.debug(f"Image info: {pil_image}")
        return pil_image
    except Exception as e:
        logger.debug(f"Error decoding image from vision payload: {e}")
        return None


def create_zmq_dict(file_path: Path):
    """
    Provides Vision Connector binary payload in a dictionary with key "image"
    that is specified as single input of inference node.
    """

    image = Image.open(file_path)
    image = image.convert(mode="RGB", colors=256)

    payload = {
        "image": {
            "resolutionWidth": image.width,
            "resolutionHeight": image.height,
            "mimeType": "image/raw",
            "dataType": "uint8",
            "channelsPerPixel": 3,
            "image": _swap_bytes(image.tobytes()),
        }
    }
    return payload


def create_image_output(image: Image):
    output_image = {
        "metadata": json.dumps(
            {"resolutionWidth": image.width, "resolutionHeight": image.height}
        ),
        "bytes": image.tobytes(),
    }
    return output_image


def get_image_from_vision_zmq_dict(image_data: dict):
    """
    Takes a Vision Connector binary payload in a dictionary,
    decodes the image and returns it as PIL image object resized
    to the input shape of the network.
    Returns None if decoding fails.
    """

    global counter
    counter = (counter + 1) % 10

    if image_data["dataType"] != "uint8" or image_data["channelsPerPixel"] != 3:
        logger.error(
            "The image must be sent with data type uint8 and 3 channels per pixel."
        )
        return None

    try:
        width = image_data["resolutionWidth"]
        height = image_data["resolutionHeight"]

        # The image is received with 'BGR' byte order
        pil_image = Image.frombytes(
            "RGB", (width, height), image_data["image"], "raw", "BGR"
        ).resize(IMAGE_SIZE)
        logger.debug(f"Image info: {pil_image}")

        return pil_image
    except Exception as e:
        logger.error(f"Error decoding image from vision payload: {e}")
        return None


def _swap_bytes(image_bytes):

    number_of_pixels = int(len(image_bytes) / 3)
    list_of_bytes = [
        [image_bytes[3 * i + 2], image_bytes[3 * i + 1], image_bytes[3 * i]]
        for i in range(number_of_pixels)
    ]
    image_bytes = bytes(chain.from_iterable(list_of_bytes))

    return image_bytes
