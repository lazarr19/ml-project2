"""
File with useful functions for merging clusters based on their GPS.
"""

import numpy as np
import haversine as hs
from haversine import Unit

def get_median_gps(cluster_lat, cluster_lon, cluster_index):
    """
    Input:
        cluster_lat: A dictionary mapping cluster index to list of latitudes in a cluster.
        cluster_lon: A dictionary mapping cluster index to list of longitudes in a cluster.
        cluster_index: An index of a cluster.
    Returns:
        Returns a tuple of two elements with latitude median and longitude median.
    """
    return (np.median(cluster_lat[cluster_index]), np.median(cluster_lon[cluster_index]))

def get_count_lat_long_for_clusters(clusters, images_gps):
    gps_count = {}
    cluster_lat = {}
    cluster_lon = {}
    
    for cluster_index in clusters:
        counter = 0
        cluster_lat[cluster_index] = []
        cluster_lon[cluster_index] = []
        for node in clusters[cluster_index]:
            if node in images_gps.keys():
                counter += 1
                (lat, lon) = images_gps[node]
                cluster_lat[cluster_index].append(lat)
                cluster_lon[cluster_index].append(lon)

        gps_count[cluster_index] = counter
    
    return gps_count, cluster_lat, cluster_lon

def gps_merge_clusters(gps, old_clusters, gps_count_thresh = 4, distance_thresh = 30):
    """
        Function that merges clusters based on the proximity of the gps location
        Input:
            gps - a dictionary that maps an image to its gps coordinates
            old_clusters - previously created clusters, some of them will be merged together based on gps data
            gps_count_thresh - number of nodes in cluster that need to have gps coordinates to consider data valid
            distance_thresh - distance in meters bellow which two clusters will get merged
        Output:
            A dictionary that maps index of a cluster to list of nodes in that cluster
    """
    print("Merging clusters by GPS:")

    new_clusters = old_clusters.copy()

    # dictionaries of clusters to count, list of latitudes, and list of longitudes
    gps_count, cluster_lat, cluster_lon = get_count_lat_long_for_clusters(old_clusters, gps)
        
    continue_iterating = True
    merge_count = 0
    while continue_iterating:

        continue_iterating = False

        # iterate trough clusters
        for cluster1 in new_clusters:
            for cluster2 in new_clusters:
                if cluster2 <= cluster1:
                    continue
                
                # if both clusters have enough nodes with gps
                if gps_count[cluster1]>=gps_count_thresh and gps_count[cluster2]>=gps_count_thresh:
                    
                    # get medians of latitude and longitude of clusters
                    gps_median1 = get_median_gps(cluster_lat, cluster_lon, cluster1)
                    gps_median2 = get_median_gps(cluster_lat, cluster_lon, cluster2)
                    
                    # calculate distance between medians
                    dist = hs.haversine(gps_median1, gps_median2, unit=Unit.METERS)
                    
                    # if the distance is lower than threshold
                    if dist <= distance_thresh:
                        continue_iterating = True

                        # update values
                        new_clusters[cluster1] = new_clusters[cluster1] + new_clusters[cluster2]
                        gps_count[cluster1] = gps_count[cluster1] + gps_count[cluster2]
                        cluster_lat[cluster1] = cluster_lat[cluster1] + cluster_lat[cluster2]
                        cluster_lon[cluster1] = cluster_lon[cluster1] + cluster_lon[cluster2]
                        
                        # remove second cluster
                        new_clusters.pop(cluster2)
                        
                        merge_count += 1
                        break

            if continue_iterating:
                break
    
    print("In total {} merges happened".format(merge_count))
    return new_clusters