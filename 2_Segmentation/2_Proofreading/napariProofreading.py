import os, sys
import h5py
import tifffile as tiff
from PIL.TiffTags import TAGS
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, measure, morphology, segmentation, transform, filters, color
from PIL import Image
import napari


def load_raw_seg_images(rawFilePath, segFilePath, resize_img=True):
    '''Read segmented image to remove first biggest label and obtain list of cell properties'''
    
    if rawFilePath.endswith('tif') or rawFilePath.endswith('tiff'):
        rawImg = io.imread(rawFilePath)
        segmentedImg = io.imread(segFilePath)
    
    if rawFilePath.endswith('h5'):
        rawImgh5 = h5py.File(rawFilePath, 'r')
        rawImg = np.array(rawImgh5.get('raw'))

        segmentedImgh5 = h5py.File(segFilePath, 'r')
        segmentedImg = np.array(segmentedImgh5.get('segmentation'))
        
    #segmentedImg = segmentedImg - 1;
    
    if resize_img == True:
            rawImg = transform.resize(rawImg, (rawImg.shape[0], 512, 512),
                            order=0, preserve_range=True, anti_aliasing=False).astype(np.uint32)
            segmentedImg = transform.resize(segmentedImg, (segmentedImg.shape[0], 512, 512),
                                  order=0, preserve_range=True, anti_aliasing=False).astype(np.uint32)  
    #uniqueIds=np.unique(segmentedImg)
    #maxId = uniqueIds.max()
     
    props = measure.regionprops(segmentedImg)

    return rawImg, segmentedImg, props

rawFilePath = sys.argv[1]
segmentedFilePath = sys.argv[2]

rawImg, segmentedImg, props = load_raw_seg_images(rawFilePath, segmentedFilePath, False)

#3D
viewer = napari.Viewer()  # no prior setup needed
viewer.add_image(rawImg, rgb=False, colormap='green', blending='additive')
viewer.add_labels(segmentedImg, name='segmentation')
napari.run()

postProcessFilePath = segmentedFilePath.rstrip('.tif');
postProcessFilePath += '_postprocessed.tif'
io.imsave(postProcessFilePath, segmentedImg)