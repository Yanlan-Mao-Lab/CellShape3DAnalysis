function [neighbours] = calculateNeighbours(image,radius)
%CALCULATENEIGHBOURS Summary of this function goes here
%   Detailed explanation goes here

idCells = unique(image(:));
idCells(idCells == 0) = [];

boundingBoxesCells = regionprops3(image, 'BoundingBox');
for numCell = idCells'
    currentBBox = boundingBoxesCells.BoundingBox(numCell, :);
    currentBBox = round(currentBBox) + [-radius -radius -radius radius*2 radius*2 radius*2];
    %TODO: CHECK NEGATIVE VALUES AND OUT OF THE IMAGE VALUES
    bboxImageOfCell = image(currentBBox(2): (currentBBox(2) + currentBBox(5)), currentBBox(1) : (currentBBox(1) + currentBBox(4)), currentBBox(3):(currentBBox(3) + currentBBox(6)));
    dilatedImage = imdilate(bboxImageOfCell == numCell, strel('sphere', radius));
    bboxImageOfCell_Dilated = bboxImageOfCell;
    bboxImageOfCell_Dilated(dilatedImage==0) = 0;
end

