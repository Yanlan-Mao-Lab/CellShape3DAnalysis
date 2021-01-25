#!/bin/bash

inputPath=/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/PreTrainedModel

allData=("AlejandraGuzman" "RobTetley" "RicardoBarrientos/NubG4-UASmyrGFP_Control" "RicardoBarrientos/NubG4-UASmyrGFP-UASMbsRNAi" "RicardoBarrientos/NubG4-UASmyrGFP-UASRokRNAi")

pretrainedModel=confocal_unet_bce_dice_ds3x

len=${#allData[@]}
for (( numData=0; numData<$len; numData++ ))
do
	currentPath=$inputPath/${allData[numData]}/$pretrainedModel/

	# Instance segmentation
	List="GASP MultiWS DtWatershed"
	arrayMethods=($List)

	for numMethod in {0..3}
	do 
		sed -e "s@currentMethod@${arrayMethods[numMethod]}@g" \
		 -e "s@currentPath@${currentPath}@g" Generic_InstanceSegmentation.yaml > Temp.yaml

		plantseg --config Temp.yaml
	done
done
