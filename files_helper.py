"""
    File containing functions for image files copying, resizing and loading.
"""
import os
import json
import shutil
import traceback
from pathlib import Path
from PIL import Image

def remove_non_ascii(string):
    """
    Function removes non-ascii characters from string.
    Input:
        string: A string.
    Return:
        A string without non-ascii characters.
    """
    return ''.join(char for char in string if (ord(char) < 128) and char!='`')

def copy_files(data_folder, output_folder, EXTENSIONS = ('.jpg','.JPG','.png','.PNG')):
    """
    Function copies all files from data_folder ending with EXTENSIONS to output_folder.
    
    Arguments:
        data_folder: A Path object of the folder containing files.
        output_folder: A Path object of the folder where new files will be copied.
        EXTENSIONS: A tuple of picture extensions to look for in files.
    """
    DATA_FOLDER = str(data_folder)
    OUTPUT_FOLDER = str(output_folder / data_folder.name)

    print("Copying images from {} to {}:".format(DATA_FOLDER, OUTPUT_FOLDER))

    counter = 0

    for (dirpath, dirnames, filenames) in os.walk(DATA_FOLDER):
        
        # create path for output folder
        output_folder = remove_non_ascii(dirpath.replace(DATA_FOLDER, OUTPUT_FOLDER, 1))
        
        # create new folder if it does not exists
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        # iterate through files
        for filename in filenames:
            # if it is a picture
            if filename.endswith(EXTENSIONS) and not filename.startswith('.'):
                try:
                    # source and destination paths
                    source_path = os.path.join(dirpath, filename)
                    destination_path = os.path.join(output_folder, filename)

                    # open image
                    image = Image.open(source_path)

                    # extract metadata
                    exif = image.info['exif']

                    # save newly created resized image
                    image.save(destination_path, exif=exif)

                    # just copy the file
                    shutil.copyfile(source_path, destination_path)
                    
                    counter += 1
                    
                except :
                    print('Error with file {} in dir {}. Not copying it.'.format(filename, dirpath))
    
    print('Successfully copied {} files.'.format(counter))


def resize_images(data_folder, RESIZE_COEFFICIENT = 1):
    """
    Directly change image width and height by dividing with RESIZE_COEFFICIENT.
    
    NOTE: Image is being changed! Previous version will not be saved! Be sure to copy images before.
    
    Arguments:
        data_folder: A Path object of the folder containing images.
        RESIZE_COEFFICIENT: A coefficient to divide width and height of an image.
    """
    if RESIZE_COEFFICIENT == 1:
        print('No resize needed since coefficient is 1.')
        return
    
    DATA_FOLDER = str(data_folder)
    
    print("Resizing images in folder {} with resize coefficient {}:".format(DATA_FOLDER, RESIZE_COEFFICIENT))

    counter = 0
    
    for (dirpath, _, filenames) in os.walk(DATA_FOLDER):
        # iterate through files
        for filename in filenames:
            try:
                # source and destination paths
                image_path = os.path.join(dirpath, filename)

                # open image
                image = Image.open(image_path)

                # extract metadata
                exif = image.info['exif']

                # size after resizing
                new_size = tuple(coord_size//RESIZE_COEFFICIENT for coord_size in image.size)

                # resize image
                image.thumbnail(new_size, Image.ANTIALIAS)

                # save newly created resized image
                image.save(image_path, optimize=True, exif=exif, quality=95)
                
                counter += 1
            except :
                print("Error with file {} in dir {}.".format(filename, dirpath))

    print('Successfully resized {} images with the resize coefficient {}.'.format(counter, RESIZE_COEFFICIENT))


def load_images(data_folder, EXTENSIONS = ('.jpg','.JPG','.png','.PNG')):
    """
    Load images matching EXTENSIONS into set of their paths in the provided DATA_FOLDER.
    
    Arguments:
        data_folder: A Path object of the folder containing images.
        PICTURE_EXTENSIONS: A tuple of picture extensions to look for in files.
    
    Return:
        images: A Python set containing paths to images.
    """

    DATA_FOLDER = str(data_folder)

    print("Loading images from {}:".format(data_folder))

    images = set()
    
    for (dirpath, _, filenames) in os.walk(DATA_FOLDER):
        # iterate through files
        for filename in filenames:
            # if it is a picture
            if filename.endswith(EXTENSIONS) and not filename.startswith('.'):
                try:
                    # source and destination paths
                    image_path = Path(os.path.join(dirpath, filename))
                    
                    # add image path
                    images.add(str(image_path))
                except :
                    print('Error with file {} in dir {}'.format(filename, dirpath))
                    print(traceback.format_exc())
    
    print("Successfully loaded {} images.".format(len(images)))
    
    # return all image paths
    return images


def calculate_total_edges(edges):
    """
    A helper function for calculating total number of edges.
    Input:
        edges: A dictionary of edges for each node.
    Return:
        Total number of edges. (undirected)
    """
    total_edges = 0

    for image in edges:
        total_edges += len(edges[image])
    
    # edges should be undirected so we divide by 2
    total_edges = total_edges//2
    return total_edges

def load_pairs_data(filename, edge_thresh, image_folder):
    """
        Function that loads pairs data from filename
        Input:
            filename - relative filepath to the document containg paris data. Each line of the file has the following format:
            
                        image1 image2 score
            
                       image1 and image2 are two images that represent a pair, and score represents the confidence of the ML
                       model that those images should form a pair
            
            edge_thresh - pairs with score lower than edge_thresh are discarded
        
        Output:
            A graph, represented by list of its nodes and adjacency list for each node
    """
    
    print("Loading nodes and pairs with the edge threshold {}:".format(edge_thresh))

    nodes = []
    edges = {}
    
    with open(filename, "r") as file:
        lines = file.readlines()

        for line in lines:
            [first_image_path, second_image_path, weight] = line.split()

            first_image = str(image_folder / first_image_path)
            second_image = str(image_folder / second_image_path)
            
            if float(weight) < edge_thresh:
                continue
                
            if first_image not in nodes:
                nodes.append(first_image)
                edges[first_image] = []

            if second_image not in nodes:
                nodes.append(second_image)
                edges[second_image] = []

            if second_image not in edges[first_image]:
                edges[first_image].append(second_image)
                
            if first_image not in edges[second_image]:
                edges[second_image].append(first_image)

    print("Successfully loaded {} nodes and {} edges.".format(len(nodes), calculate_total_edges(edges)))
    return nodes, edges

def save_results(dictionary, file):
    """
    A helper function for saving dictionary as file.
    Input:
        dictionary: Python dictionary.
        file: Path to file where we will save dictionary.
    """
    print("Saving results to {}:".format(str(file)))
    
    # create json object from dictionary
    json_dict = json.dumps(dictionary)

    with open(str(file), "w") as f:
        f.write(json_dict)
    
    print("Successfully saved results.")
