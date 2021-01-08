#!/usr/bin/python

import numpy as np
import h5py
import pytorch3dunet
import os, sys
from skimage import io

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


outputDir = '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/ImageAnalysis/Datasets/HDF5/'
#First we create all the datasets with the tif files from plantseg
# Then modify these ones with the refines ones from webknossos

path = sys.argv[1];
 
# call listdir() method
# path is a directory of which you want to list
directories = os.listdir( path )

for rawFileName in directories:
	print (rawFileName)
	if rawFileName.endswith('.tif'):
		
		hf = h5py.File(outputDir + rawFileName.replace('.tif', '') +'.h5', 'w')

		rawImg = io.imread(path + rawFileName);

		#Shape DepthWidthHeight
		hf.create_dataset('raw', data=rawImg, compression="gzip", compression_opts=9)

		segmentedImgDir = find(rawFileName.replace('.tif', '_predictions_gasp_average.tiff'), path)

		labelledImg = io.imread(segmentedImgDir);
		hf.create_dataset('label', data=labelledImg, compression="gzip", compression_opts=9);

		hf.close()


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

