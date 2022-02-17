// https://forum.image.sc/t/pipeline-for-cell-tracking-using-cellpose-for-segmentation-and-trackmate-for-tracking/51615
// Dataset : DPC_timelapse_05h.tif
// https://zenodo.org/record/4700067/files/DPC_timelapse_05h.tif?download=1
imageName = getTitle()
//close("\\Others");
roiManager("reset");

// Use Cellpose to get cells segmentation
// it requires :
// - a working Cellpose environment (either conda or venv)
// - the Cellpose wrapper (PTBIOP update site)
//run("Cellpose Advanced", "diameter=30 cellproba_threshold=0.0 flow_threshold=0.4 model=cyto nuclei_channel=-1 cyto_channel=1 dimensionmode=2D");

// Cellpose generates Label image, let convert them to ROIs
// it requires LaRoMe (PTBIOP update site)
run("Label image to ROIs", "");

// Use TrackMate to track the ROIs
// requires to add script to Fiji directory (PTBIOP update site)
run("Run TrackMate from RoiManager", "framegap=3 linkdistance=30 gapdistance=60.0 allowsplit=true splitdistance=80.0 ");

// TrackMate script, renamed ROIs accordingly to track they belong to
// use this information to fill ROIs with color 
// requires LaRoMe (PTBIOP update site)
selectWindow(imageName);
//run("Remove Overlay");
run("ROIs to Measurement Image", "column_name=Pattern pattern=Track-(\\d*):.*");
resetMinAndMax();
run("glasbey inverted");