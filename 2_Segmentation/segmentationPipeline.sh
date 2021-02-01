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
python $WORKDIR/2_Segmentation/segmentationGoodnes.py $WORKDIR/Datasets/PreTrainedModel
echo '---- Segmentation goodness: Done! ----'

###### CARE WITH THIS #######
###### JUST FOR DEBUG PURPOSES#####
exit 1

###### NEED TO CHECK 
selectBestOutput.sh

## Postprocess output
echo '---- Postprocess output ----'
echo '---- Postprocess output: Done! ----'

#Finish
conda deactivate 

# Step 2: Proofreading
echo '------------------ Proofreading step ----------------------'

# Step 2.1: Prepare segmented data to WebKnossos upload and postprocess it
conda activate webkronosos

cd 2_Segmentation/2_Proofreading/
./uploadSegmentationToWebKnossos.sh '$WORKDIR/Datasets/ToProcess/RobTetley/'
./uploadSegmentationToWebKnossos.sh '$WORKDIR/Datasets/ToProcess/AlejandraGuzman/'
./uploadSegmentationToWebKnossos.sh '$WORKDIR/Datasets/ToProcess/RiciBarrientos/NubG4-UASmyrGFP-UASMbsRNAi/'
./uploadSegmentationToWebKnossos.sh '$WORKDIR/Datasets/ToProcess/RiciBarrientos/NubG4-UASmyrGFP_Control/'
./uploadSegmentationToWebKnossos.sh '$WORKDIR/Datasets/ToProcess/RiciBarrientos/NubG4-UASmyrGFP-UASRokRNAi/'
cd ../..

# Step 2.2: Webknossos

# Go to: https://webknossos.org/dashboard/datasets

# Step 2.3: Export annotations to image sequence

python apply_merger_mode_tiff.py ToUpload/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270/ Downloaded/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270__explorational__pvicente_munuera__c80702/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270__explorational__pvicente_munuera__c80702.nml RefinedTiff/


# Step 3: Transfer learning
echo '------------------ Transfer learning step ----------------------'

# Step 3.1: Prepare datasets
python createDatasetFromTiff.py '$WORKDIR/Datasets/ToProcess/' '$WORKDIR/Datasets/HDF5/'

conda deactivate

# Step 3.2: Pytorch-3dunet - Transfer learning 
conda activate 3dunet
train3dunet --config training_ownData.yaml

# Step 3.3: Predictions from the 'improved model'
predict3dunet --config test_ownData.yaml
conda deactivate

# Go again to Step 2
