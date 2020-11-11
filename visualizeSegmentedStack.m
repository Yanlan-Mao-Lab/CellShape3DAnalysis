

%Read stack
stackFile = 'Data/190321_RnG4-UASmyrGFP_CELLOTAPE-FILTERPAPER_DISH-3-DISC-1_STACK_SR-2-5X_predictions_gasp_average.tiff';
[tiff_stack] = readStackFile(stackFile);

xyScale = 0.0744151;
zScale = 0.5336974;
resizingSize = 1;

tiff_stack_trueScale = uint16(imresize3(double(tiff_stack), size(tiff_stack)/resizingSize .* [1 1 zScale/xyScale], 'nearest'))-1;

clearvars tiff_stack

%featuresImage = regionprops3(tiff_stack_trueScale-1, 'all');

lastCell = max(tiff_stack_trueScale(:));
background = tiff_stack_trueScale == 0;

background_dilated = imdilate(background, strel('sphere', 1));
outerLayerTissue = uint16(tiff_stack_trueScale>0 & background_dilated) .* tiff_stack_trueScale;

clearvars background_dilated background

outerAreasOfCell = cell(lastCell, 1);
for numCell = 1:lastCell
    numCell
    outerAreasOfCell{numCell} = regionprops3(outerLayerTissue == numCell, 'Volume');
end

cellfun(@(x) length(x), outerAreasOfCell);

[neighbours] = calculateNeighbours(tiff_stack_trueScale, 4);

% infoPerZ = {};
% for numZ = 1:size(tiff_stack_trueScale, 3)
%     numZ
%     infoPerZ{numZ} = regionprops(tiff_stack_trueScale(:, :, numZ)-1, {'Area', 'MajorAxisLength', 'MinorAxisLength' 'Eccentricity', 'Orientation', 'ConvexArea', 'FilledArea', 'EquivDiameter', 'Solidity', 'Extent', 'Perimeter'});
% end

cellHeights = zeros(lastCell, length(infoPerZ));
for numZ = 1:length(infoPerZ)
    numZ
    actualZ = infoPerZ{numZ};
    
    for numCell = 1:length(actualZ)
        cellHeights(numCell, numZ) = actualZ(numCell).Area;
    end
end

for numCell = 1:size(cellHeights, 1)
    numZsOfCell = find(cellHeights(numCell, :));
    
end
find(cellHeights(1, :))

% outputCSV = cell(lastCell, 1);
% 
% for numSeed = 2:lastCell
%     numSeed
%     % Painting each cell
%     [x,y,z] = ind2sub(size(tiff_stack_trueScale),find(tiff_stack_trueScale == numSeed));
%     x = x * resizingSize;
%     y = y * resizingSize;
%     z = z * resizingSize;
%     outputCSV{numSeed} = [x, y, z, repmat(numSeed, [length(x) 1]), x*xyScale, y*xyScale, z*xyScale];
% end
% 
% outputCSV_all = vertcat(outputCSV{2:end});
% 
% outputCSV_T = array2table(outputCSV_all);
% 
% writetable(outputCSV_T, '190321_RnG4-UASmyrGFP_CELLOTAPE-FILTERPAPER_DISH-3-DISC-1_STACK_SR-2-5X_segmentedCells.csv');

paint3DCells(tiff_stack_trueScale - 1, [], [])