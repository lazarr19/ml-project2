"""
File has useful functions for creation of clusters. 
"""

def dfs(node, visited, edges, component):
    """
        Helper function for dfs traversal of the graph
        Input:
            node - node we're currently in
            visited - list of visited nodes
            edges - adjacency list for each node
            component - list of nodes in current component, function should modify this and add current node to the list
        Output:
            No output, result is the modification of lists visited and component
    """
    if node not in visited:
        visited.append(node)
        component.append(node)
        for neighbour in edges[node]:
            dfs(neighbour, visited, edges, component)


def connected_components(nodes, edges):
    """
        Function that takes strings as input and returns connected components, which reprsent the initial clustering of nodes:
        Input:
            nodes - list of nodes
            edges - adjacency list for each node
        Output:
            A dictionary mapping the index of a connected component to the list of nodes in that component
    """
    print("Creating clusters:")

    visited = []
    counter = 0
    clusters = {}
    for node in nodes:
        if node not in visited:
            clusters[counter] = []
            dfs(node, visited, edges, clusters[counter])
            counter += 1
    
    print("Successfully created {} clusters.".format(len(clusters)))
    return clusters
