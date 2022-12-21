import argparse
import traceback
from pathlib import Path
from files_helper import resize_images

def main(image_dir, resize_coefficient=1):
    resize_images(image_dir, resize_coefficient)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    try:
        parser.add_argument('--image_dir', type=Path, default=Path("datasets"), required=False)
        parser.add_argument('--resize_coefficient', type=int, default=1, required=False)
        args = parser.parse_args()
        main(args.image_dir, args.resize_coefficient)
    except:
        print(traceback.format_exc())
