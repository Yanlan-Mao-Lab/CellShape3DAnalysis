#!/bin/bash

# Prepare segmented data to WebKnossos upload
./uploadSegmentationToWebKnossos.sh '/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/ImageAnalysis/Datasets/Original/RiciBarrientos/NubG4-UASmyrGFP_Control/'


#Export annotations to image sequence
python apply_merger_mode_tiff.py ToUpload/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270/ Downloaded/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270__explorational__pvicente_munuera__c80702/201105_NubG4-UASmyrGFP-UASMbsRNAi_COVERSLIP-FLAT_DISH-3-DISC-1_STACK_maxCell_13270__explorational__pvicente_munuera__c80702.nml RefinedTiff/
