# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import argparse
import json
import os
from pathlib import Path

import pandas as pd
from azure.ai.ml import MLClient
from azure.identity import ManagedIdentityCredential
from common.src.base_logger import get_logger
from sklearn.metrics import classification_report

logger = get_logger(__name__)


def main(
    validation_results: str,
    raw_data: str,
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    asset_name: str,
    asset_version: str,
    metrics_results: str,
):

    client = MLClient(
        credential=ManagedIdentityCredential(
            client_id=os.getenv("DEFAULT_IDENTITY_CLIENT_ID")
        ),
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )

    raw_data_path = Path(raw_data).rglob("./*/*")
    raw_data_classes = [f.parent.name for f in raw_data_path]

    if len(raw_data_classes) == 0:
        raise ValueError("No classes found in raw data")

    data_asset = client.data.get(name=asset_name, version=asset_version)
    labels_dict = data_asset.tags

    raw_data_classes_int = [
        int(labels_dict[class_name]) for class_name in raw_data_classes
    ]

    validation_results = pd.read_csv(validation_results)
    validation_results_classes = validation_results["prediction"]
    validation_results_classes_int = [int(pred) for pred in validation_results_classes]

    clf_report = classification_report(
        y_true=raw_data_classes_int,
        y_pred=validation_results_classes_int,
        output_dict=True,
        target_names=labels_dict.keys(),
    )
    macro_avg = clf_report["macro avg"]

    metrics_to_tag = {
        "accuracy_validation": clf_report["accuracy"],
        "avg_precision_validation": macro_avg["precision"],
        "avg_recall_validation": macro_avg["recall"],
        "avg_f1_score_validation": macro_avg["f1-score"],
    }

    with open(metrics_results, "w") as json_file:
        json.dump(metrics_to_tag, json_file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("score")
    parser.add_argument(
        "--validation_results", type=str, help="Path to validation results"
    )
    parser.add_argument("--raw_data", type=str, help="Path to raw data")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription ID")
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure resource group name"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine Learning workspace name"
    )
    parser.add_argument("--asset_name", type=str, help="Model Name")
    parser.add_argument("--asset_version", type=str, help="Model Version")
    parser.add_argument("--metrics_results", type=str, help="Path to output file")

    args = parser.parse_args()

    main(
        args.validation_results,
        args.raw_data,
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.asset_name,
        args.asset_version,
        args.metrics_results,
    )
