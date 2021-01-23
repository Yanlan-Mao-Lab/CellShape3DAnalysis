#!/usr/bin/python

import os, sys

from skimage import io, measure, segmentation
from PIL.TiffTags import TAGS
from PIL import Image
import tifffile as tiff
import numpy as np

rawFilePath = '201105_NubG4-UASmyrGFP_COVERSLIP-FLAT_DISH-1-DISC-1_STACK.tif'
segFilePath = '201105_NubG4-UASmyrGFP_COVERSLIP-FLAT_DISH-1-DISC-1_STACK_predictions_gasp_average.tiff'
postFilePath = '201105_NubG4-UASmyrGFP_COVERSLIP-FLAT_DISH-1-DISC-1_STACK_postprocess.tif'


# Read segmented image to remove first biggest label
rawImg = io.imread(rawFilePath);
postProcessImg = io.imread(postFilePath);
#new = segmentation.watershed(rawImg,postProcessImg)

