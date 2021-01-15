#!/usr/bin/python

import os, sys

from skimage import io, measure
from PIL.TiffTags import TAGS
from PIL import Image
import tifffile as tiff
import numpy as np
import napari
import matplotlib.pyplot as plt

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

#Measures properties of labelled regions
props = measure.regionprops(segmentedImg)

#Array of Id and area (same as volume?)
a = np.zeros((maxId,2))

for i in range(maxId):
    a[i,1] = props[i].area
    a[i,0] = i

#Threshold segments
areaMean = np.mean(a)
areaStd = np.std(a)
smallThreshold = 10000
bigThreshold = 600000

aThreshold = np.empty((0,2), int)
IdsToRemove = np.empty((0,2),int)

for i in range(maxId):
    if a[i,1] > smallThreshold and a[i,1] < bigThreshold:
        aThreshold = np.append(aThreshold, np.array([a[i,:]]), axis=0)
    else:
        IdsToRemove = np.append(IdsToRemove, np.array([a[i,:]]), axis=0)
        
#Plot histogram of thresholded areas
plt.hist(aThreshold[:,1], bins=30)
plt.show()

#Keep only thresholded Ids in post processed image
postProcessImg=segmentedImg.copy()

for Id in range(maxId):
    print(Id)
    if Id in IdsToRemove[:,0]:
        postProcessImg[postProcessImg==Id]=0

#Replaces ID with 0 if ID is in a fewer number of slices than threshold
#VERY slow!!! >> hrs

#for Id in range(maxId):
#    print(Id)
#    count = len(np.unique(np.where(segmentedImg==Id)[0]))
#    if count < threshold:
#        postProcessImg[postProcessImg==Id]=0
        
#Visualise raw, segmented and postprocessed image using napari
#Napari viewer with raw and segment images as layers
with napari.gui_qt():
    viewer = napari.view_image(rawImg, rgb=False, colormap='green', blending='additive')
    viewer.add_image(segmentedImg, rgb=False, colormap='magenta', blending='additive')
    viewer.add_image(postProcessImg, rgb=False)

#Separate window with post processed image?
#with napari.gui_qt():
#    viewer = napari.view_image(postProcessImg, rgb=False)
