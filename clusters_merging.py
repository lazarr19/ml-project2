"""
File has useful functions for merging clusters. 
"""

def agree_to_merge(cluster1, cluster2, edges, confidence_threshold=1/6):
    """
        A helper function that decides if the first cluster (cluster1) wants to merge with the second cluster (cluster2).
        Input:
            cluster1 - list of nodes in the first cluster
            cluster2 - list of nodes in the second cluster
            edges - adjacency list for each node
            confidence_threshold - threshold that represents how much should clusters be connected for them to get merged
                                   empirically, the value should be around ~1/6 if edges are generated from netvlad with
                                   edge_thresh of 0.2
        Output:
            A boolean value that represents if first cluster wants to merge with the second.
    """
    
    ok = 0 #number of nodes for merge
    not_ok = 0 #number of nodes against merge, we can use this to return from function earlier
    
    cluster1_length = len(cluster1)
    
    for image in cluster1:
        if len(set(edges[image])&set(cluster2))>=confidence_threshold*len(edges[image]):
            ok += 1
        else:
            not_ok += 1
        
        # if we already have enough for break
        if ok >= confidence_threshold * cluster1_length:
            break
            
        # if we already have enough for against
        if cluster1_length - not_ok < confidence_threshold * cluster1_length:
            break
        
    # if we do not have enough images that agree from one cluster return False
    if ok < confidence_threshold * cluster1_length:
        return False
    
    return True


def merge(cluster1, cluster2, edges, confidence_threshold=1/6):
    """
        A helper functions that decides if two clusters should get merged together.
        Input:
            cluster1 - list of nodes in the first cluster
            cluster2 - list of nodes in the second cluster
            edges - adjacency list for each node
            confidence_threshold - threshold that represents how much should clusters be connected for them to get merged
                                   empirically, the value should be around ~1/6 if edges are generated from netvlad with
                                   edge_thresh of 0.2
        Output:
            A boolean value that represents if we should merge two clusters together
        
        Clusters will be merged together if and only if the following condition holds for both clusters:
            
            confidence_threshold amount of nodes (ie. 1/6 of nodes by default) have at least confidence_threshold edges
            in the other cluster (ie. 1/6 of the total number of edges they are connected to).
        
    """
    cluster1_agrees = agree_to_merge(cluster1, cluster2, edges, confidence_threshold)
    
    # if first cluster does not want to merge we won't merge
    if not cluster1_agrees:
        return False
    
    cluster2_agrees = agree_to_merge(cluster2, cluster1, edges, confidence_threshold)
    
    # since we know that cluster1 already agrees, decision is on cluster2
    return cluster2_agrees

def create_new_clusters_for_non_clustered_nodes(non_clustered_nodes, old_clusters):
    """
    A function adds non clustered nodes as singular clusters to already created clusters.
    Input:
        non_clustered_nodes: A list of nodes that are not clustered
        old_clusters: Dictionary of already existing clusters.
    Return:
        New dictionary of clusters with non clustered nodes now clustered as singular clusters.
    """
    new_clusters = old_clusters.copy()
    
    # start from the index after last cluster
    counter = len(old_clusters)
    for node in non_clustered_nodes:
        # add new cluster of only one new node
        new_clusters[counter] = [node]
        counter += 1
    return new_clusters

