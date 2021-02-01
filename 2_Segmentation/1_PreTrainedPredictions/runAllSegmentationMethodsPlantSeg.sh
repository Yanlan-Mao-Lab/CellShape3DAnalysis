#!/bin/bash

inputPath=/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/PreTrainedModel

allData=("RobTetley" "AlejandraGuzman" "RiciBarrientos/NubG4-UASmyrGFP_Control" "RiciBarrientos/NubG4-UASmyrGFP-UASMbsRNAi" "RiciBarrientos/NubG4-UASmyrGFP-UASRokRNAi")

pretrainedModel=confocal_unet_bce_dice_ds3x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

len=${#allData[@]}
for (( numData=0; numData<$len; numData++ ))
do
	echo "#${allData[numData]}"
	currentPath=$inputPath/${allData[numData]}/$pretrainedModel/
	if [ ${allData[numData]} = "AlejandraGuzman" ]; then
		betaParameters="0.7 0.7 -1 0.5"
		probabilityThreshold="0.5 0.5 -1 0.5"
	elif [ ${allData[numData]} = "RobTetley" ]; then
		betaParameters="0.4 0.5 -1 0.5"
		probabilityThreshold="0.6 0.4 -1 0.3"
	else # Generic params
		betaParameters="0.6 0.6 0.6 0.6"
		probabilityThreshold="0.5 0.5 0.5 0.5"
	fi

	betaParam=($betaParameters)
	probThresh=($probabilityThreshold)

	# Instance segmentation
	List="GASP MutexWS DtWatershed MultiCut"
	arrayMethods=($List)

	for numMethod in {0..3}
	do 
		echo "##${arrayMethods[numMethod]}"
		if [ ${betaParam[numMethod]} != -1 ]; then
			if [ ! -d "$currentPath/${arrayMethods[numMethod]}_${probThresh[numMethod]}_${betaParam[numMethod]}" ]; then
				
				sed -e "s@currentMethod@${arrayMethods[numMethod]}@g" \
				 -e "s@currentPath@${currentPath}@g" \
				 -e "s@betaParam@${betaParam[numMethod]}@g" \
				 -e "s@probThresh@${probThresh[numMethod]}@g" \
				 $DIR/Models/Generic_InstanceSegmentation.yaml > $DIR/Models/Temp.yaml

				plantseg --config $DIR/Models/Temp.yaml > out.log
				rm $DIR/Models/Temp.yaml
			fi
		fi
		echo "##${arrayMethods[numMethod]} - Done!"
	done
	echo "#${allData[numData]} - Done!"
done
