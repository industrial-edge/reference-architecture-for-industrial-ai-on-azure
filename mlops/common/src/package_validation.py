import argparse
import joblib
import pandas
import tempfile
import shutil
from pathlib import Path

from common.src.base_logger import get_logger
from simaticai.testing.pipeline_runner import LocalPipelineRunner

logger = get_logger(__name__)


def main(payload_data, package_path, validation_results):
    """Validates the created package through the next steps:
     - extracts the given package
     - creates a virtual python environment
     - installs the packages defined in the requirements.txt files for components
     - reads the given example payloads
     - executes the defined pipeline against the given example payloads
    If successful, the package can be registered
    """

    validation_results = Path(validation_results)
    package_path = Path(package_path)
    package_path = (
        package_path / "package_path" if package_path.is_dir() else package_path
    )
    payload_file = Path(payload_data)
    payload_file = (
        payload_file / "payload_file" if payload_file.is_dir() else payload_file
    )

    test_dir = Path(tempfile.gettempdir()) / "test"
    test_dir.mkdir(parents=True, exist_ok=True)

    temp_package_dir = Path(tempfile.gettempdir()) / "package"
    temp_package_dir.mkdir(parents=True, exist_ok=True)

    if package_path.is_dir():
        shutil.copytree(package_path, temp_package_dir, dirs_exist_ok=True)
    else:
        shutil.copy2(package_path, temp_package_dir / package_path.name)

    package_zip_file = temp_package_dir / package_path.name

    logger.info(
        "payload_file exists, dir, file: %s %s %s \n%s",
        payload_file.exists(),
        payload_file.is_dir(),
        payload_file.is_file(),
        payload_file,
    )

    input_list = joblib.load(payload_file)
    logger.info(f"input_list len: {len(input_list)}")
    logger.debug(f"input_list[0]: {input_list[0]}")

    outputs = []
    with LocalPipelineRunner(package_zip_file, test_dir) as runner:
        for input_data in input_list:
            out1 = runner.run_pipeline(input_data)
            logger.info(f"out1: {out1}")

            if isinstance(out1, list):
                logger.info("out1 is a list")
                for row in out1:
                    outputs.append(row)
            else:
                logger.info("out1 is not a list")
                outputs.append(out1)

    logger.info(f"outputs len: {len(outputs)}")
    logger.debug(f"outputs: {outputs}")

    df_outputs = pandas.DataFrame(outputs)
    df_outputs.to_csv(validation_results, quotechar="'", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--payload_data",
        type=str,
        default="../data/payload_data",
        help="Path to created payload data file in joblib",
    )
    parser.add_argument(
        "--package_path",
        type=str,
        help="Path to saved package",
    )
    parser.add_argument(
        "--validation_results",
        type=str,
        help="Validation result file for outputs",
    )

    args = parser.parse_args()

    main(
        payload_data=args.payload_data,
        package_path=args.package_path,
        validation_results=args.validation_results,
    )
