import argparse
import os
from pathlib import Path

import joblib
import pandas as pd
import tsfresh.feature_extraction.feature_calculators as fc

from state_identifier.src.prep.preprocessing_utils import (
    FeatureTransformer,
    FillMissingValues,
    SumColumnsTransformer,
    WindowTransformer,
    negative_sum_of_changes,
    positive_sum_of_changes,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(raw_data: str, prep_data: str, preparation_pipeline_path: str) -> None:

    lines = [
        f"Raw data path: {raw_data}",
        f"Data output path: {prep_data}",
    ]

    raw_data_frame = pd.read_parquet(raw_data)

    for line in lines:
        logger.info(line)

    data_prep(raw_data_frame, prep_data, preparation_pipeline_path)


def data_prep(
    raw_data_frame: pd.DataFrame,
    prep_data: str,
    preparation_pipeline_path: str,
    window_size: int = 300,
    window_step: int = 300,
) -> None:
    """
    Prepare the data for model ingestion by applying several transformations.

    This function carries out the following steps:
    1. Computes the sum of specified columns and adds it as a new column to the dataframe.
    2. Applies a series of transformations to the data, including filling missing values,
       summarizing columns, windowing, feature extraction, and scaling.
    3. Saves the transformed data as a CSV file in Azure Blob Storage.

    Arguments:
    raw_data_frame: pandas DataFrame
        DataFrame containing the raw data
    prep_data: str
        File path to where the transofrmed data is written
    preparation_pipeline_path: str
        File path to where the data preparation pipeline is written
    window_size: int
        Size of the window used for windowing the data
    window_step: int
        Step size of the window used for windowing the data

    Returns:
    None
        The function does not return any value. The result is saved as a CSV file named
        "transformed_data.csv" in the 'prep_data' directory in Azure Blob Storage.
    """

    # Define the columns that will be used by the model.
    input_columns = ["ph1", "ph2", "ph3"]

    # Compute the sum of the pH's as they are strongly correlated
    raw_data_frame["ph_sum"] = (
        SumColumnsTransformer()
        .transform(raw_data_frame[input_columns].values)
        .flatten()
    )

    # The features specified here will be extracted window by window.
    # You can differentiate between the importance of various features by specifying different weights as integers.  # noqa: E501
    # Features specified with a weight greater than 1 will be fed to the subsequent parts of the ML pipeline  # noqa: E501
    # with the corresponding multiplicity.
    weighted_feature_list = [
        (2, [fc.maximum, fc.minimum, fc.mean]),
        (1, [fc.variance, fc.standard_deviation]),
        (1, [fc.sum_values]),
        (1, [fc.absolute_sum_of_changes]),
        (1, [positive_sum_of_changes, negative_sum_of_changes]),
        (
            1,
            [
                fc.count_above_mean,
                fc.longest_strike_above_mean,
                fc.longest_strike_below_mean,
            ],
        ),
    ]

    raw_data_numpy_filtered = raw_data_frame[input_columns].values

    data_preparation_pipeline = Pipeline(
        [
            ("fillmissing", FillMissingValues("ffill")),
            ("summarization", SumColumnsTransformer()),
            (
                "windowing",
                WindowTransformer(window_size=window_size, window_step=window_step),
            ),
            ("featurization", FeatureTransformer(function_list=weighted_feature_list)),
            ("scaling", MinMaxScaler(feature_range=(0, 1))),
        ]
    )

    data_preparation_pipeline.fit(raw_data_numpy_filtered)

    transformed_data = data_preparation_pipeline.transform(raw_data_numpy_filtered)

    transformed_data_frame = pd.DataFrame(transformed_data)

    # output_transformed_data
    transformed_data_frame.to_csv(
        os.path.join(prep_data, "transformed_data.csv"), index=False
    )

    # #save pipeline to joblib
    model_path = Path(preparation_pipeline_path) / "preparation_pipeline.joblib"

    joblib.dump(data_preparation_pipeline, model_path, compress=9)

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
        "--prep_data", type=str, default="../data/prep_data", help="Path to prep data"
    )

    parser.add_argument(
        "--preparation_pipeline_path",
        type=str,
        default="../data/prep_pipeline",
        help="Path to preparation pipeline file",
    )

    args = parser.parse_args()
    raw_data = args.raw_data
    prep_data = args.prep_data
    preparation_pipeline_path = args.preparation_pipeline_path

    main(raw_data, prep_data, preparation_pipeline_path)