def merge_clusters_iteratively(non_clustered_nodes, edges, old_clusters):
    """
        Function that merges clusters selctively based on the edges with lower edge_thresh.
        Input:
            non_clustered_node - nodes that haven't been clustered so far
            edges - adjacency list (with weaker edge_thresh)
            old_clusters - clusters already created, some of which will get merged based on the new edges
        Ouput:
            A dictionary mapping the index of the cluster to the list of nodes in that cluster
    """
    print("Merging clusters based on the edges with lower edge threshold:")

    #
    new_clusters = create_new_clusters_for_non_clustered_nodes(non_clustered_nodes, old_clusters)
    
    #In each iteration we'll go over all pairs and see if we can merge two of them
    
    continue_iterating = True #variable that stores the decision if we should continue iterating, if nothing changes, it becomes False
    first_to_consider = 0 #first next cluster to consider
    previosly_merged = -1 #index of the cluster which was merged in the previous step
    merge_count = 0 #number of merges
    
    # first_to_consider and previosly_merged are used for optimizing the code, ie. reducing the number of pairs of clusters
    # we consider in each iteration to only ones which are necessary
    while continue_iterating:

        continue_iterating = False

        # iterate trough clusters
        for i in new_clusters.keys():

            # find first cluster to consider
            if i < first_to_consider:
                continue

            first_to_consider = i

            # iterate again to find a match
            for second_cluster in new_clusters.keys():

                if first_to_consider == second_cluster:
                    continue

                # find new cluster so that it is not already merged
                if second_cluster < first_to_consider and not first_to_consider == previosly_merged:
                    continue

                # check if clusters want to merge
                if merge(new_clusters[first_to_consider], new_clusters[second_cluster], edges):
                    
                    # update previously merged
                    previosly_merged = first_to_consider
                    
                    # update new cluster
                    new_clusters[first_to_consider] = new_clusters[first_to_consider] + new_clusters[second_cluster]
                    
                    continue_iterating = True
                    
                    # remove merged cluster
                    new_clusters.pop(second_cluster)
                    
                    merge_count += 1
                    break

            if continue_iterating:
                break

    print("In total {} merges happened.".format(merge_count))
    return new_clusters

def create_belonging_cluster(clusters):
    """
    Function creates dictionary that maps node to cluster it belongs to.
    Input:
        clusters: A dictionary of clusters.
    Return:
        A dictionary that maps node to cluster it belongs to.
    """
    # mapping from each node to a cluster he's in
    belonging_cluster = {} 
    for cluster_index in clusters:
        for node in clusters[cluster_index]:
            belonging_cluster[node] = cluster_index
    return belonging_cluster

def merge_small_clusters(edges, old_clusters, cluster_size_threshold = 4, top_edges_threshold = 3):
    """
        Function for merge of the smaller clusters by using top top_edges_threshold edges voting.
        Input:
            edges - adjacency list for each node
            old_clusters - previously created clusters, some of them will be merged together
            cluster_size_threshold - upper limit to the size, bellow which we'll consider grouping this cluster with others
            top_edges_threshold - number of best edges we're going to consider
        Output:
            A dictionary mapping the index of the cluster to the list of nodes in that cluster
    """
    print("Merging smaller clusters:")

    new_clusters = old_clusters.copy()
    merge_count = 0
    continue_iterating = True
    
    while continue_iterating:

        belonging_cluster = create_belonging_cluster(new_clusters)

        continue_iterating = False

        for cluster_index in new_clusters:
            # if cluster is small enough
            if len(new_clusters[cluster_index])<=cluster_size_threshold:
                
                # indices of all clusters that we consider
                top_clusters = []
                
                # add all cluster indices to top_clusters that we want to check
                for first_node in new_clusters[cluster_index]:
                    for second_node in edges[first_node][:top_edges_threshold]:
                        top_clusters.append(belonging_cluster[second_node])
                        
                # check if there is only one cluster, other than the current to which nodes are connected
                if len(set(top_clusters).difference(set([cluster_index])))==1: 
                    
                    # get index that we will add
                    selected_cluster_index = list(set(top_clusters).difference(set([cluster_index])))[0]
                    
                    # add its nodes to current cluster
                    new_clusters[cluster_index] = new_clusters[cluster_index] + new_clusters[selected_cluster_index]
                    
                    # remove selected cluster
                    new_clusters.pop(selected_cluster_index)
                    
                    continue_iterating = True
                    merge_count += 1
                    break
                    
    print("In total {} merges happened.".format(merge_count))
    return new_clusters