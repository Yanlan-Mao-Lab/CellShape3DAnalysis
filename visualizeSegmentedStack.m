%Read stack
stackFile = 'Data/190321_RnG4-UASmyrGFP_CELLOTAPE-FILTERPAPER_DISH-3-DISC-1_STACK_SR-2-5X_predictions_gasp_average.tiff';
[tiff_stack] = readStackFile(stackFile);

xyScale = 0.0744151;
zScale = 0.5336974;
resizingSize = 1;

tiff_stack_trueScale = imresize3(double(tiff_stack), size(tiff_stack)/resizingSize .* [1 1 zScale/xyScale], 'nearest');

featuresImage = regionprops3(tiff_stack_trueScale-1, 'all');

lastCell = max(tiff_stack_trueScale(:));

infoPerZ = {};
for numZ = 1:size(tiff_stack_trueScale, 3)
    numZ
    infoPerZ{numZ} = regionprops(tiff_stack_trueScale(:, :, numZ)-1, {'Area', 'MajorAxisLength', 'MinorAxisLength' 'Eccentricity', 'Orientation', 'ConvexArea', 'FilledArea', 'EquivDiameter', 'Solidity', 'Extent', 'Perimeter'});
end

outputCSV = cell(lastCell, 1);

for numSeed = 2:lastCell
    numSeed
    % Painting each cell
    [x,y,z] = ind2sub(size(tiff_stack_trueScale),find(tiff_stack_trueScale == numSeed));
    x = x * resizingSize;
    y = y * resizingSize;
    z = z * resizingSize;
    outputCSV{numSeed} = [x, y, z, repmat(numSeed, [length(x) 1]), x*xyScale, y*xyScale, z*xyScale];
end

outputCSV_all = vertcat(outputCSV{2:end});

writetable(outputCSV_all, '190321_RnG4-UASmyrGFP_CELLOTAPE-FILTERPAPER_DISH-3-DISC-1_STACK_SR-2-5X_segmentedCells.csv');

paint3DCells(tiff_stack_trueScale - 1, [], [])