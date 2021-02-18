#!/usr/bin/python

import h5py
import os, sys
from os import path
from skimage import io
import numpy as np
import re

def findDir(name, inputDir):
    for root, dirs, files in os.walk(inputDir):
        if name in files:
            return path.join(root, name)

def readImageSequence(directory):
    numZ = 0;
    allFiles = os.listdir(directory);
    allFiles = sorted(allFiles, key=lambda x: (int(re.sub('\D','',x)),x))
    initFile = io.imread(directory + '/' + allFiles[0]);
    stack = np.zeros((len(allFiles), initFile.shape[0], initFile.shape[1]), dtype=np.uint16)
    for file in allFiles:
        stack[numZ, :, :] = io.imread(directory + '/' + file);
        numZ=numZ+1;
    return stack


#First we create all the datasets with the tif files from plantseg
# Then modify these ones with the refines ones from webknossos

# important directories:
# - Datasets/PretrainedModel/*.h5 - Raw images preprocessed by plantseg (some may have different pixel depth)
# - 2_Segmentation/2_Proofreading/3_RefinedTiff - Improved segmentation from webknossos
# - Datasets/PretrainedModel_best - Segmentation directly from plantseg

inputDir = sys.argv[1];
#inputDir = '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/PretrainedModel/RobTetley/'

refinedDir = inputDir.replace('Datasets/HDF5', '2_Segmentation/2_Proofreading/3_RefinedTiff')
try:
    os.makedirs(outputDir);
except Exception as e:
    print ('Dir exits')

for rawFileName in os.listdir(inputDir):
    #print(rawFileName)
    if rawFileName.endswith('.h5'):
        
        newHDF5Img = inputDir + '/' + rawFileName;

        with h5py.File(newHDF5Img, 'r+') as hf:
            # Refine dataset if the files exist
            for refinedFile in os.listdir(refinedDir):
                if rawFileName.replace('_predictions_best.h5', '') in refinedFile:
                    labelledImg = readImageSequence(refinedDir+'/'+refinedFile)
                    
                    segmentation = hf['segmentation'];
                    segmentationNP = segmentation[()];
                    segmentationNP[labelledImg>0] = labelledImg[labelledImg>0];

                    hf.clear()
                    hf.create_dataset('label', data=segmentationNP, compression="gzip", compression_opts=9)
                    
            with h5py.File(inputDir.replace('HDF5', 'PreTrainedModel') + '/' + rawFileName.replace('_predictions_best', '')) as rawHf:
                hf.create_dataset('raw', data=rawHf['raw'], compression="gzip", compression_opts=9)