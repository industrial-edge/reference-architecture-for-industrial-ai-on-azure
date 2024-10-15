import argparse
import joblib
import pandas
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

    test_dir = Path("./test")
    test_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "payload_file exists, dir, file: %s %s %s \n%s",
        payload_file.exists(),
        payload_file.is_dir(),
        payload_file.is_file(),
        payload_file,
    )

    input_list = joblib.load(payload_file)

    with LocalPipelineRunner(package_path, test_dir) as runner:
        outputs = runner.run_pipeline(input_list)

    if len(outputs) > 0:
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

    main(args.payload_data, args.package_path, args.validation_results)
