import argparse
import joblib
import logging
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main(raw_data: str, payload_data: str) -> None:

    lines = [
        f"Raw data path: {raw_data}",
        f"Data output path: {payload_data}",
    ]
    logger.info("\n".join(lines))

    raw_data_frame = pd.read_parquet(raw_data)

    # creating a list of dictionaries as the `process_input(..)` method receives them
    input_list = raw_data_frame[["ph1", "ph2", "ph3"]].to_dict(orient="records")

    array_of_input_lists = []
    array_of_input_lists.append(input_list)

    joblib.dump(array_of_input_lists, payload_data, compress=9)

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

    main(raw_data=raw_data, payload_data=payload_data)
