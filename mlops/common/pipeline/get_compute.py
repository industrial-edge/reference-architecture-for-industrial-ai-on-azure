import argparse

from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute
from azure.identity import DefaultAzureCredential

from mlops.common.src.base_logger import get_logger

logger = get_logger(__name__)


def get_compute(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    cluster_name: str,
    cluster_size: str,
    cluster_region: str,
    min_instances: int,
    max_instances: int,
    idle_time_before_scale_down: int,
):
    """
    Retrieves an existing compute cluster or creates a new one.

    Arguments:
    subscription_id: str
        Azure subscription id
    resource_group_name: str
        Azure Machine learning resource group
    workspace_name: str
        Azure Machine learning Workspace name
    cluster_name: str
        Azure Machine learning cluster name
    cluster_size: str
        Azure Machine learning cluster size
    cluster_region: str
        Azure Machine learning cluster region
    min_instances: int
        Minimum number of nodes in the cluster
    max_instances: int
        Maximum number of nodes in the cluster
    idle_time_before_scale_down: int
        Idle time before scaling down the cluster

    Returns:
    compute_object: AmlCompute
        Azure Machine learning compute object
    """
    compute_object = None
    try:
        client = MLClient(
            DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )
        try:
            compute_object = client.compute.get(cluster_name)
            logger.info(f"Found existing compute target {cluster_name}, so using it.")
        except Exception:
            logger.error(f"{cluster_name} is not found! Trying to create a new one.")
            compute_object = AmlCompute(
                name=cluster_name,
                type="amlcompute",
                size=cluster_size,
                location=cluster_region,
                min_instances=min_instances,
                max_instances=max_instances,
                idle_time_before_scale_down=idle_time_before_scale_down,
            )
            compute_object = client.compute.begin_create_or_update(
                compute_object
            ).result()
            logger.info(f"A new cluster {cluster_name} has been created.")
    except Exception:
        logger.critical("Oops!  invalid credentials.. Try again...")
        raise
    return compute_object


def main():
    parser = argparse.ArgumentParser("get_compute")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument(
        "--resource_group_name", type=str, help="Azure Machine learning resource group"
    )
    parser.add_argument(
        "--workspace_name", type=str, help="Azure Machine learning Workspace name"
    )
    parser.add_argument(
        "--cluster_name", type=str, help="Azure Machine learning cluster name"
    )
    parser.add_argument(
        "--cluster_size", type=str, help="Azure Machine learning cluster size"
    )
    parser.add_argument(
        "--cluster_region", type=str, help="Azure Machine learning cluster region"
    )
    parser.add_argument("--min_instances", type=int, default=0)
    parser.add_argument("--max_instances", type=int, default=4)
    parser.add_argument("--idle_time_before_scale_down", type=int, default=120)

    args = parser.parse_args()
    get_compute(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.cluster_name,
        args.cluster_size,
        args.cluster_region,
        args.min_instances,
        args.max_instances,
        args.idle_time_before_scale_down,
    )


if __name__ == "__main__":
    main()
