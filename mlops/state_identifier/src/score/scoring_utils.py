import numpy as np
from sklearn.metrics.pairwise import euclidean_distances


def dunn_index(np_array: np.array, labels: np.array) -> float:  # noqa: N803
    """
    Compute the Dunn index for a dataset with given labels.

    The Dunn index is a metric used to evaluate the quality of clustering. It is defined
    as the ratio between the smallest distance between observations not in the same
    cluster to the largest intra-cluster distance.

    Arguments:
    np_array: np.array
        The test data to be evaluated.
    labels: np.array
        The labels from the validation results.

    Returns:
    float
        The Dunn index for the given data and labels.
    """
    distances = euclidean_distances(np_array)
    unique_labels = np.unique(labels)

    inter_cluster_distances = []
    intra_cluster_distances = []

    for label in unique_labels:
        intra_cluster_distance = distances[labels == label][:, labels == label].max()
        intra_cluster_distances.append(intra_cluster_distance)

        for other_label in unique_labels:
            if label != other_label:
                inter_cluster_distance = distances[labels == label][
                    :, labels == other_label
                ].min()
                inter_cluster_distances.append(inter_cluster_distance)

    dunn_index_value = min(inter_cluster_distances) / max(intra_cluster_distances)

    return dunn_index_value
