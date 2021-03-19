#!/usr/bin/python

import os, sys
import h5py
import tifffile as tiff
from PIL.TiffTags import TAGS
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, measure, morphology, segmentation
from skimage.transform import resize
from PIL import Image
from scipy.spatial import Delaunay
import napari


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

    h5File = h5py.File(segFilePath, 'r')
    segmentedImg = np.array(h5File.get('segmentation'))
    #segmentedImg = io.imread(segFilePath)
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

def threshold_segments(segmentedImg, props, lower_percentile, higher_percentile, hist=False, nbins=30):
    
    cell_heights = calculate_cell_heights(props)
        
    smallThreshold = np.percentile(cell_heights[:,1], lower_percentile)
    bigThreshold = np.percentile(cell_heights[:,1], higher_percentile)
    
    #skimage.morphology.remove_small_objects()
    
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
    
    #Plot histogram
    if hist == True:
        plt.hist(IdsThresholded[:,1], bins=nbins)
        plt.xlabel('Segment area')
        plt.ylabel('Frequency density')
        plt.show()
    
    return thresholdImg
    

#Threshold segments to remove too small/big segments and background
def manual_threshold_segments(segmentedImg, smallThreshold, hist=False, nbins=30):

    thresholdImg = morphology.remove_small_objects(segmentedImg, smallThreshold)
    
    #Plot histogram
    if hist == True:
        plt.hist(aThreshold[:,1], bins=nbins)
        plt.xlabel('Segment area')
        plt.ylabel('Frequency density')
        plt.show()
    
    return thresholdImg

def threshold_heights(watershedImg, props, percentile):
    
    cell_heights = calculate_cell_heights(props)
        
    threshold = np.percentile(cell_heights[:,1], percentile)
        
    IdsThresholded = np.empty((0,1))
    
    for i in range(len(props)):
        if cell_heights[i,1] < threshold:
            IdsThresholded = np.append(IdsThresholded, props[i].label)
    
    return IdsThresholded.astype(np.uint16) 


def in_hull(p, hull):
    """
    Test if points in `p` are in `hull`

    `p` should be a `NxK` coordinates of `N` points in `K` dimensions
    `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of the 
    coordinates of `M` points in `K`dimensions for which Delaunay triangulation
    will be computed
    """
    if not isinstance(hull,Delaunay):
        hull = Delaunay(hull)

    return hull.find_simplex(p)>=0


def neighbours(watershedImg):
    
    cells=np.sort(np.unique(watershedImg))
    cells=cells[1:]
    neighbours=np.empty((0,2))
    
    for cel in cells:
        print(cel)
        BW = segmentation.find_boundaries(watershedImg==cel)
        BW_dilated = morphology.binary_dilation(BW)
        neighs=np.unique(watershedImg[BW_dilated==1])
        neighs=neighs[1:]
        for n in neighs:
            neighbours = np.append(neighbours, [(cel, n)], axis=0)
            
    return neighbours

#Fing neighbours for single cell
def cell_neighbours(cellID, segmentedImg):
    
    neighbours=np.empty((0,2))

    BW = segmentation.find_boundaries(segmentedImg==cellID)
    BW_dilated = morphology.binary_dilation(BW)
    neighs=np.unique(segmentedImg[BW_dilated==1])
    neighs=neighs[1:]
            
    return neighs

#Find outlines
def neighbour_outlines(cellID, segmentedImg):
    
    neighs=cell_neighbours(cellID, segmentedImg)
    
    mask = np.isin(segmentedImg,neighs)
    inmask=~mask
    neighboursImg = segmentedImg.copy()
    neighboursImg[inmask]=0
    boundariesImg = segmentation.find_boundaries(nImg)
    
    #Show in napari
    with napari.gui_qt():
        viewer = napari.view_image(rawImg, rgb=False, colormap='green', blending='additive')
        viewer.add_labels(segmentedImg, name='PlantSeg')
        viewer.add_labels(neighboursImg, name='neighbours')
        viewer.add_labels(boundariesImg, name='boundaries')
        
    return neighboursImg, boundariesImg
        
   
