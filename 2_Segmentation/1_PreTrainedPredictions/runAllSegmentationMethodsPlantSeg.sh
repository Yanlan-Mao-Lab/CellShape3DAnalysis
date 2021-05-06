#!/bin/bash

inputPath=$1

allData=("RobTetley" "AlejandraGuzman" "RiciBarrientos/NubG4-UASmyrGFP_Control" "RiciBarrientos/NubG4-UASmyrGFP-UASMbsRNAi" "RiciBarrientos/NubG4-UASmyrGFP-UASRokRNAi")

pretrainedModel=$2 

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

len=${#allData[@]}
for (( numData=0; numData<$len; numData++ ))
do
	echo "#${allData[numData]}"
	currentPath=$inputPath/${allData[numData]}/$pretrainedModel/
	if [ ${allData[numData]} = "AlejandraGuzman" ]; then
		probabilityThreshold="0.0001 -1 -1 -1"
		betaParameters="0.83 -1 -1 -1"
	elif [ ${allData[numData]} = "RobTetley" ]; then
		if [ $pretrainedModel = "confocal_unet_bce_dice_ds3x" ]; then
			probabilityThreshold="0.65 -1 -1 -1"
			betaParameters="0.2 -1 -1 -1"
		else
			probabilityThreshold="0.65 -1 -1 -1"
			betaParameters="0.4 -1 -1 -1"
		fi
	else # Generic params for Rici
		probabilityThreshold="0.75 -1 -1 -1"
		betaParameters="0.3 -1 -1 -1"
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
