#!/bin/bash
eval "$(conda shell.bash hook)"
source menu.sh

export WORKDIR=/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis

while 
	# Generates dialog with options
	declare -a options=("Pretraining" "Proofreading" "Transfer learning" "Exit");
	generateDialog "options" "Choose an option" "${options[@]}"

	read choice

	if [ $choice -eq 1 ]; then
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
		$WORKDIR/2_Segmentation/1_PreTrainedPredictions/runAllSegmentationMethodsPlantSeg.sh $WORKDIR/Datasets/PreTrainedModel confocal_unet_bce_dice_ds3x

		#exit 1

		## Check basic features of segmented images to see which are better
		echo '---- Segmentation goodness ----'
		#python $WORKDIR/2_Segmentation/1_PreTrainedPredictions/segmentationGoodness.py $WORKDIR/Datasets/PreTrainedModel/RobTetley/
		#python $WORKDIR/2_Segmentation/1_PreTrainedPredictions/segmentationGoodness.py $WORKDIR/Datasets/PreTrainedModel/AlejandraGuzman/
		#python $WORKDIR/2_Segmentation/1_PreTrainedPredictions/segmentationGoodness.py $WORKDIR/Datasets/PreTrainedModel/RiciBarrientos/
		echo '---- Segmentation goodness: Done! ----'

		## Pick best segmentations
		#2_Proofreading/selectBestOutput.sh $WORKDIR/Datasets/PreTrainedModel $WORKDIR/Datasets/PreTrainedModel_best $WORKDIR/Datasets/HDF5/

		## Postprocess output
		echo '---- Postprocess output ----'

		echo '---- Postprocess output: Done! ----'

		#Finish
		conda deactivate
	fi

	if [ $choice -eq 2 ]; then
		# Step 2: Proofreading
		echo '------------------ Proofreading step ----------------------'

		# Step 2.1: Prepare segmented data to WebKnossos upload and postprocess it
		conda activate webkronosos

		echo '# Creating a random file to upload to WebKnossos' #### ADD HERE THE DIRECTORY WHERE IT BELONGS
		cd 2_Proofreading/
		#./uploadSegmentationToWebKnossos.sh $WORKDIR/Datasets/ToProcess/ RobTetley
		#./uploadSegmentationToWebKnossos.sh $WORKDIR/Datasets/ToProcess/ AlejandraGuzman
		#./uploadSegmentationToWebKnossos.sh $WORKDIR/Datasets/ToProcess/ RiciBarrientos/NubG4-UASmyrGFP-UASMbsRNAi
		#./uploadSegmentationToWebKnossos.sh $WORKDIR/Datasets/ToProcess/ RiciBarrientos/NubG4-UASmyrGFP_Control
		#./uploadSegmentationToWebKnossos.sh $WORKDIR/Datasets/ToProcess/ RiciBarrientos/NubG4-UASmyrGFP-UASRokRNAi

		# Step 2.2: Webknossos

		# Go to: https://webknossos.org/dashboard/datasets
		#exit 1

		## Download volume annotation from webKnossos


		dataSetName=RobTetley
		# Step 2.3: Export annotations to image sequence
		for fileName in 1_ToUpload/$dataSetName/*
		do
			export fileNameRaw="$(basename "${fileName}")"
			downloadedFile=$(ls 2_Downloaded/$dataSetName/${fileNameRaw%.zip}*.zip)
			#echo $fileName
			echo ${fileNameRaw%.zip}

			if [ $downloadedFile != '' ]; then

				mkdir 1_ToUpload/$dataSetName/${fileNameRaw%.zip}
				unzip -o $fileName -d 1_ToUpload/$dataSetName/${fileNameRaw%.zip}

				mkdir 2_Downloaded/$dataSetName/${fileNameRaw%.zip}
				unzip -o $downloadedFile -d 2_Downloaded/$dataSetName/${fileNameRaw%.zip}

				unzip -o 2_Downloaded/$dataSetName/${fileNameRaw%.zip}/data.zip -d 2_Downloaded/$dataSetName/${fileNameRaw%.zip}/segmentation

				cp 1_ToUpload/$dataSetName/${fileNameRaw%.zip}/datasource-properties.json 2_Downloaded/$dataSetName/${fileNameRaw%.zip}/datasource-properties.json

				mkdir 3_RefinedTiff/$dataSetName/${fileNameRaw%.zip}
				python -m wkcuber.export_wkw_as_tiff --source_path 2_Downloaded/$dataSetName/${fileNameRaw%.zip}/ --destination_path 3_RefinedTiff/$dataSetName/${fileNameRaw%.zip} --layer_name segmentation
			fi
		done

		#rm 1_ToUpload/*
		#rm -r 2_Downloaded/*
		cd ..
	fi


	if [ $choice -eq 3 ]; then
		# Step 3: Transfer learning
		echo '------------------ Transfer learning step ----------------------'

		# Step 3.1: Prepare datasets
		python 2_Proofreading/createDatasetFromTiff.py $WORKDIR/Datasets/HDF5/RobTetley/

		conda deactivate

		cd 3_TransferLearning/pytorch-3dunet/pytorch3dunet/

		# Step 3.2: Pytorch-3dunet - Transfer learning 
		conda activate 3dunet
		train3dunet --config ../../training_RobData.yaml

		# Step 3.3: Predictions from the 'improved model'
		predict3dunet --config ../../test_ownData_Rob.yaml
		conda deactivate

		cd ../../../

		conda activate plant-seg
		$WORKDIR/2_Segmentation/1_PreTrainedPredictions/runAllSegmentationMethodsPlantSeg.sh $WORKDIR/Datasets/HDF5/ ModelPredictions


		#2_Proofreading/selectBestOutput.sh $WORKDIR/Datasets/PreTrainedModel $WORKDIR/Datasets/PreTrainedModel_best $WORKDIR/Datasets/HDF5/
		# Go again to Step 2
	fi

	[[ $choice -ne 0 ]]
do true; done