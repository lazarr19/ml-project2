import argparse
from pathlib import Path
from hloc import extract_features, pairs_from_retrieval
import traceback

def extract_features_from_images(images_folder, outputs):
    """
    Function generates global-feats-netvlad.h5 file at outputs folder with features of images extracted using netvlad.

    Input:
        images_folder: A folder containing images.
        outputs: A Path object folder to create global-feats-netvlad.h5 file in it.
    """
    # if you want to change configuration you can do it here
    netvlad_conf = extract_features.confs['netvlad']

    try:
        return extract_features.main(netvlad_conf, images_folder, outputs)
    except:
        print("An error occured while trying to extract features from images!")
        print(traceback.format_exc())


def generate_most_similar_pairs(retrieval_path, outputs, num_to_match):
    """
    Function creates a file 'pairs-netvlad.txt' with 
    Input:
        retrieval_path: The path of the generated 'global-feats-netvlad.h5' file of extract_features_from_images function.
        outputs: A Path object folder to create global-feats-netvlad.h5 file in it.
        num_to_match: An integer of how many most similar pairs we look for for one image.
    
    As a result, the function generates 'pairs-netvlad.txt' file with top num_to_match most similar pairs for each image.
    """
    pairs = outputs / 'pairs-netvlad.txt'
    pairs_from_retrieval.main(retrieval_path, pairs, num_matched=num_to_match)


def main(image_dir, outputs_dir, num_to_match, ):
    retrieval_path = extract_features_from_images(image_dir, outputs_dir)
    generate_most_similar_pairs(retrieval_path, outputs_dir, num_to_match)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    try:
        parser.add_argument('--image_dir', type=Path, default=Path("datasets"), required=False)
        parser.add_argument('--outputs_dir', type=Path, default=Path("netvlad"), required=False)
        parser.add_argument('--num_to_match', type=int, required=True)
        args = parser.parse_args()
        main(args.image_dir, args.outputs_dir, args.num_to_match)
    except:
        print(traceback.format_exc())