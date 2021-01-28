#!/usr/bin/python

import os, sys

from skimage import io, measure
import csv
import numpy
from skimage.transform import resize
from skimage.util import img_as_uint

#Example: python segmentationGoodnes.py /media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/PreTrainedModel

# opening the csv file in 'w+' mode 
file = open(sys.argv[1] + '/datasetFeatures.csv', 'w+') 

sizeRefactor = 4;

# writing the data into the file 
with file:
	write = csv.writer(file)

	# writing the fields  
	write.writerow(['Name', 'TotalCells', 'AvgVolume', 'StdVolume', 'AvgSolidity', 'pctConvexCells', 'AvgCellHeight'])

	for root, subdirs, files in os.walk(sys.argv[1]):
		for rawFileName in files:
			if rawFileName.endswith(".tiff") and "_predictions_" in rawFileName:
				print(rawFileName)
				segmentedImg = io.imread(root + '/' + rawFileName);
				segmentedImg = resize(segmentedImg, (segmentedImg.shape[0] // sizeRefactor, segmentedImg.shape[1] // sizeRefactor, segmentedImg.shape[2] // sizeRefactor), order=0, preserve_range=True, anti_aliasing=False);

				# https://scikit-image.org/docs/dev/api/skimage.measure.html#skimage.measure.regionprops
				props = measure.regionprops(segmentedImg.astype('uint16'))

				#Volume
				volumeList = [cell.area for cell in props];
				meanVolume = numpy.mean(volumeList);
				stdVolume = numpy.std(volumeList);

				#Total cells
				numberOfCells = len(volumeList);

				# Cell occupying convex volume
				try:
					solidityVolume = [cell.solidity for cell in props];
					meanSolidity = numpy.mean(solidityVolume);
					pctConvexCells = sum(cell > 0.8 for cell in solidityVolume)/len(solidityVolume);
				except:
					meanSolidity = -1;
					pctConvexCells = -1;

				#Approximate cell height
				cellHeight = [cell.major_axis_length for cell in props];
				meanCellHeight = numpy.mean(cellHeight);


				write.writerow([root + '/' + rawFileName, numberOfCells, meanVolume, stdVolume, \
					meanSolidity, pctConvexCells, meanCellHeight]) 





