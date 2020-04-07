# coding: utf-8
"""
Scan image for EXIF information. Run the script to have statistics for camera model, lens model and capture focal in 3 CSV format files.
(c) 2020 Tao Jiang.
Email: philip_jtao@hotmail.com
Web: https://jiangtao.art
"""

import argparse
import json
import hashlib
import os
import logging
import sys
import copy
import time
import pprint
from hashlib import md5
from PIL import Image
import PIL.ExifTags
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("scan_image")

# Global variables
myModel = dict()    # Contains my camera model list
myLensModel = dict()    # Contains my lens model list
myFocal = dict()    # Contains focal list

#--------------------------------------------------------

class exif_collector:
    
    def __init__(self, file_path):
        self.file_path = file_path
    
    def get_hashcode(self):
        if os.path.isfile(self.file_path):
            f = open(self.file_path,'rb')
            sha256_obj = hashlib.sha256()
            sha256_obj.update(f.read())
            hash_code = sha256_obj.hexdigest()
            f.close()
        else:
            hash_code = None
            log.error(self.file_path + " cannot open for hashcode.")
        return hash_code

    def get_exif(self):
        try:
            image = Image.open(self.file_path)
            log.debug(self.file_path + " opened for exif info.")
            exif = {
                PIL.ExifTags.TAGS[k]: v
                for k, v in image._getexif().items()
                if k in PIL.ExifTags.TAGS
            }
        except Exception as e:
            exif = None
            log.error(self.file_path + " cannot open for exif info.")
            log.debug("Error retrieving exif info: {}".format(e))
        finally:
            log.debug("Get EXIF finished.")
            return exif

    def get_aspect_ratio(self):
        ratio = 0.0
        try:
            image = Image.open(self.file_path)
            log.debug(self.file_path + " opened for aspect ratio.")
        except Exception as e:
            log.error(self.file_path + " cannot open for aspect ratio.")
            log.debug("Error retrieving aspect ratio: {}".format(e))
        else:
            ratio = image.width/image.height
            log.debug("Image aspect ratio is %f.", ratio)
        finally:
            log.debug("Get aspect ratio finished.")
        return ratio

def process(file_path):
    log.info("---> File to handle: " + file_path + " <---")
    global myModel, myLensModel, myFocal
    collector = exif_collector(file_path)
    image_exif = collector.get_exif()
    if (image_exif != None):
        if ('Model' in image_exif.keys()):
            if (len(image_exif['Model']) > 0):
                myModel[image_exif['Model']] = myModel.get(image_exif['Model'], 0) + 1
        if ('LensModel' in image_exif.keys()):
            if (len(image_exif['LensModel']) > 0):
                myLensModel[image_exif['LensModel']] = myLensModel.get(image_exif['LensModel'], 0) + 1
        if ('FocalLengthIn35mmFilm' in image_exif.keys()):
            if (image_exif['FocalLengthIn35mmFilm'] > 0):
                myFocal[image_exif['FocalLengthIn35mmFilm']] = myFocal.get(image_exif['FocalLengthIn35mmFilm'], 0) + 1
    pass

def main():
    log.info(">>>>>>>>>>>>>>>>>>>>  Task Started  >>>>>>>>>>>>>>>>>>>>")
    global myModel, myLensModel, myFocal
    AMOUNT = 0

    if (len(sys.argv) != 2):
        print("Please give a file path name.\n")
    else:
        if os.path.isdir(sys.argv[1]):
            # Traversal the folder.
            g = os.walk(sys.argv[1])
            for path, dir_list, file_list in g:
                for file_name in file_list:
                    process(os.path.join(path, file_name))
                    AMOUNT += 1
        else:
            process(sys.argv[1])
            AMOUNT = 1

    print(myModel)
    dataframe = pd.DataFrame(myModel.items(), columns=['Camera Model', 'Amount'])
    dataframe.to_csv("myModel.csv", index=False, sep=',')

    print(myLensModel)
    dataframe = pd.DataFrame(myLensModel.items(), columns=['Lens Model', 'Amount'])
    dataframe.to_csv("myLensModel.csv", index=False, sep=',')

    print(myFocal)
    dataframe = pd.DataFrame(myFocal.items(), columns=['Focal', 'Value'])
    dataframe.to_csv("myFocal.csv", index=False, sep=',')

    log.info("<<<<<<<<<<<<<<<<<<<<  Task completed (%d files processed)  <<<<<<<<<<<<<<<<<<<<", AMOUNT)

if __name__ == "__main__":
    main()
