"""
File contains useful functions for grouping singular clusters.
"""

SINGULAR_CLUSTER_INDEX = "-1"

def group_sigular_clusters(clusters):
    """
    A function that merges singular clusters into one.
    Input:
        clusters: A dictionary of clusters.
        singular_cluster_index: An index of new cluster that groups singular ones. (by default -1)
    """
    print("Grouping singular clusters:")

    # list grouped singular clusters nodes
    grouped_sigular_clusters = []
    # indices of clusters that need to be dropped as they are merged together
    clusters_to_be_dropped = []

    # iterating through clusters
    for cluster_index in clusters:
        # checking if it is singular
        if len(clusters[cluster_index])==1:
            grouped_sigular_clusters.extend(clusters[cluster_index])
            clusters_to_be_dropped.append(cluster_index)

    # dropping merged indices
    for cluster_index in clusters_to_be_dropped:
        clusters.pop(cluster_index)
    
    clusters = add_nodes_to_singular_cluster(clusters, grouped_sigular_clusters)

    return clusters

def add_nodes_to_singular_cluster(clusters, nodes):
    """
    Function extends cluster of grouped singular clusters with a list of nodes.
    Input:
        clusters: A dictionary of clusters.
        nodes: Nodes to be added to cluster of grouped singular clusters.
        singular_cluster_index: An index of new cluster that groups singular ones. (by default -1)
    """
    print("Extending singular nodes cluster:")
    if SINGULAR_CLUSTER_INDEX in clusters:
        clusters[SINGULAR_CLUSTER_INDEX].extend(nodes)
        print("Created singular images cluster with size of {} images.".format(len(nodes)))
    else:
        clusters[SINGULAR_CLUSTER_INDEX] = nodes
        print("Extended singular images cluster by {}.".format(len(nodes)))
    print("Singular images cluster has the size of {}.".format(len(clusters[SINGULAR_CLUSTER_INDEX])))

    return clusters