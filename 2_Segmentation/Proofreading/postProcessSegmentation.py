#!/usr/bin/python

import os, sys

from skimage import io, measure, segmentation
from skimage.transform import resize
from PIL.TiffTags import TAGS
from PIL import Image
import tifffile as tiff
import numpy as np
import napari
import matplotlib.pyplot as plt

# Obtain raw image parameters: zSpacing, xResolution and yResolution
def raw_parameters(rawFilePath):
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
        
    return zSpacing, xResolution, yResolution

def load_raw_seg_images(rawFilePath, segFilePath, resize_img=True):
    # Read segmented image to remove first biggest label
    rawImg = io.imread(rawFilePath);

    segmentedImg = io.imread(segFilePath);
    segmentedImg = segmentedImg - 1;
    
    if resize_img == True:
            rawImg = resize(rawImg, (rawImg.shape[0], 512, 512),
                            order=0, preserve_range=True, anti_aliasing=False).astype(np.uint32)
            segmentedImg = resize(segmentedImg, (segmentedImg.shape[0], 512, 512),
                                  order=0, preserve_range=True, anti_aliasing=False).astype(np.uint32)  
    #uniqueIds=np.unique(segmentedImg)
    #maxId = uniqueIds.max()
     
    props = measure.regionprops(segmentedImg)

    return rawImg, segmentedImg, props

def area_array(props):
    
    a = np.zeros((len(props),2))
    
    for i in range(len(props)):
        a[i,1] = props[i].area
        a[i,0] = props[i].label
        
    return a.astype(np.uint16)

def calculate_cell_heights(props):
    
    cell_heights = np.zeros((len(props),2))
    
    for i in range(len(props)):
        cell_heights[i,0] = props[i].label
        cell_heights[i,1] = props[i].bbox[3]-props[i].bbox[0]
        
    return cell_heights

#def calculate_thresholds(cell_heights, percentage):
    
    

def remove_background(segmentedImg, props, hist=True, nbins=30):
    
    backgroundIds = np.zeros((0,1))

    for i in range(len(props)):
        if (props[i].bbox[4] == 512) and (props[i].bbox[5] == 512):
            backgroundIds= np.append(backgroundIds, props[i].label)
    
    for i in range(len(backgroundIds)):
        Id = backgroundIds[i]
        segmentedImg[segmentedImg==Id] = 0
    
    new_props = measure.regionprops(segmentedImg)
    
    new_a = area_array(new_props)
        
    #Plot histogram
    if hist == True:
        plt.hist(new_a[:,1], bins=nbins)
        plt.xlabel('Segment area')
        plt.ylabel('Frequency density')
        plt.show()
        
    segmentedImg = segmentedImg + 1
        
    return segmentedImg, new_props

#Threshold segments to remove too small/big segments and background
def threshold_segments(segmentedImg, props, smallThreshold, bigThreshold, hist=False, nbins=30):
    
    #Measures properties of labelled regions
    #Labels with 0 ignored so indices are n-2 from rawImg or n-1 from segmentedImg
    
    #Array of Id and area
    a = area_array(props)
   
    aThreshold = np.empty((0,2))
    IdsToRemove = np.empty((0,1))
    
    for i in range(len(props)):
        if a[i,1] > smallThreshold and a[i,1] < bigThreshold:
            aThreshold = np.append(aThreshold, np.array([a[i,:]]), axis=0)
        else:
            IdsToRemove = np.append(IdsToRemove, i)
            
    thresholdImg=rem_background_segmentedImg.copy()
    
    for i in range(len(IdsToRemove)):
        Id = int(IdsToRemove[i])
        thresholdImg[new_props[Id].coords[:,0],new_props[Id].coords[:,1],new_props[Id].coords[:,2]] = 0
    
    #Plot histogram
    if hist == True:
        plt.hist(aThreshold[:,1], bins=nbins)
        plt.xlabel('Segment area')
        plt.ylabel('Frequency density')
        plt.show()
    
    return thresholdImg

#Plot histogram of total number of z slices per id
def z_slice_hist(Img,nbins=30):
    props = measure.regionprops(Img)
    zHeights = np.zeros(len(props))
    
    for i in range(len(props)):
        zHeights[i] = props[i].bbox[3]-props[i].bbox[0]
        
    plt.hist(zHeights,bins=nbins)
    plt.xlabel('Z height (in slices)')
    plt.ylabel('Frequency density')
    plt.show()


#Use functions

rawFilePath = 'Data/Original/Rici/201105_NubG4-UASmyrGFP_COVERSLIP-FLAT_DISH-1-DISC-1_STACK.tif'
segFilePath = 'Data/Original/Rici/201105_NubG4-UASmyrGFP_COVERSLIP-FLAT_DISH-1-DISC-1_STACK_predictions_gasp_average.tiff'

rawImg, segmentedImg, props = load_raw_seg_images(rawFilePath, segFilePath)

#rawImg, segmentedImg, props = load_raw_seg_images(sys.argv[1], sys.argv[2], True)

rem_background_segmentedImg, new_props = remove_background(segmentedImg, props, False)

thresholdImg = threshold_segments(rem_background_segmentedImg, new_props, 1000, 110000, False)
#thresholdImg = thresholdImg + 1
watershedImg = segmentation.watershed(rawImg, thresholdImg, watershed_line = False)
#watershed_props = measure.regionprops(watershedImg)
watershedImg = watershedImg -1

# Saves post processed output as tif
tiff.imsave('postProcessImg.tif', watershedImg)

#https://github.com/taketwo/glasbey

#Visualise raw, segmented, thresholded and watershed image using napari
#Napari viewer with raw and segment images as layers
with napari.gui_qt():
    viewer = napari.view_image(rawImg, rgb=False, colormap='green', blending='additive')
    viewer.add_image(segmentedImg, rgb=False, colormap='magenta', blending='additive')
    viewer.add_image(thresholdImg, rgb=False, blending='additive')
    viewer.add_image(watershedImg, rgb=False, blending='additive')
    

