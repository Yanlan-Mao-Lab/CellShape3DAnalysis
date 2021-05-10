function [neighbours] = calculateNeighbours(boundingBoxesCells, radius)
%CALCULATENEIGHBOURS Summary of this function goes here
%   Detailed explanation goes here

for numCell = 1:size(boundingBoxesCells, 1)
    bboxImageOfCell = image(currentBBox(2): (currentBBox(2) + currentBBox(5)), currentBBox(1) : (currentBBox(1) + currentBBox(4)), currentBBox(3):(currentBBox(3) + currentBBox(6)));
    dilatedImage = imdilate(boundingBoxesCells{numCell, 1}, strel('sphere', radius));
    bboxImageOfCell_Dilated = bboxImageOfCell;
    bboxImageOfCell_Dilated(dilatedImage==0) = 0;
end

