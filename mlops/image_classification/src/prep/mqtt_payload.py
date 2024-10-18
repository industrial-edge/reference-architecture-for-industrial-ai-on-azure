# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import joblib
import pandas as pd
from pathlib import Path

from image_classification.src.package.payload import create_mqtt_payload
from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(raw_data: str, payload_data: str) -> None:
    raw_data = Path(raw_data)
    lines = [
        f"Raw data path: {raw_data}",
        f"Raw data path is directory: {raw_data.is_dir()}",
        f"Data output path: {payload_data}",
    ]

    image_list = raw_data.rglob("./*/*")
    df_images = pd.DataFrame([{"file": f, "class": f.parent.name} for f in image_list])

    input_list = []
    for _, row in df_images.iterrows():
        payload = create_mqtt_payload(row["file"])
        input_list.append({"vision_payload": payload})

    logger.info("\n".join(lines))
    logger.info("First sample records of payload:")
    for payload in input_list[:3]:
        logger.info(payload)

    joblib.dump(input_list, payload_data, compress=9)

    logger.info("Finish")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw_data",
        type=str,
        default="../data/raw_data",
        help="Path to raw data",
    )
    parser.add_argument(
        "--payload_data",
        type=str,
        help="Path to payload data to be created",
    )

    args = parser.parse_args()
    raw_data = args.raw_data
    payload_data = args.payload_data

    main(raw_data, payload_data)
