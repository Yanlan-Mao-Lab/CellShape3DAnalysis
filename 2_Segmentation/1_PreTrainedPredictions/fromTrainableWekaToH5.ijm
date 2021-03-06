//run("Channels Tool...");
Stack.setDisplayMode("grayscale");
run("Close");
run("Split Channels");
selectWindow("C1-Part2_Decon_c1_t2.tif");
selectWindow("C2-Part2_Decon_c1_t2.tif");
selectWindow("C1-Part2_Decon_c1_t2.tif");
run("HDF5 (new or replace)...", "save=/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/PreTrainedModel/RobTetley/confocal_unet_bce_dice_ds3x/C1-Part2_Decon_c1_t2.h5");
selectWindow("C2-Part2_Decon_c1_t2.tif");
run("Invert", "stack");
run("HDF5 (new or replace)...", "save=/media/pablo/d7c61090-024c-469a-930c-f5ada47fb049/PabloVicenteMunuera/CellShape3DAnalysis/Datasets/PreTrainedModel/RobTetley/confocal_unet_bce_dice_ds3x/C2-Part2_Decon_c1_t2.h5");
