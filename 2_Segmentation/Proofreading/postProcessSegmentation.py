#!/usr/bin/python

import os, sys

from skimage import io
from PIL.TiffTags import TAGS
from PIL import Image
import tifffile as tiff
import numpy as np
import napari

rawFilePath = '201105_NubG4-UASmyrGFP_COVERSLIP-FLAT_DISH-1-DISC-1_STACK.tif'
segFilePath = '201105_NubG4-UASmyrGFP_COVERSLIP-FLAT_DISH-1-DISC-1_STACK_predictions_gasp_average.tiff'

# Obtain raw image parameters: zSpacing, xResolution and yResolution
rawImg = tiff.TiffFile(rawFilePath);
try:
	zSpacing = rawImg.imagej_metadata['spacing'];
except Exception as e:
	zSpacing = 1;

if rawImg.imagej_metadata['unit'] == 'micron':
	measurementsInMicrons = True;

rawImg = Image.open(rawFilePath)

if TAGS[282] == 'XResolution':
	xResolution = 1/rawImg.tag_v2[282];

if TAGS[283] == 'YResolution':
	yResolution = 1/rawImg.tag_v2[283];

if measurementsInMicrons:
	#To nanometers
	zSpacing=zSpacing*1000;
	xResolution=xResolution*1000;
	yResolution=yResolution*1000;

# Read segmented image to remove first biggest label
rawImg = io.imread(rawFilePath);

segmentedImg = io.imread(segFilePath);
segmentedImg = segmentedImg - 1;

uniqueIds=np.unique(segmentedImg)
maxId = uniqueIds.max()

#Visualise raw, segmented and postprocessed image using napari
#Napari viewer with raw and segment images as layers
with napari.gui_qt():
    viewer = napari.view_image(rawImg, rgb=False, colormap='green', blending='additive')
    viewer.add_image(segmentedImg, rgb=False, colormap='magenta', blending='additive')
#    viewer.add_image(postProcessImg, rgb=False)

#Separate window with post processed image?
#with napari.gui_qt():
#    viewer = napari.view_image(postProcessImg, rgb=False)
