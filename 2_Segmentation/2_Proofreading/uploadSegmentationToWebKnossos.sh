#!/bin/bash
# This script is developed to upload stack tiff files of raw and segmented to WebKnossos
# Input: rawDirName

export rawDirName=$1
export segmentedDirName=$1/PreProcessing/confocal_unet_bce_dice_ds3x/GASP/PostProcessing

for fileNameRaw in $rawDirName/*.tif
do

	echo $fileNameRaw

	export fileNameRawOnly="$(basename "${fileNameRaw}")"
	export fileNameSeg="$segmentedDirName/${fileNameRawOnly%.tif}_predictions_gasp_average.tiff"
	echo $fileNameSeg
	#First step: Remove background cell with a python/julia script
	#Input: raw and segmented file
	#Output: (xScale, yScale, zScale) in nanometers 
	#		MaxCell to use within WebKronossos
	#		image sequence of both files at Tmp/source/color and Tmp/source/segmentation
	export outputPython=($(python removeBackgroundToWebKnossos.py $fileNameRaw $fileNameSeg))
	# https://stackoverflow.com/questions/17238608/how-to-return-multiple-variables-from-python-to-bash

	for (( numFrame = 1; numFrame <= ${outputPython[4]}; numFrame++ )); do
		mkdir -p Tmp/wkw$numFrame

		#Second step: Using scales and filenames of previous steps, create wkw files
		python -m wkcuber --layer_name segmentation --scale ${outputPython[0]},${outputPython[1]},${outputPython[2]} --dtype uint16 --name generic Tmp/source$numFrame/segmentation/ Tmp/wkw$numFrame
		python -m wkcuber --layer_name color --scale ${outputPython[0]},${outputPython[1]},${outputPython[2]} --dtype uint8 --name generic Tmp/source$numFrame/color/ Tmp/wkw$numFrame

		#Third step: create the zip within ToUpload/filename.zip
		cd Tmp/wkw$numFrame
		zip -r ../../ToUpload/${fileNameRawOnly%.tif}_T${numFrame}_maxCell_${outputPython[3]}.zip *
		cd ..
		cd ..
	done

	#Forth step: remove everything from Tmp
	rm -r Tmp
done