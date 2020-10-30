%Read stack
stackFile = '/Users/pablovicentemunuera/Documents/ImageAnalysis/Data/190321_RnG4-UASmyrGFP_CELLOTAPE-FILTERPAPER_DISH-3-DISC-1_STACK_SR-2-5X_predictions_gasp_average.tiff';
[tiff_stack] = readStackFile(stackFile);

xyScale = 0.0744151;
zScale = 0.5336974;
resizingSize = 4;

tiff_stack_trueScale = imresize3(double(tiff_stack), size(tiff_stack)/resizingSize .* [1 1 zScale/xyScale], 'nearest');

paint3DCells(tiff_stack_trueScale - 1, [], [])