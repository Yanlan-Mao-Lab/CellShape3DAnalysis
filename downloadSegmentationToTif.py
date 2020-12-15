
from tempfile import mkdtemp
import zipfile
import wkw
import numpy as np
import os, sys
from skimage import io
from os import path, makedirs

#Input:
# 1: Name of the annotated zip file
# 2: Directory of images
# 
# Example: 'Downloaded/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270__explorational__pvicente_munuera__c80702.zip' '../TestImages/'


#Look for original image
annotatedImg = sys.argv[1]

annotatedImgFileName = os.path.basename(annotatedImg);

annotatedImgSplitted = annotatedImgFileName.split('_maxCell_');

rawImageFileName = annotatedImgSplitted[0] + '.tif';

rawImgDir = find(rawImageFileName, sys.argv[2])

rawImg = io.imread(rawImgDir);

#Get its shape
shapeRawImg = rawImg.shape;

#Read zip annotation from WebKnossos
datasetAnnotated = read_volume_annotation(annotatedImg, np.array([0, 0, 0]), shapeRawImg)



def read_volume_annotation(filename, offset, shape):
    tmp_dir = mkdtemp()

    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(tmp_dir)

    with zipfile.ZipFile(path.join(tmp_dir, "data.zip"), "r") as zip_ref:
        zip_ref.extractall(path.join(tmp_dir, "segmentation"))

    ds = wkw.Dataset.open(path.join(tmp_dir, "segmentation", "1"))
    return ds.read(offset, shape)[0]


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

