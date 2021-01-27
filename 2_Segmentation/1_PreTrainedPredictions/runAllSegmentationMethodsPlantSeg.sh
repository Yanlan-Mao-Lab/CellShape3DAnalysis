#!/bin/bash

inputPath=/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/PreTrainedModel

allData=("AlejandraGuzman" "RobTetley") #"RiciBarrientos/NubG4-UASmyrGFP_Control" "RiciBarrientos/NubG4-UASmyrGFP-UASMbsRNAi" "RiciBarrientos/NubG4-UASmyrGFP-UASRokRNAi")

pretrainedModel=confocal_unet_bce_dice_ds3x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

len=${#allData[@]}
for (( numData=0; numData<$len; numData++ ))
do
	currentPath=$inputPath/${allData[numData]}/$pretrainedModel/

	# Instance segmentation
	List="GASP MutexWS DtWatershed"
	arrayMethods=($List)

	for numMethod in {0..2}
	do 
		if [ ! -d "$currentPath/${arrayMethods[numMethod]}" ]; then
			sed -e "s@currentMethod@${arrayMethods[numMethod]}@g" \
			 -e "s@currentPath@${currentPath}@g" $DIR/Generic_InstanceSegmentation.yaml > $DIR/Temp.yaml

			plantseg --config $DIR/Temp.yaml
			rm $DIR/Temp.yaml
		fi
	done
done
