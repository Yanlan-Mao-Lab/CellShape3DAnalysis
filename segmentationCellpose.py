
import numpy as np
import matplotlib.pyplot as plt
import skimage.io
import os, sys
from cellpose import models, io
import inspect
import napari

##Check API: https://cellpose.readthedocs.io/en/latest/api.html

# model_type='cyto' or model_type='nuclei'
model = models.Cellpose(model_type='cyto', gpu=True)

# list of files
inputDir = '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/cellpose/3d/'

segmentation3D = False
# define CHANNELS to run segementation on
# grayscale=0, R=1, G=2, B=3
# channels = [cytoplasm, nucleus]
# if NUCLEUS channel does not exist, set the second channel to 0
channel = [0,0]
# IF ALL YOUR IMAGES ARE THE SAME TYPE, you can give a list with 2 elements
# channels = [0,0] # IF YOU HAVE GRAYSCALE
# channels = [2,3] # IF YOU HAVE G=cytoplasm and B=nucleus
# channels = [2,1] # IF YOU HAVE G=cytoplasm and R=nucleus

# if diameter is set to None, the size of the cells is estimated on a per image basis
# you can set the average cell `diameter` in pixels yourself (recommended)
# diameter can be a list or a single number for all images

for filename in os.listdir(inputDir):
	if filename.endswith('.tif'):
		img = io.imread(inputDir + filename)
		if segmentation3D:
			masks, flows, styles, diams = model.eval(img, diameter=30, channels=channel, anisotropy=10, do_3D=True, cellprob_threshold=-6.)
	    	# save results so you can load in gui
			io.masks_flows_to_seg(img, masks, flows, diams, inputDir + filename, channel)

		    # save results as png
			io.save_to_tif(img, masks, flows, inputDir + filename)
		else: #Treat 3D as image sequence

			for numZ in range(0, len(img)):
				#print(inspect.signature(model.eval)) - to get the real parameters
				masks, flows, styles, diams = model.eval(img[numZ, :, :], diameter=30, channels=channel, augment=True, resample=True, flow_threshold=0.0, cellprob_threshold=-6.)
				if not os.path.exists(inputDir + filename.replace('.tif', '')):
					os.makedirs(inputDir + filename.replace('.tif', ''))

				# viewer = napari.Viewer()  # no prior setup needed
				# viewer.add_image(img[numZ, :, :], rgb=False, colormap='green', blending='additive')
				# viewer.add_labels(masks, name='masks')
				# napari.run()
				# save results so you can load in gui
				io.masks_flows_to_seg(img[numZ, :, :], masks, flows, diams, inputDir + filename.replace('.tif', '') + '/' + str(numZ), channel)

				# save results as png
				io.save_to_png(img[numZ, :, :], masks, flows, inputDir + filename.replace('.tif', '') + '/' + str(numZ))
	    	


