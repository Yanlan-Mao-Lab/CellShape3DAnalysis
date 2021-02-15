#!/bin/bash

eval "$(conda shell.bash hook)"

export WORKDIR=/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis

# Step 1: Obtain segmentation from pretrained model
conda activate plant-seg

echo '------------------ Pretraning step ----------------------'

## Alejandra Guzman Data
echo '#Alejandra Guzman Dataset - Pre'
if [ ! -d "$WORKDIR/Datasets/PreTrainedModel/AlejandraGuzman/confocal_unet_bce_dice_ds3x/MultiCut_0.5_0.6/" ]; then
	plantseg --config $WORKDIR/2_Segmentation/1_PreTrainedPredictions/Models/AleData_MultiCut.yaml > out.log
fi
echo '#Ale - Done!'


## Rob Tetley Data
echo '#Rob Tetley Dataset - Pre'
if [ ! -d "$WORKDIR/Datasets/PreTrainedModel/RobTetley/confocal_unet_bce_dice_ds3x/" ]; then
	plantseg --config $WORKDIR/2_Segmentation/1_PreTrainedPredictions/Models/RobData_MultiCut.yaml > out.log
fi
echo '#Rob - Done!'

## Rici Barrientos Data
echo '#Rici Barrientos Dataset - Pre'
### Control
echo '##Control - Pre'
if [ ! -d "$WORKDIR/Datasets/PreTrainedModel/RiciBarrientos/NubG4-UASmyrGFP_Control/confocal_unet_bce_dice_ds3x/MultiCut_0.5_0.6/" ]; then
	plantseg --config $WORKDIR/2_Segmentation/1_PreTrainedPredictions/Models/RiciData_Control_MultiCut.yaml > out.log
fi
echo '##Control - Done!'

### Mbs 
echo '##Mbs - Pre'
if [ ! -d "$WORKDIR/Datasets/PreTrainedModel/RiciBarrientos/NubG4-UASmyrGFP-UASMbsRNAi/confocal_unet_bce_dice_ds3x/MultiCut_0.5_0.6/" ]; then
	plantseg --config $WORKDIR/2_Segmentation/1_PreTrainedPredictions/Models/RiciData_Mbs_MultiCut.yaml > out.log
fi
echo '##Mbs - Done!'

### Rok
echo '##Rok - Pre'
if [ ! -d "$WORKDIR/Datasets/PreTrainedModel/RiciBarrientos/NubG4-UASmyrGFP-UASRokRNAi/confocal_unet_bce_dice_ds3x/MultiCut_0.5_0.6/" ]; then
	plantseg --config $WORKDIR/2_Segmentation/1_PreTrainedPredictions/Models/RiciData_Rok_MultiCut.yaml > out.log
fi
echo '##Rok - Done!'
echo '#Rici - Done!'

## Run the different instance segmentation methods
$WORKDIR/2_Segmentation/1_PreTrainedPredictions/runAllSegmentationMethodsPlantSeg.sh

## Check basic features of segmented images to see which are better
echo '---- Segmentation goodness ----'
#python $WORKDIR/2_Segmentation/1_PreTrainedPredictions/segmentationGoodness.py $WORKDIR/Datasets/PreTrainedModel/RobTetley/
#python $WORKDIR/2_Segmentation/1_PreTrainedPredictions/segmentationGoodness.py $WORKDIR/Datasets/PreTrainedModel/AlejandraGuzman/
#python $WORKDIR/2_Segmentation/1_PreTrainedPredictions/segmentationGoodness.py $WORKDIR/Datasets/PreTrainedModel/RiciBarrientos/
echo '---- Segmentation goodness: Done! ----'

## Pick best segmentations
#2_Proofreading/selectBestOutput.sh

## Postprocess output
echo '---- Postprocess output ----'

echo '---- Postprocess output: Done! ----'

#Finish
conda deactivate 

# Step 2: Proofreading
echo '------------------ Proofreading step ----------------------'

# Step 2.1: Prepare segmented data to WebKnossos upload and postprocess it
conda activate webkronosos

echo '# Creating a random file to upload to WebKnossos' #### ADD HERE THE DIRECTORY WHERE IT BELONGS
cd 2_Proofreading/
#./uploadSegmentationToWebKnossos.sh $WORKDIR/Datasets/ToProcess/RobTetley/
#./uploadSegmentationToWebKnossos.sh $WORKDIR/Datasets/ToProcess/AlejandraGuzman/
#./uploadSegmentationToWebKnossos.sh $WORKDIR/Datasets/ToProcess/RiciBarrientos/NubG4-UASmyrGFP-UASMbsRNAi/
#./uploadSegmentationToWebKnossos.sh $WORKDIR/Datasets/ToProcess/RiciBarrientos/NubG4-UASmyrGFP_Control/
#./uploadSegmentationToWebKnossos.sh $WORKDIR/Datasets/ToProcess/RiciBarrientos/NubG4-UASmyrGFP-UASRokRNAi/

# Step 2.2: Webknossos

# Go to: https://webknossos.org/dashboard/datasets
#exit 1

## Download volume annotation from webKnossos
cd 2_Downloaded
unzip *
cd ..

# Step 2.3: Export annotations to image sequence
for fileName in 1_ToUpload/*
do
	export fileNameRaw="$(basename "${fileName}")"
	downloadedFile=$(ls 2_Downloaded/${fileNameRaw%.zip}*.zip)
	#echo $fileName
	#echo ${fileNameRaw%.zip}

	if [ $downloadedFile != '']; then

		mkdir 1_ToUpload/${fileNameRaw%.zip}
		unzip $fileName -d 1_ToUpload/${fileNameRaw%.zip}

		mkdir 2_Downloaded/${fileNameRaw%.zip}
		unzip $downloadedFile -d 2_Downloaded/${fileNameRaw%.zip}

		unzip 2_Downloaded/${fileNameRaw%.zip}/data.zip -d 2_Downloaded/${fileNameRaw%.zip}/segmentation

		cp 1_ToUpload/${fileNameRaw%.zip}/datasource-properties.json 2_Downloaded/${fileNameRaw%.zip}/datasource-properties.json

		mkdir 3_RefinedTiff/${fileNameRaw%.zip}
		python -m wkcuber.export_wkw_as_tiff --source_path 2_Downloaded/${fileNameRaw%.zip}/ --destination_path 3_RefinedTiff/${fileNameRaw%.zip} --layer_name segmentation
	fi
done

#rm 1_ToUpload/*
#rm -r 2_Downloaded/*
cd ..


# Step 3: Transfer learning
echo '------------------ Transfer learning step ----------------------'

# Step 3.1: Prepare datasets
python 2_Proofreading/createDatasetFromTiff.py $WORKDIR/Datasets/PreTrainedModel/RobTetley/

conda deactivate

exit 1

# Step 3.2: Pytorch-3dunet - Transfer learning 
conda activate 3dunet
train3dunet --config training_ownData.yaml

# Step 3.3: Predictions from the 'improved model'
predict3dunet --config test_ownData.yaml
conda deactivate

# Go again to Step 2