def hourglass(cell1ID,cell2ID,watershedImg):
    
    cell1_ZXY = np.transpose(np.nonzero(watershedImg == cell1ID))
    cell2_ZXY = np.transpose(np.nonzero(watershedImg == cell2ID))
    
    #separates all XY coordinates of cell 1 = all possible locations of cell 1 in last 3 slices
    cell1_XY_maxslices = cell1_ZXY[np.where(np.isin(cell1_ZXY[:,0],np.unique(cell1_ZXY[:,0])[-3:]))][:,1:]
    #cell1_XY_maxslices = cell1_ZXY[:,[1, 2]]   
    
    #calculate coordinates of bottom slice of cell 2
    cell2_XY_minslice = cell2_ZXY[np.where(np.isin(cell2_ZXY[:,0],np.unique(cell2_ZXY[:,0])[0]))][:,1:]
    
    #check if coordinates of bottom slice of cell 2 are within the convex hull/cluster of all cell 1 points
    #matches = np.sum(in_hull(cell2_XY_minslice, cell1_XY_maxslices))
    
    #return matches
    
    #if matches > 0.9*cell2_XY_minslice.shape[0]:
    #    watershedImg[watershedImg==cell1ID] = cell2ID
        
    if all(i in cell1_XY_maxslices for i in cell2_XY_minslice):
        watershedImg[watershedImg==cell1ID] = cell2ID
        
    return watershedImg
    

def merge_labels(watershedImg, topCellID, bottomCellID):
    
    watershedImg[watershedImg==bottomCellID] = topCellID
        
    return watershedImg    

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



def save_hdf5(segFilePath, zSpacing, xResolution, yResolution):
    
    postProcessFilePath = segFilePath.rstrip('predictions_gasp_average.h5') 
    postProcessFilePath += '_postprocessed.h5'
    postProcessFile = h5py.File(postProcessFilePath, "w")
    segmentation = postProcessFile.create_dataset("segmentation", data=watershedImg, dtype='uint16')
    
    segmentation.attrs['zSpacing'] = zSpacing
    segmentation.attrs['xResolution'] = [xResolution.numerator,xResolution.denominator]
    segmentation.attrs['yResolution'] = [yResolution.numerator,yResolution.denominator]
    postProcessFile.close()


#Use functions

#rawImg, segmentedImg, props = load_raw_seg_images(sys.argv[1], sys.argv[2], True)

rawFilePath = 'Data/Original/Rici/201105_NubG4-UASmyrGFP_COVERSLIP-FLAT_DISH-1-DISC-1_STACK.tif'
segFilePath = 'Data/Original/Rici/201105_NubG4-UASmyrGFP_COVERSLIP-FLAT_DISH-1-DISC-1_STACK_predictions_gasp_average.h5'

#rawFilePath = 'Data/Original/Rob/Part2_Decon_c1_t1.tif'
#segFilePath = 'Data/Original/Rob/Part2_Decon_c1_t1_predictions_best.tiff'

rawImg, segmentedImg, props = load_raw_seg_images(rawFilePath, segFilePath)
zSpacing, xResolution, yResolution = raw_parameters(rawFilePath)
rem_background_segmentedImg, new_props = remove_background(segmentedImg, props, False)

#thresholdImg = manual_threshold_segments(rem_background_segmentedImg, new_props, 1000, 110000, False)

#RICI
thresholdImg = threshold_segments(rem_background_segmentedImg, new_props, 20, 100, False)

#ROB
#thresholdImg = threshold_segments(rem_background_segmentedImg, new_props, 30, 99.999, False)

watershedImg = segmentation.watershed(rawImg, thresholdImg, watershed_line = False)

# Reassign background IDs
watershedImg = watershedImg -1
thresholdImg[thresholdImg==1] = 0

#watershedImg = merge_labels(watershedImg, 712, 649)

# Saves post processed output as h5
#img = np.nonzzero(watershedImg == cellID)

#tiff.imsave(postProcessFilePath,'.f', watershedImg)

#Visualise raw, segmented, thresholded and watershed image using napari
#Napari viewer with raw and segment images as layers
with napari.gui_qt():
    viewer = napari.view_image(rawImg, rgb=False, colormap='green', blending='additive')
    #viewer.add_image(segmentedImg, rgb=False, colormap='magenta', blending='additive')
    viewer.add_labels(segmentedImg, name='PlantSeg')
    #viewer.add_image(thresholdImg, rgb=False, blending='additive')
    viewer.add_labels(thresholdImg, name='thresholded')
    #viewer.add_image(watershedImg, rgb=False, blending='additive')
    viewer.add_labels(watershedImg, name='watershed')
    

