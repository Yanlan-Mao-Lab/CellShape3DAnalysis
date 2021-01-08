function [bboxImageOfCells] = discretizeCells(labelledImage, offset)
%DISCRETIZECELLS Summary of this function goes here
%   Detailed explanation goes here

idCells = unique(labelledImage(:))';
idCells(idCells == 0) = [];

boundingBoxesCells = regionprops3(labelledImage, 'BoundingBox');
bboxImageOfCells = cell(max(idCells), 2);
for numCell = idCells
    currentBBox = boundingBoxesCells.BoundingBox(numCell, :);
    currentBBox = round(currentBBox + [-offset -offset -offset currentBBox(1) + offset*2 currentBBox(2) + offset*2 currentBBox(3) + offset*2]);

    try
        bboxImageOfCells{numCell, 1} = labelledImage(currentBBox(2): currentBBox(5), currentBBox(1) : currentBBox(4), currentBBox(3): currentBBox(6));
    catch ex
        currentBBox(currentBBox(1:3) <= 0) = 1;
        lastPart = currentBBox(4:6);
        sizeLabelledImage = size(labelledImage);
        lastPart(currentBBox(4:6) >= size(labelledImage)) = sizeLabelledImage(currentBBox(4:6) >= size(labelledImage));
        currentBBox(4:6) = lastPart;
        bboxImageOfCells{numCell, 1} = labelledImage(currentBBox(2): currentBBox(5), currentBBox(1) : currentBBox(4), currentBBox(3): currentBBox(6));
    end
    bboxImageOfCells{numCell, 2} = currentBBox;
end

end

