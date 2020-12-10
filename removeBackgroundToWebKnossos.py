#!/usr/bin/python

import os, sys

from skimage import io
from PIL.TiffTags import TAGS
from PIL import Image
import tifffile as tiff
import numpy as np

# Obtain raw image parameters: zSpacing, xResolution and yResolution
rawImg = tiff.TiffFile(sys.argv[1]);
try:
	zSpacing = rawImg.imagej_metadata['spacing'];
except Exception as e:
	zSpacing = 1;

if rawImg.imagej_metadata['unit'] == 'micron':
	measurementsInMicrons = True;

rawImg = Image.open(sys.argv[1])

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
rawImg = io.imread(sys.argv[1]);

segmentedImg = io.imread(sys.argv[2]);
segmentedImg = segmentedImg - 1;

uniqueIds=np.unique(segmentedImg)
maxId = uniqueIds.max()


os.mkdir('Tmp')
if len(segmentedImg.shape) == 3:
	timePointsTotal = 1;
	os.mkdir('Tmp/source1')
	os.mkdir('Tmp/source1/color')
	os.mkdir('Tmp/source1/segmentation')
	#Segmented image is saved at Tmp/source/segmentation
	for currentFrame in range(0,segmentedImg.shape[0]):
		io.imsave("Tmp/source1/segmentation/segmented"+ str(currentFrame) +".tif", segmentedImg[currentFrame, :, :])

	#Raw images is saved at Tmp/source/color
	for currentFrame in range(0,rawImg.shape[0]):
		io.imsave("Tmp/source1/color/raw"+ str(currentFrame) +".tif", rawImg[currentFrame, :, :])
elif len(segmentedImg.shape) == 4:
	timePointsTotal = segmentedImg.shape[0];
	for currentTimeFrame in range(0, rawImg.shape[0]):
		os.mkdir('Tmp/source'+ str(currentTimeFrame+1))
		os.mkdir('Tmp/source'+ str(currentTimeFrame+1) +'/color')
		os.mkdir('Tmp/source'+ str(currentTimeFrame+1) +'/segmentation')
		#Segmented image is saved at Tmp/source/segmentation
		for currentZFrame in range(0, segmentedImg.shape[1]):
			io.imsave("Tmp/source"+ str(currentTimeFrame+1) +"/segmentation/segmented"+ str(currentZFrame) +".tif", segmentedImg[currentTimeFrame, currentZFrame, :, :])

		#Raw images is saved at Tmp/source/color
		for currentZFrame in range(0, rawImg.shape[1]):
			io.imsave("Tmp/source"+ str(currentTimeFrame+1) +"/color/raw"+ str(currentZFrame) +".tif", rawImg[currentTimeFrame, currentZFrame, :, :])


print(float(xResolution), float(yResolution), float(zSpacing), maxId, timePointsTotal)