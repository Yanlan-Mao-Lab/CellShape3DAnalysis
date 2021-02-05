#!/usr/bin/python

import h5py
import os, sys
from os import path
from skimage import io
import numpy as np

def findDir(name, inputDir):
    for root, dirs, files in os.walk(inputDir):
        if name in files:
            return path.join(root, name)

def readImageSequence(directory):
    numZ = 0;
    allFiles = os.listdir(directory);
    initFile = io.imread(directory + '/' + allFiles[0]);
    stack = np.zeros((len(allFiles), initFile.shape[0], initFile.shape[1]), dtype=np.uint16)
    for file in allFiles:
        stack[numZ, :, :] = io.imread(directory + '/' + file);
        numZ=numZ+1;

    print (numZ)
    return stack

#First we create all the datasets with the tif files from plantseg
# Then modify these ones with the refines ones from webknossos

# important directories:
# - Datasets/PretrainedModel/*.h5 - Raw images preprocessed by plantseg (some may have different pixel depth)
# - 2_Segmentation/2_Proofreading/3_RefinedTiff - Improved segmentation from webknossos
# - Datasets/PretrainedModel_best - Segmentation directly from plantseg

inputDir = sys.argv[1];
#inputDir = '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/PretrainedModel/RobTetley/'

outputDir = inputDir.replace('PreTrainedModel', 'HDF5')
refinedDir = inputDir.replace('Datasets/PreTrainedModel', '2_Segmentation/2_Proofreading/3_RefinedTiff')
try:
    os.makedirs(outputDir);
except Exception as e:
    print ('Dir exits')

for rawFileName in os.listdir(inputDir):
    #print(rawFileName)
    if rawFileName.endswith('.h5'):
        
        newHDF5Img = outputDir + '/' + rawFileName;
        #if not path.exists(newHDF5Img):
        #print (rawFileName)
        hf = h5py.File(newHDF5Img, 'w')

        rawImg = h5py.File(inputDir + '/' + rawFileName, 'r');

        #Shape DepthWidthHeight
        hf.create_dataset('raw', data=rawImg['raw'], compression="gzip", compression_opts=9)

        for refinedFile in os.listdir(refinedDir):
            if rawFileName.replace('.h5', '') in refinedFile:
                labelledImg = readImageSequence(refinedDir+'/'+refinedFile)
        else:
            segmentedImgDir = findDir(rawFileName.replace('.h5', '_predictions_best.tiff'), inputDir.replace('PreTrainedModel', 'PreTrainedModel_best'))
            labelledImg = io.imread(segmentedImgDir);

        hf.create_dataset('label', data=labelledImg, compression="gzip", compression_opts=9);

        hf.close()
        