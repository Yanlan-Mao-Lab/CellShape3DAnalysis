#!/usr/bin/python

import os, sys
from skimage import io
from PIL.TiffTags import TAGS
from PIL import Image
import tifffile as tiff
import numpy as np

def obtainVoxelDepth(inputDir):
	voxelDepth = np.zeros((len(os.listdir(inputDir)), 3));
	numFile = 0;
	for rawFileName in os.listdir(inputDir):
		# Obtain raw image parameters: zSpacing, xResolution and yResolution
		rawImg = tiff.TiffFile(inputDir + '/' + rawFileName);
		try:
			zSpacing = rawImg.imagej_metadata['spacing'];
		except Exception as e:
			zSpacing = 1;

		if rawImg.imagej_metadata['unit'] == 'micron':
			measurementsInMicrons = True;

		rawImg = Image.open(inputDir + '/' + rawFileName)

		if TAGS[282] == 'XResolution':
			xResolution = 1/float(rawImg.tag_v2[282]);

		if TAGS[283] == 'YResolution':
			yResolution = 1/float(rawImg.tag_v2[283]);

		if measurementsInMicrons:
			#To nanometers
			zSpacing=zSpacing*1000;
			xResolution=xResolution*1000;
			yResolution=yResolution*1000;

		voxelDepth[numFile, 0] = xResolution;
		voxelDepth[numFile, 1] = yResolution;
		voxelDepth[numFile, 2] = zSpacing;
		numFile = numFile + 1;

	return voxelDepth;

toProcessDir = sys.argv[1];

voxelDepths = obtainVoxelDepth(toProcessDir);
imposedValues = [np.max(voxelDepths[:, 0]), np.max(voxelDepths[:, 1]), np.min(voxelDepths[:, 2])];
print(voxelDepths / imposedValues)

for rawFileName in os.listdir(toProcessDir):
	h5Filename = toProcessDir.replace('ToProcess', 'HDF5') + '/ToNormalize/' + rawFileName.replace('.tiff', '_predictions_best.h5');

	with h5py.File(newHDF5Img, 'r+') as hf:
		

