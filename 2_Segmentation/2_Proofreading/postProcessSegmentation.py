#!/usr/bin/python

import os, sys
import h5py
import tifffile as tiff
from PIL.TiffTags import TAGS
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, measure, morphology, segmentation, transform
from PIL import Image
import napari


def raw_parameters(rawFilePath):
    '''Obtain raw image parameters: zSpacing, xResolution and yResolution from TIFF'''
    
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
    '''Read segmented image to remove first biggest label and obtain list of cell properties'''
    
    #If TIFF
    #rawImg = io.imread(rawFilePath);
    #segmentedImg = io.imread(segFilePath)
    
    #If HDF5
    rawImgh5 = h5py.File(rawFilePath, 'r')
    rawImg = np.array(rawImgh5.get('raw'))

    segmentedImgh5 = h5py.File(segFilePath, 'r')
    segmentedImg = np.array(segmentedImgh5.get('segmentation'))
    
    segmentedImg = segmentedImg - 1;
    
    if resize_img == True:
            rawImg = transform.resize(rawImg, (rawImg.shape[0], 512, 512),
                            order=0, preserve_range=True, anti_aliasing=False).astype(np.uint32)
            segmentedImg = transform.resize(segmentedImg, (segmentedImg.shape[0], 512, 512),
                                  order=0, preserve_range=True, anti_aliasing=False).astype(np.uint32)  
    #uniqueIds=np.unique(segmentedImg)
    #maxId = uniqueIds.max()
     
    props = measure.regionprops(segmentedImg)

    return rawImg, segmentedImg, props


def area_array(props):
    '''Obtain array of cell areas from props'''
    a = np.zeros((len(props),2))
    
    for i in range(len(props)):
        a[i,1] = props[i].area
        a[i,0] = props[i].label
        
    return a.astype(np.uint16)


def calculate_cell_heights(props, hist=False, bins=30):
    '''Obtain array of cell heights (in slices) from props'''
    
    cell_heights = np.zeros((len(props),2))
    
    for i in range(len(props)):
        cell_heights[i,0] = props[i].label
        cell_heights[i,1] = props[i].bbox[3]-props[i].bbox[0]

    #Plot histogram
    if hist == True:        
        plt.hist(cell_heights[:,1],bins=nbins)
        plt.xlabel('Z height (in slices)')
        plt.ylabel('Frequency density')
        plt.show()
        
    return cell_heights


def remove_background(segmentedImg, props):
    '''Remove background IDs'''
    
    backgroundIds = np.zeros((0,1))
    xdim = segmentedImg.shape[1]
    ydim = segmentedImg.shape[2]
    
    #Backgrouynd IDs identified if dimensions match full image
    for i in range(len(props)):
        if (props[i].bbox[4] == xdim) and (props[i].bbox[5] == ydim):
            backgroundIds= np.append(backgroundIds, props[i].label)
    
    for i in range(len(backgroundIds)):
        Id = backgroundIds[i]
        segmentedImg[segmentedImg==Id] = 0
    
    new_props = measure.regionprops(segmentedImg)
        
    segmentedImg = segmentedImg + 1
        
    return segmentedImg, new_props


def threshold_segments(segmentedImg, props, lower_percentile, higher_percentile):
    '''Remove cells outside specified min and max percentile'''
    
    cell_heights = calculate_cell_heights(props)
        
    smallThreshold = np.percentile(cell_heights[:,1], lower_percentile)
    bigThreshold = np.percentile(cell_heights[:,1], higher_percentile)
    
    IdsThresholded = np.empty((0,2))
    IdsToRemove = np.empty((0,1))
    
    for i in range(len(props)):
        if cell_heights[i,1] > smallThreshold and cell_heights[i,1] < bigThreshold:
            IdsThresholded = np.append(IdsThresholded, np.array([cell_heights[i,:]]), axis=0)
        else:
            IdsToRemove = np.append(IdsToRemove, i)
            
    thresholdImg=rem_background_segmentedImg.copy()
    
    for i in range(len(IdsToRemove)):
        Id = int(IdsToRemove[i])
        thresholdImg[new_props[Id].coords[:,0],new_props[Id].coords[:,1],new_props[Id].coords[:,2]] = 0
    
    return thresholdImg
    

def manual_threshold_segments(segmentedImg, smallThreshold):
    '''Remove cells outside specified min and max pixel area. Not recommended'''

    thresholdImg = morphology.remove_small_objects(segmentedImg, smallThreshold)
    
    #Also works with function below
    #skimage.morphology.remove_small_objects()

    return thresholdImg


def threshold_heights(watershedImg, percentile):
    '''Threshold cells based on specified height percentile'''
    
    props= measure.regionprops(watershedImg)
    
    cell_heights = calculate_cell_heights(props)
        
    threshold = np.percentile(cell_heights[:,1], percentile)
        
    IdsThresholded = np.empty((0,1))
    
    for i in range(len(props)):
        if cell_heights[i,1] < threshold:
            IdsThresholded = np.append(IdsThresholded, props[i].label)
    
    return IdsThresholded.astype(np.uint16) 


