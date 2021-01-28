#!/bin/bash

export WORKDIR=/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis

# Step 1: Obtain segmentation from pretrained model
conda activate plant-seg

## Alejandra Guzman Data
if [ ! -d "$WORKDIR/Datasets/PreTrainedModel/AlejandraGuzman/confocal_unet_bce_dice_ds3x/MultiCut_0.5_0.6/" ]; then
	plantseg --config $WORKDIR/2_Segmentation/1_PreTrainedPredictions/AleData_MultiCut.yaml
fi

## Rob Tetley Data
if [ ! -d "$WORKDIR/Datasets/PreTrainedModel/RobTetley/confocal_unet_bce_dice_ds3x/MultiCut_0.5_0.6/" ]; then
	plantseg --config $WORKDIR/2_Segmentation/1_PreTrainedPredictions/RobData_MultiCut.yaml
fi

## Rici Barrientos Data
### Control
if [ ! -d "$WORKDIR/Datasets/PreTrainedModel/RiciBarrientos/NubG4-UASmyrGFP_Control/confocal_unet_bce_dice_ds3x/MultiCut_0.5_0.6/" ]; then
	plantseg --config $WORKDIR/2_Segmentation/1_PreTrainedPredictions/RiciData_Control_MultiCut.yaml
fi

### Mbs 
if [ ! -d "$WORKDIR/Datasets/PreTrainedModel/RiciBarrientos/NubG4-UASmyrGFP-UASMbsRNAi/confocal_unet_bce_dice_ds3x/MultiCut_0.5_0.6/" ]; then
	plantseg --config $WORKDIR/2_Segmentation/1_PreTrainedPredictions/RiciData_Mbs_MultiCut.yaml
fi

### Rok
if [ ! -d "$WORKDIR/Datasets/PreTrainedModel/RiciBarrientos/NubG4-UASmyrGFP-UASRokRNAi/confocal_unet_bce_dice_ds3x/MultiCut_0.5_0.6/" ]; then
	plantseg --config $WORKDIR/2_Segmentation/1_PreTrainedPredictions/RiciData_Rok_MultiCut.yaml
fi

## Run the different instance segmentation methods
$WORKDIR/2_Segmentation/1_PreTrainedPredictions/runAllSegmentationMethodsPlantSeg.sh

#Finish
conda deactivate 

# Step 2: Proofreading

# Step 2.1: Prepare segmented data to WebKnossos upload and postprocess it
conda activate webkronosos

cd 2_Segmentation/Proofreading/
./uploadSegmentationToWebKnossos.sh '$WORKDIR/Datasets/Original/RiciBarrientos/NubG4-UASmyrGFP_Control/'
cd ../..

# Step 2.2: Webknossos
https://webknossos.org/dashboard/datasets

# Step 2.3: Export annotations to image sequence

python apply_merger_mode_tiff.py ToUpload/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270/ Downloaded/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270__explorational__pvicente_munuera__c80702/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270__explorational__pvicente_munuera__c80702.nml RefinedTiff/


# Step 3: Transfer learning

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
