#!/usr/bin/python
from skimage import io
import os, sys
import pyclesperanto_prototype as cle
import napari
from skimage.io import imsave
import numpy as np
import tifffile as tiff

# initialize GPU
device = cle.select_device("GTX")
print("Used GPU: ", device)

zRangeToCrop = [[11, 16], [12, 16], [12, 17], [12, 18], [13, 18], [13, 21], [13, 22], [13, 24], [13, 24], [14, 26]]

inputFile = '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/Original/Robs data/sqhAX3_SqhGFP-EcadTom/280618/Disc2/Part2_decon.tif';
inputFile_corrected = '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/Original/Robs data/sqhAX3_SqhGFP-EcadTom/280618/Disc2/Part2_decon_EnhancedContrast_ChannelTogether_Blurred.tif';

projectedImg_channel1 = None
projectedImg_channel2 = None
projectedImg_corrected = None

# Shape (frames, Zs, channels, x, y)
rawImg = io.imread(inputFile)

# Enhance contrast of raw image

# Gaussian blur in z axis (2, 2, 1)

correctedImg = io.imread(inputFile_corrected)

projectedImg = np.zeros_like(rawImg[:, 0, :, :, :])
projectedImg_ToSegment = np.zeros_like(rawImg[:, 0, 0, :, :])

# Crop range of Zs for each channel and the corrected
# Maximum z projection of each timepoint
for numFrame in range(0, len(zRangeToCrop)):
	#1st channel
	rawImg_gpu = cle.push(rawImg[numFrame, (zRangeToCrop[numFrame][0]-1):(zRangeToCrop[numFrame][1]-1), 0, :, :])
	projectedImg_channel1 = cle.maximum_z_projection(rawImg_gpu, projectedImg_channel1)

	#2nd channel
	rawImg_gpu = cle.push(rawImg[numFrame, (zRangeToCrop[numFrame][0]-1):(zRangeToCrop[numFrame][1]-1), 1, :, :])
	projectedImg_channel2 = cle.maximum_z_projection(rawImg_gpu, projectedImg_channel2)
	
	# Blurred image to segment
	correctedImg_gpu = correctedImg[numFrame, (zRangeToCrop[numFrame][0]-1):(zRangeToCrop[numFrame][1]-1), :, :]
	projectedImg_corrected = cle.maximum_z_projection(correctedImg_gpu, projectedImg_corrected)

	projectedImg[numFrame, 0, :, :] = cle.pull(projectedImg_channel1);
	projectedImg[numFrame, 1, :, :] = cle.pull(projectedImg_channel2);
	projectedImg_ToSegment[numFrame, :, :] = cle.pull(projectedImg_corrected);


tiff.imsave('projectedImg.tif', projectedImg, imagej=True, metadata={'axes': 'TCYX'})
tiff.imsave('projectedImg_ToSegment.tif', projectedImg_ToSegment, imagej=True, metadata={'axes': 'TYX'})