import argparse
import shutil
import zipfile

from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(
    raw_data: str,
    prep_data: str,
    # preparation_pipeline_path: str
) -> None:
    lines = [
        f"Raw data path: {raw_data}",
        f"Data output path: {prep_data}",
    ]

    for line in lines:
        logger.info(line)

    logger.info("skipping...")


def data_prep(
    raw_data: str,
    prep_data: str,
) -> None:

    shutil.rmtree(prep_data, ignore_errors=True)
    with zipfile.ZipFile(raw_data, "r") as zip_file:
        zip_file.extractall(prep_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw_data",
        type=str,
        default="../data/raw_data",
        help="Path to raw data",
    )
    parser.add_argument(
        "--prep_data", type=str, default="../data/prep_data", help="Path to prep data"
    )
    args = parser.parse_args()

    main(
        raw_data=args.raw_data,
        prep_data=args.prep_data,
    )
