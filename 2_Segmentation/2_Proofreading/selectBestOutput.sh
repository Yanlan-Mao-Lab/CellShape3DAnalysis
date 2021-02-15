#!/bin/bash

#Here, we move the best output of each category to a give directory.
# Also rename _predictions_WHATEVER_ for _predictions_best.tiff

inputPath=/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/PreTrainedModel
outputPath=/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/PreTrainedModel_best
mkdir $outputPath

allData=("RobTetley") #"AlejandraGuzman" "RiciBarrientos/NubG4-UASmyrGFP_Control" "RiciBarrientos/NubG4-UASmyrGFP-UASMbsRNAi" "RiciBarrientos/NubG4-UASmyrGFP-UASRokRNAi")

pretrainedModel=confocal_unet_bce_dice_ds3x

len=${#allData[@]}
for (( numData=0; numData<$len; numData++ ))
do
	if [ ${allData[numData]} = "AlejandraGuzman" ]; then
		bestAlgorithm="${allData[numData]}/$pretrainedModel/";
	elif [ ${allData[numData]} = "RobTetley" ]; then
		bestAlgorithm=${allData[numData]}/$pretrainedModel/GASP_0.4_0.5;
	else #Rici's
		bestAlgorithm="${allData[numData]}/$pretrainedModel/";
	fi

	mkdir $outputPath/${allData[numData]}/
	cp $inputPath/$bestAlgorithm/PostProcessing/*.tiff $outputPath/${allData[numData]}/
	cp $inputPath/$bestAlgorithm/*.h5 $outputPath/${allData[numData]}/

	rename 's/_predictions_.*.tiff/_predictions_best.tiff/g' $outputPath/${allData[numData]}/*
	rename 's/_predictions_.*.h5/_predictions_best.h5/g' $outputPath/${allData[numData]}/*
done