
# Deep Learning-Based Clustering of Images of Damaged Buildings
ML4Science Project, Machine Learning (CS-433), Fall 2022

## Table of contents

* [Repository description](#repository-description)
* [Folders description](#folders-description)
* [Changes made on hloc](#changes-made-on-hloc)
* [Requirements](#requirements)
* [Code files descriptions](#code-files-descriptions)
	* files_helper.py
    * gps_helper.py
    * cluster_creation.py
    * clusters_merging.py
    * clusters_gps.py
    * clusters_singular.py
* [Scripts](#scripts)
    * copy_images.py
    * resize_images.py
    * hloc_netvlad.py
    * create_clusters.py
    * export_clusters.py
* [How to use the repo](#how-to-use-the-repo)

### Repository description

We present the scripts we created for the unsupervised clustering of images. We provide tools to copy and resize your images. The tool [Hierarchical-Localization](https://github.com/cvg/Hierarchical-Localization/tree/master/hloc)  is included with slight changes for our use case. It is used to extract features from images and generate similarity scores between them. That score is utilized for the clusterization of the initial images, which are finally exported, with the preservation of the folder structure.

### Folders description

* datasets - tool searches for images in this folder. The process will preserve the tree structure of folders.
* hloc - the tool [Hierarchical-Localization](https://github.com/cvg/Hierarchical-Localization/tree/master/hloc) we used to generate features from images. The tool is slightly modified, and those modifications are described [here](#changes-made-on-hloc).
* netvlad - the folder where we store image features and generate the most similar pairs of images.
* results - the folder where we store clusters.json file that is a dictionary of clusters. Also there you can create your clusters with export_clusters.py.

### Changes made on hloc

This tool does two things. First, it generates features for images. Second, it uses those features to compare images and find the most similar ones. Files that we use in our implementation are extract_features.py and pairs_from_retrieval.py.

We had to change the code to get what we wanted. The original code only gives pairs of images that are similar. We wanted to know how similar the pictures actually are. So, we changed the code and added a third element to a pair of two similar images - the similarity weight.
It was already calculated in the original code, we just adjusted the code to print it. The file we changed is pairs_from_retrieval.py.

    edited: pairs_from_retrieval.py

Other changes we made are mostly technical. None of them has effects on the outputs the code produces. We list them here for completeness:

One of the problems that occurred was an error raised by the code for creating workers when using torch. To make it work, we set `num_workers` variable to zero. As a result, calculations are not parallelized, but it is still feasible for our dataset. For example, the extraction of features on our local machines took 7 hours for ~11300 images. Those settings can be modified accordingly, although changing them might require some additional tinkering with the environment.

Changes for num_workers:

    extract_features, line 250: num_workers is 1 in the original code, in ours, it is 0

Additionally, the documentation on the repo [Hierarchical-Localization](https://github.com/cvg/Hierarchical-Localization) says that pycolmap is no longer needed, however, they still import it in one script. We commented out its import in the:

    utils/parsers.py, line 5: # import pycolmap

We have opted for this option because the installation was producing dependency issues. The alternative is to install pycolmap.

Keep in mind that the remainder of the code works independently of the tool used in this step. Ie. another tool that creates output in the format: 

    path_to_first_image, path_to_second_image, similarity_score

is sufficient and the usage of this hloc can be avoided.

### Requirements

The required installations are listed in requirements.txt. Keep in mind that pycolmap is preferred, but not needed ([here](#changes-made-on-hloc)).

Of course, you can install them with:

    $ pip install -r requirements.txt.

### Code files descriptions

#### files_helper.py
The file contains functions for image file copying, resizing, and loading.

#### gps_helper.py
The file contains functions for the extraction of GPS from images.

#### cluster_creation.py
File has useful functions for the creation of clusters.

#### clusters_merging.py
File has useful functions for merging clusters. 

#### clusters_gps.py
File with useful functions for merging clusters based on their GPS.

#### clusters_singular.py
The file contains useful functions for grouping singular clusters.

### Scripts

#### copy_images.py
Script copies image files with default extensions ('.jpg','.JPG','.png','.PNG') from **image_dir** to **export_dir**. 

Arguments:
* --**image_dir**: type=Path, required=True
* --**export_dir**: type=Path, default=Path("datasets"), required=False

#### resize_images.py
Script resizes images in **image_dir** with resize coefficient **resize_coefficient**.

Arguments:
* --**image_dir**: type=Path, default=Path("datasets"), required=False
* --**resize_coefficient**: type=int, default=1, required=False

#### hloc_netvlad.py
The script extracts features of images in **outputs_dir/global-feats-net lead.h5**, finds **num_to_match** most similar pairs for each image and stores it in **outputs_dir/pairs-netvlad.txt**.

Arguments:
* --**image_dir**: type=Path, default=Path("datasets"), required=False
* --**outputs_dir**: type=Path, default=Path("netvlad"), required=False
* --**num_to_match**: type=int, required=True

#### create_clusters.py
Images are loaded from **image_dir**. It also loads edges and their weight from **pairs_file**. The script first creates strong clusters of images with **strong_edg_thresh**, then expands it by new edges of **weak_edg_thresh**, and merges clusters based on some criteria described in files. After, it merges clusters that have at least **gps_count_thresh** nodes with GPS data. It merges clusters that are not separated more than **gps_distance_thresh**. The results are saved in **results_dir** in the *clusters.json* file.

Arguments:
* --**image_dir**: type=Path, default=Path("datasets"), required=False
* --**results_dir**: type=Path, default=Path("results"), required=False
* --**pairs_file**: type=Path, default=Path("netvlad/pairs-netvlad.txt"), required=False
* --**strong_edg_thresh**: type=float, default=0.35, required=False
* --**weak_edg_thresh**: type=float, default=0.2, required=False
* --**gps_count_thresh**: type=int, default=4, required=False
* --**gps_distance_thresh**: type=float, default=30, required=False

#### export_clusters.py
Script copies images from **image_dir** to **results_dir/building_images** and creates clusters that are saved in **results_dir/clusters.json** by *create_clusters.py* script. It preserves folder structure.

* --**image_dir**: type=Path, default=Path("datasets"), required=False
* --**results_dir**: type=Path, default=Path("results"), required=False


### How to use the repo

Assume that you have a folder of images at **src_path** and you want to resize them by 2 and create clusters of those images.
An example of how to use this repo is the following:

    python copy_images.py --image_dir src_path
    python resize_images.py --resize_coefficient 2
    python hloc_netvlad.py --num_to_match 10
    python create_clusters.py
    python export_clusters.py

**Team**: mleco

**Team members**: Aleksa Milisavljevic, Lazar Radojevic, Luka Radic