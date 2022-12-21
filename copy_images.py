import argparse
import traceback
from pathlib import Path
from files_helper import copy_files

def main(image_dir, export_dir):
    copy_files(image_dir, export_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    try:
        parser.add_argument('--image_dir', type=Path, required=True)
        parser.add_argument('--export_dir', type=Path, default=Path("datasets"), required=False)
        args = parser.parse_args()
        main(args.image_dir, args.export_dir)
    except:
        print(traceback.format_exc())
