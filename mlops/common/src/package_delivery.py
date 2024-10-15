# Copyright (C) 2023 Siemens AG
# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.
#
# SPDX-License-Identifier: MIT

"""
A Python module to execute parameterized Azure ML Pipeline Step
"""

import argparse
import logging
import os
import sys

from azure.ai.ml import MLClient
from azure.identity import (
    ChainedTokenCredential,
    ManagedIdentityCredential,
    AzureCliCredential,
)
from azure.keyvault.secrets import SecretClient

from common.src.package_delivery_mm import ModelManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


def main(
    keyvault_name: str,
    iot_hub_connection_string_secret_name: str,
    event_hub_connection_string_secret_name: str,
    device_id: str,
    edge_package_name: str,
    edge_package_version: str,
    deploy_environment: str,
):
    # Getting credentials for User Managed Identity added to Compute Cluster in order to 
    # use related Azure resources
    azure_credential = ChainedTokenCredential(
        AzureCliCredential(),
        ManagedIdentityCredential(client_id=os.getenv("DEFAULT_IDENTITY_CLIENT_ID")),
    )

    # ml_client 
    ml_client = MLClient(
        credential=azure_credential,
        subscription_id=os.environ.get("AZUREML_ARM_SUBSCRIPTION"),
        resource_group_name=os.environ.get("AZUREML_ARM_RESOURCEGROUP"),
        workspace_name=os.environ.get("AZUREML_ARM_WORKSPACE_NAME"),
    )

    # connecting Azure Keyvault to get access to IoTHub as the required credentials and connection strings are stored in KeyVault
    secret_client = SecretClient(
        credential=azure_credential,
        vault_url=f"https://{keyvault_name}.vault.azure.net/",
    )
    iot_hub_con_str = secret_client.get_secret(
        iot_hub_connection_string_secret_name
    ).value
    iot_event_hub_con_str = secret_client.get_secret(
        event_hub_connection_string_secret_name
    ).value

    # In case the version of the package is defined as "latest", 
    # we need to search for the name in the Model Registry and get the Edge Deployment Package
    # with the same name and the highest version number registered
    if edge_package_version == "latest":
        package = None
        for p in ml_client.models.list(name=edge_package_name):
            package = p if package is None or p.version > package.version else package
    else:
        package = ml_client.models.get(
            name=edge_package_name, version=edge_package_version
        )

    # Once the package is found we want to store the environment name where the package is delivered, 
    # so we update the "deploy_environment" in the tags of the registered package
    package_tags = package.tags
    package_tags["deploy_environment"] = deploy_environment
    package.tags = package_tags
    ml_client.models.create_or_update(model=package)

    # Then we do the same with the model belongs to the package
    model_name = package_tags["model_name"]
    model_version = package_tags["model_version"]

    model = ml_client.models.get(name=model_name, version=model_version)
    model_tags = model.tags
    model_tags["deploy_environment"] = deploy_environment
    model.tags = model_tags
    ml_client.models.create_or_update(model=model)

    # Now we can find the path of the proper package zip file in the Storage Account
    datastore_name = package.path.split("/")[
        package.path.split("/").index("datastores") + 1
    ]
    datastore = ml_client.datastores.get(datastore_name)
    blob_name = package.path.split("/paths/")[1]

    logger.info(f"device_id: {device_id}")
    logger.info("package.model_version : %s", package.tags["packageid"])
    logger.info(f"package.name: {package.name}")
    logger.info(f"package.version: {package.version}")
    logger.info(f"datastore.account_name: {datastore.account_name}")
    logger.info(f"datastore.container_name: {datastore.container_name}")
    logger.info(f"blob_name: {blob_name}")

    model_manager = ModelManager(
        iot_hub_con_str=iot_hub_con_str,
        iot_event_hub_con_str=iot_event_hub_con_str,
        device_id=device_id,
        storage_account_name=datastore.account_name,
        container_name=datastore.container_name,
        blob_name=blob_name,
        azure_credential=azure_credential,
        package_id=package.tags["packageid"],
        package_name=package.name,
        package_version=package.version,
    )

    # Start the delivery to AI Model Manager
    try:
        model_manager.start_event_hub_loop()

        # Check the result of the delivery
        if model_manager.state == "Success":
            logger.info(
                f"Successful delivery '{model_manager.delivery_id}' to '{model_manager.device_id}'."
            )
        else:
            raise ValueError(
                f"Delivery '{model_manager.delivery_id}' to '{model_manager.device_id}' failed with "
                f"state '{model_manager.state}'."
            )
    except Exception as mme:
        raise ValueError(
            f"""Delivery '{model_manager.delivery_id}' to '{model_manager.device_id}' \
                failed with state '{model_manager.state}'.
                and error: {mme}
                """
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--keyvault_name",
        type=str,
        help="The name of the Azure Key vault that stores secrets needed for the delivery",
    )
    parser.add_argument(
        "--iot_hub_connection_string_secret_name",
        type=str,
        help="The name of the secret in Azure Key vault that stores the iot-hub-connections-string",
    )
    parser.add_argument(
        "--event_hub_connection_string_secret_name",
        type=str,
        help="The name of the secret in Azure Key vault that stores the event_hub_connection_string",
    )
    parser.add_argument("--device_id", type=str, help="target device id")
    parser.add_argument("--edge_package_name", type=str, help="edge package name")
    parser.add_argument(
        "--edge_package_version",
        type=str,
        help="edge package version",
        default="latest",
    )
    parser.add_argument(
        "--deploy_environment",
        type=str,
        help="Environment where asset is deployed",
        default="dev",
    )

    args = parser.parse_args()

    main(
        args.keyvault_name,
        args.iot_hub_connection_string_secret_name,
        args.event_hub_connection_string_secret_name,
        args.device_id,
        args.edge_package_name,
        args.edge_package_version,
        args.deploy_environment,
    )
