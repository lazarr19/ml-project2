import argparse
import os
import json
import shutil
import traceback
from pathlib import Path
from clusters_singular import SINGULAR_CLUSTER_INDEX


def calculate_number_of_digits(number):
    counter = 0
    while number!=0:
        counter += 1
        number = number // 10
    return counter

def building_number_to_string(number, max_number_of_digits):
    number_of_digits = calculate_number_of_digits(number)
    zeros_to_add = max_number_of_digits - number_of_digits
    return ("0"*zeros_to_add) + str(number)

def main(IMAGE_FOLDER=Path("datasets"), RESULTS_FOLDER=Path("results")):
    
    CLUSTERS_FOLDER = RESULTS_FOLDER / "building_images"
    CLUSTERS_FILE = RESULTS_FOLDER / "clusters.json"

    try:
        with open(CLUSTERS_FILE, "r") as read_file:
            clusters = json.load(read_file)
    except:
        print("Error reading {}.".format(CLUSTERS_FILE))
        print(traceback.format_exc())

    # -1 because of the singular cluster
    max_number_of_digits = calculate_number_of_digits(len(clusters)-1)

    # number of current building
    counter = 1

    for cluster_index in sorted(clusters, key=lambda key: len(clusters[key]), reverse=True):
        folder_name = "building_" + building_number_to_string(counter, max_number_of_digits)

        if cluster_index == SINGULAR_CLUSTER_INDEX:
            folder_name = "NotAssigned"
            # do not update counter
            counter -= 1

        # create new folder if it does not exists
        output_folder = CLUSTERS_FOLDER / folder_name

        for cluster_element in clusters[cluster_index]:
            destination_path = cluster_element.replace(str(IMAGE_FOLDER), str(output_folder), 1)
        
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.copyfile(cluster_element, destination_path)

        counter += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    try:
        parser.add_argument('--image_dir', type=Path, default=Path("datasets"), required=False)
        parser.add_argument('--results_dir', type=Path, default=Path("results"), required=False)
        args = parser.parse_args()
        main(args.image_dir, args.results_dir)
    except:
        print(traceback.format_exc())