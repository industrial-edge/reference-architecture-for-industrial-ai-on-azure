import argparse
import json
from pathlib import Path
import pandas
import numpy as np
import joblib
from sklearn.metrics import silhouette_score
from state_identifier.src.score.scoring_utils import dunn_index
from state_identifier.src.si.preprocessing import (
    SumColumnsTransformer,
)

from common.src.base_logger import get_logger

logger = get_logger(__name__)


def main(
    subscription_id: str,
    workspace_name: str,
    resource_group_name: str,
    asset_name: str,
    asset_version: str,
    validation_results: str,
    raw_data: str,
    model: str,
    metrics_results: str,
):

    logger.info(f"subscription_id: {subscription_id}")
    logger.info(f"workspace_name: {workspace_name}")
    logger.info(f"resource_group_name: {resource_group_name}")
    logger.info(f"asset_name: {asset_name}")
    logger.info(f"asset_version: {asset_version}")

    """Compute clustering metrics for packaged model:
    - reads prediction labels, inertia from validation_results
    - loads prep_data
    - computes the following metrics: silhouette, dunn_index
    - metrics are written to an output file
    """
    metrics_results = Path(metrics_results)
    logger.info(f"metrics_results: {metrics_results}")

    validation_file = Path(validation_results)
    validation_file = (
        validation_file / "validation_file"
        if validation_file.is_dir()
        else validation_file
    )
    logger.info(f"validation_file: {validation_file}")

    logger.info(
        "validation_file exists, dir, file: %s %s %s \n%s",
        validation_file.exists(),
        validation_file.is_dir(),
        validation_file.is_file(),
        validation_file,
    )

    df = pandas.read_csv(validation_file, quotechar="'")
    logger.info(f"DataFrame columns: {df.columns}")  # Log the columns of the DataFrame

    results = df.to_dict(orient="records")
    predictions = [int(item["prediction"]) for item in results]

    # Convert predictions to a NumPy array
    validation_labels = np.array(predictions)

    # Load the model
    models_file_path = Path(model) / "clustering-model.joblib"
    model_instance = joblib.load(models_file_path)
    logger.info(f"Pipeline steps: {model_instance.named_steps.keys()}")

    # prepare data
    raw_data_frame = pandas.read_parquet(raw_data)

    input_columns = ["ph1", "ph2", "ph3"]
    raw_data_frame["ph_sum"] = (
        SumColumnsTransformer()
        .transform(raw_data_frame[input_columns].values)
        .flatten()
    )

    data_preparation_pipeline = model_instance.named_steps["preprocessing"]

    raw_data_numpy_filtered = raw_data_frame[input_columns].values
    data_preparation_pipeline.fit(raw_data_numpy_filtered)

    transformed_data = data_preparation_pipeline.transform(raw_data_numpy_filtered)
    prep_data = pandas.DataFrame(transformed_data)

    if len(validation_labels) != len(prep_data):
        logger.error(
            f"Inconsistent number of samples: prep_data has {len(prep_data)}, "
            f"but validation_labels has {len(validation_labels)}."
        )
        raise ValueError(
            "Inconsistent number of samples between prep_data and validation_labels."
        )

    silhouette_score_value = silhouette_score(prep_data, validation_labels)
    logger.info(f"silhouette: {silhouette_score_value}")

    dunn_index_value = dunn_index(prep_data, validation_labels)
    logger.info(f"dunn_index: {dunn_index_value}")

    metrics_dict = {
        "silhouette": silhouette_score_value,
        "dunn_index": dunn_index_value,
    }

    logger.info("Writing to metrics_results")
    with open(metrics_results, "w") as file:
        json.dump(metrics_dict, file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("score")

    parser.add_argument("--subscription_id", type=str, help="Azure subscription ID")
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine Learning workspace name"
    )
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure resource group name"
    )
    parser.add_argument("--asset_name", type=str, help="Model Name")
    parser.add_argument("--asset_version", type=str, help="Model Version")
    parser.add_argument(
        "--validation_results", type=str, help="Path to validation results"
    )
    parser.add_argument("--raw_data", type=str, help="Path to raw data")
    parser.add_argument("--prep_data", type=str, help="Path to prep data")
    parser.add_argument("--model", type=str, help="Path to model")
    parser.add_argument("--metrics_results", type=str, help="Path to output file")

    args = parser.parse_args()

    main(
        subscription_id=args.subscription_id,
        workspace_name=args.workspace_name,
        resource_group_name=args.resource_group_name,
        asset_name=args.asset_name,
        asset_version=args.asset_version,
        validation_results=args.validation_results,
        raw_data=args.raw_data,
        model=args.model,
        metrics_results=args.metrics_results,
    )