def neighbours(watershedImg, threshold_height_cells):
    '''Return array of pairs of neighbouring cells from list of thresholded cells in whole image'''
    
    #If cells aren't thresholded
    #cells=np.sort(np.unique(watershedImg))
    #cells=cells[1:]
    
    neighbours=np.empty((0,2))
    
    for cel in threshold_height_cells:
        BW = segmentation.find_boundaries(watershedImg==cel)
        BW_dilated = morphology.binary_dilation(BW)
        neighs=np.unique(watershedImg[BW_dilated==1])
        indices = np.where(neighs==0.0)
        indices = np.append(indices, np.where(neighs==cel))
        neighs = np.delete(neighs, indices)
        for n in neighs:
            neighbours = np.append(neighbours, [(cel, n)], axis=0).astype(np.uint16)
            
    return neighbours


#Find neighbours for single cell
def cell_neighbours(cellID, segmentedImg):
    '''Return array of cell pairs for specified cell'''
    
    neighbours=np.empty((0,2))

    BW = segmentation.find_boundaries(segmentedImg==cellID)
    BW_dilated = morphology.binary_dilation(BW)
    neighs=np.unique(segmentedImg[BW_dilated==1])
    neighs=neighs[1:]
            
    return neighbours
        
   
def hourglass_ind(cell1ID,cell2ID,watershedImg):
    '''Project cell1 onto 2D plane and if cell2 projection overlaps, merges cell IDs'''
    
    cell1_ZXY = np.transpose(np.nonzero(watershedImg == cell1ID))
    cell2_ZXY = np.transpose(np.nonzero(watershedImg == cell2ID))
    
    #separates all XY coordinates of cell 1 = all possible locations of cell 1 in last slice
    cell1_XY_maxslices = cell1_ZXY[np.where(np.isin(cell1_ZXY[:,0],np.unique(cell1_ZXY[:,0])[-1]))][:,1:]
    #cell1_XY_maxslices = cell1_ZXY[:,[1, 2]]   
    
    #calculate coordinates of bottom slice of cell 2
    cell2_XY_minslice = cell2_ZXY[np.where(np.isin(cell2_ZXY[:,0],np.unique(cell2_ZXY[:,0])[0]))][:,1:]
        
    if all(i in cell1_XY_maxslices for i in cell2_XY_minslice):
        watershedImg[watershedImg==cell1ID] = cell2ID
        
    return watershedImg


def hourglass(neigbours,watershedImg):
    '''Project cell1 onto 2D plane and if cell2 projection overlaps, merges cell IDs for whole image using neighbours array'''
    for row in neighbours:
        print(row)
        if (row[0] in np.unique(watershedImg)) and (row[1] in np.unique(watershedImg)):
            cell1_ZXY = np.transpose(np.nonzero(watershedImg == row[0]))
            cell2_ZXY = np.transpose(np.nonzero(watershedImg == row[1]))
            cell1_XY_maxslices = cell1_ZXY[np.where(np.isin(cell1_ZXY[:,0],np.unique(cell1_ZXY[:,0])[-1]))][:,1:]
            cell2_XY_minslice = cell2_ZXY[np.where(np.isin(cell2_ZXY[:,0],np.unique(cell2_ZXY[:,0])[0]))][:,1:]
            if all(i in cell1_XY_maxslices for i in cell2_XY_minslice):
                watershedImg[watershedImg==row[0]] = row[1]
        
    return watershedImg


def save_hdf5(segFilePath):
    '''Saves postprocessed image as HDF5'''
    
    postProcessFilePath = segFilePath.rstrip('predictions_gasp_average.h5') 
    postProcessFilePath += '_postprocessed.h5'
    postProcessFile = h5py.File(postProcessFilePath, "w")
    segmentation = postProcessFile.create_dataset("segmentation", data=watershedImg, dtype='uint16')
    
    #If properties from TIFF (need to add into function argument)
    #segmentation.attrs['zSpacing'] = zSpacing
    #segmentation.attrs['xResolution'] = [xResolution.numerator,xResolution.denominator]
    #segmentation.attrs['yResolution'] = [yResolution.numerator,yResolution.denominator]
    
    postProcessFile.close()


#Use functions

rawImg, segmentedImg, props = load_raw_seg_images(sys.argv[1], sys.argv[2], False)

rem_background_segmentedImg, new_props = remove_background(segmentedImg, props)

thresholdImg = threshold_segments(rem_background_segmentedImg, new_props, 30, 99.99)
watershedImg = segmentation.watershed(rawImg, thresholdImg)

# Reassign background IDs
watershedImg = watershedImg -1
thresholdImg[thresholdImg==1] = 0

# Saves post processed output as h5
save_hdf5(sys.argv[2])

# Save as TIFF
#tiff.imsave(postProcessFilePath,'.f', watershedImg)

#Visualise raw, segmented, thresholded and watershed image using napari
#Napari viewer with raw and segment images as layers
with napari.gui_qt():
    viewer = napari.view_image(rawImg, rgb=False, colormap='green', blending='additive')
    viewer.add_labels(segmentedImg, name='PlantSeg')
    viewer.add_labels(thresholdImg, name='thresholded')
    viewer.add_labels(watershedImg, name='watershed')
    
    
