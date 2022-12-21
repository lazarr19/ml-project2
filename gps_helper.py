"""
    File containing functions for extraction of GPS from images.
"""
import os
import traceback
from pathlib import Path
from exif import Image as exifImage

def valid_gps_coordinates(gps):
    """
    Input:
        gsp: A tuple of three coordinates: degrees, minutes and seconds.
    Return:
        Returns True if all coordinates are not zero.
    """
    return not (gps[0]==0 and gps[1]==0 and gps[2]==0)


def get_gps_degree(gps):
    """
    Input:
        gsp: A tuple of three coordinates: degrees, minutes and seconds.
    Return:
        Returns gps coordinate in degrees as a float number.
    """
    return float(gps[0]) + float(gps[1])/60 + float(gps[2])/3600


def get_gps_degrees(latitude, longitude):
    """
    Input:
        latitude: A tuple of three coordinates: degrees, minutes and seconds.
        longitude: A tuple of three coordinates: degrees, minutes and seconds.
    Return:
        Returns a tuple of two elements, latitude and longitude in degrees as floating number.
    """
    return (get_gps_degree(latitude), get_gps_degree(longitude))


def has_gps_coordinates(image):
    """
    Input:
        image: An exifImage object (from exif import Image as exifImage).
    Return:
        Returns a boolean if image has both latitude and longitude and if they are valid.
    """
    # list of all metadata for an image
    image_metadata = image.list_all()
    
    # checking if it has metadata about gps
    has_gps_metadata = ('gps_latitude' in image_metadata) and ('gps_longitude' in image_metadata)
    if not has_gps_metadata:
        return False
    
    # checking if the data is valid
    has_valid_gps_metadata = valid_gps_coordinates(image.gps_longitude) and valid_gps_coordinates(image.gps_longitude)
    
    return has_valid_gps_metadata


def extract_gps_from_images(data_folder):
    """
    Function creates a dictionary which maps image paths to corresponding GPS values.

    Arguments
        data_folder: A Path object of the folder containing images.
    
    Return:
        images: A dictionary mapping image path to its GPS coordinates tuple.
    """
    DATA_FOLDER = str(data_folder)
    
    print("Loading GPS coordinates from images in folder {}:".format(DATA_FOLDER))

    # couters for info
    counter_gps = 0
    counter_total = 0
    
    # dictionary mapping image path to its gps
    images_gps = {}
    
    for (dirpath, dirnames, filenames) in os.walk(DATA_FOLDER):
        for filename in filenames:
            # current image path
            image_path = str(Path(os.path.join(dirpath, filename)))
            try:
                with open(image_path, "rb") as image_file:
                    # get image as exifImage
                    img = exifImage(image_file)
                    
                    if img.has_exif:
                        
                        if has_gps_coordinates(img):
                            images_gps[image_path] = get_gps_degrees(img.gps_latitude, img.gps_longitude)
                            
                            counter_gps+=1
                        
                    else:
                        info = "does not contain any EXIF information"
                        print(f"Image {image_file.name}: {info}")
                        
            except:
                print('Error with file {} in dir {}'.format(filename, dirpath))
                print(traceback.format_exc())
            
            counter_total += 1
    
    print('Got GPS coordinates of {} out of {} images.'.format(counter_gps, counter_total))
    return images_gps

