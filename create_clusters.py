import argparse
import traceback
from pathlib import Path
from gps_helper import extract_gps_from_images
from clusters_gps import gps_merge_clusters
from files_helper import save_results, load_images, load_pairs_data
from clusters_creation import connected_components
from clusters_merging import merge_clusters_iteratively, merge_small_clusters
from clusters_singular import group_sigular_clusters, add_nodes_to_singular_cluster

def main(IMAGES_FOLDER=Path("datasets"), RESULTS_FOLDER=Path("results"), PAIRS_FILE=Path("netvlad/pairs-netvlad.txt"), STRONG_EDGES_THRESHOLD=0.35, WEAK_EDGES_THRESHOLD=0.2, \
        GPS_COUNT_THRESH=4, GPS_DISTANCE_THRESH=30):
    # set file for exporting clusters
    CLUSTERS_FILE = RESULTS_FOLDER / "clusters.json"

    # load all nodes
    all_nodes = load_images(IMAGES_FOLDER)

    # load strong edges with its nodes
    strong_nodes, strong_edges = load_pairs_data(PAIRS_FILE, STRONG_EDGES_THRESHOLD, IMAGES_FOLDER)

    # create strong clusters
    strong_clusters = connected_components(strong_nodes, strong_edges)

    # load weaker edges with its nodes
    weak_nodes, weak_edges = load_pairs_data(PAIRS_FILE, WEAK_EDGES_THRESHOLD, IMAGES_FOLDER)

    # REMIDER, weak_nodes and weak_edges are supersets of strong_nodes and strong_edges!

    # new nodes with just weak links (and not strong links)
    new_nodes = list(set(weak_nodes).difference(set(strong_nodes)))

    # advanced merge, considering weaker edges, but under more strict conditions
    merged_strong_clusters = merge_clusters_iteratively(new_nodes, weak_edges, strong_clusters)

    # merge of the clusters that don't have too much nodes
    merged_strong_and_small_clusters = merge_small_clusters(weak_edges, merged_strong_clusters)

    # load GPS data of images
    images_gps = extract_gps_from_images(IMAGES_FOLDER)

    # merge of clusters based on gps data
    merged_clusters = gps_merge_clusters(images_gps, merged_strong_and_small_clusters, GPS_COUNT_THRESH, GPS_DISTANCE_THRESH)

    # merge all singular clusters
    merged_clusters_grouped_singular = group_sigular_clusters(merged_clusters)

    # really weak nodes are ones that do not even have weak edges
    nodes_without_weak_edges = list(set(all_nodes).difference(set(weak_nodes)))

    # add nodes that do not even have weak edges to cluster of singularities
    final_clusters = add_nodes_to_singular_cluster(merged_clusters_grouped_singular, nodes_without_weak_edges)

    # save resulting clusters
    save_results(final_clusters, CLUSTERS_FILE)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    try:
        parser.add_argument('--image_dir', type=Path, default=Path("datasets"), required=False)
        parser.add_argument('--results_dir', type=Path, default=Path("results"), required=False)
        parser.add_argument('--pairs_file', type=Path, default=Path("netvlad/pairs-netvlad.txt"), required=False)
        parser.add_argument('--strong_edg_thresh', type=float, default=0.35, required=False)
        parser.add_argument('--weak_edg_thresh', type=float, default=0.2, required=False)
        parser.add_argument('--gps_count_thresh', type=int, default=4, required=False)
        parser.add_argument('--gps_distance_thresh', type=float, default=30, required=False)
        args = parser.parse_args()
        main(args.image_dir, args.results_dir, args.pairs_file, args.strong_edg_thresh, args.weak_edg_thresh, args.gps_count_thresh, args.gps_distance_thresh)
    except:
        print(traceback.format_exc())