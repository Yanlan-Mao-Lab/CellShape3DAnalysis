#!/bin/bash

# Step 1: Obtain segmentation from pretrained model


# Step 2: Proofreading

# Step 2.1: Prepare segmented data to WebKnossos upload
./uploadSegmentationToWebKnossos.sh '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/ImageAnalysis/Datasets/Original/RiciBarrientos/NubG4-UASmyrGFP_Control/'

# Step 2.2: Webknossos


# Step 2.3: Export annotations to image sequence
python apply_merger_mode_tiff.py ToUpload/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270/ Downloaded/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270__explorational__pvicente_munuera__c80702/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270__explorational__pvicente_munuera__c80702.nml RefinedTiff/


# Step 3: Transfer learning

# Step 3.1: Prepare datasets


# Step 3.2: Pytorch-3dunet - Transfer learning 
train3dunet --config training_ownData.yaml

# Step 3.3: Predictions from the 'improved model'


# Go again to Step 2
