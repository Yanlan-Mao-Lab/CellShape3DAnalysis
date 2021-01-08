

%Read stack
stackFile = 'Data/190321_RnG4-UASmyrGFP_CELLOTAPE-FILTERPAPER_DISH-3-DISC-1_STACK_SR-2-5X_predictions_gasp_average.tiff';
[tiff_stack] = readStackFile(stackFile);

xyScale = 0.0744151;
zScale = 0.5336974;
resizingSize = 1;

tiff_stack_trueScale = uint16(imresize3(double(tiff_stack), size(tiff_stack)/resizingSize .* [1 1 zScale/xyScale], 'nearest'))-1;

clearvars tiff_stack

[bboxImageOfCells] = discretizeCells(tiff_stack_trueScale, 4);

%featuresImage = regionprops3(tiff_stack_trueScale-1, 'all');

lastCell = max(tiff_stack_trueScale(:));
background = tiff_stack_trueScale == 0;

background_dilated = imdilate(background, strel('sphere', 1));
outerLayerTissue = uint16(tiff_stack_trueScale>0 & background_dilated) .* tiff_stack_trueScale;

clearvars background_dilated background
%clearvars tiff_stack_trueScale

outerAreasOfCell = cell(lastCell, 1);
featuresOfCells = cell(lastCell, 4);

bboxImageOfCells(:, 4) = {[]};

selectedCells = find(cellfun(@(x) size(x, 3), bboxImageOfCells(:, 1)) > 200);
for numCell = 1:lastCell
    numCell
    
    %3D features
    featuresOfCells{numCell, 1} = regionprops3(bboxImageOfCells{numCell, 1} == numCell, {'Volume', 'EquivDiameter', 'Extent', 'PrincipalAxisLength', 'Orientation', 'ConvexVolume', 'Solidity', 'SurfaceArea'});
    
    %3D features of apical and basal layer
    currentBoundingBox = bboxImageOfCells{numCell, 2};
    outerLayerOfCell = outerLayerTissue(currentBoundingBox(2): currentBoundingBox(5), currentBoundingBox(1) : currentBoundingBox(4), currentBoundingBox(3): currentBoundingBox(6))>0 & bboxImageOfCells{numCell, 1} == numCell;
    featuresOfCells{numCell, 2} = regionprops3(outerLayerOfCell, {'Volume', 'Centroid', 'EquivDiameter', 'Extent', 'PrincipalAxisLength', 'Orientation', 'ConvexVolume', 'Solidity', 'SurfaceArea'});
    bboxImageOfCells{numCell, 3} = outerLayerOfCell;
    %2D features
    currentCellImage = bboxImageOfCells{numCell, 1};
    currentCellPerZ = cell(size(currentCellImage, 3), 1);
    for numZ = 1:size(currentCellImage, 3)
        currentCellPerZ{numZ} = regionprops(currentCellImage(:, :, numZ) == numCell, {'Area', 'MajorAxisLength', 'MinorAxisLength' 'Eccentricity', 'Orientation', 'ConvexArea', 'FilledArea', 'EquivDiameter', 'Solidity', 'Extent', 'Perimeter'});
    end
    featuresOfCells(numCell, 3) = {currentCellPerZ};
    %Neighbours
    %featuresOfCells{numZ, 4} = calculateNeighbours(bboxImageOfCells(:, 1), radius);
end

%% Cells with at least 150 zs and that have only a basal and apical side (sortof)
correctCells = cellfun(@(x) size(x, 3), bboxImageOfCells(:, 1)) > 150 & cellfun(@(x) size(x, 1) == 2, featuresOfCells(:, 2));

correctFeatureCells = featuresOfCells(correctCells, :);

featureTable = vertcat(correctFeatureCells{:, 1});
cellHeight = [];
apicalSurface = [];
basalSurface = [];
lateralArea = [];
for numCell = 1:size(correctFeatureCells, 1)
    numCell
    apicoBasalFeatures = correctFeatureCells{numCell, 2};
    [~, apical] = min(apicoBasalFeatures.Centroid(:, 3));
    [~, basal] = max(apicoBasalFeatures.Centroid(:, 3));
    
    cellHeight(numCell, 1) = pdist2(apicoBasalFeatures.Centroid(1, :), apicoBasalFeatures.Centroid(2, :));
    apicalSurface(numCell, 1) = apicoBasalFeatures.Volume(apical);
    basalSurface(numCell, 1) = apicoBasalFeatures.Volume(basal);
    lateralArea(numCell, 1) = correctFeatureCells{numCell, 1}.SurfaceArea(1) - apicalSurface(numCell) - basalSurface(numCell);
end
featureTable = horzcat(featureTable, table(cellHeight, apicalSurface, basalSurface, lateralArea));
featureTablePixels = featureTable;

featureTableMicrons = featureTable;

featureTableMicrons.Volume = featureTable.Volume * xyScale^3;
featureTableMicrons.apicalSurface = featureTable.apicalSurface  * xyScale^2;
featureTableMicrons.basalSurface = featureTable.basalSurface * xyScale^2;
featureTableMicrons.cellHeight = featureTable.cellHeight * xyScale^1;
featureTableMicrons.ConvexVolume = featureTable.ConvexVolume * xyScale^3;
featureTableMicrons.EquivDiameter = featureTable.EquivDiameter * xyScale^1;
featureTableMicrons.lateralArea = featureTable.lateralArea * xyScale^1;
featureTableMicrons.PrincipalAxisLength = featureTable.PrincipalAxisLength * xyScale^1;
featureTableMicrons.SurfaceArea = featureTable.SurfaceArea * xyScale^2;

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