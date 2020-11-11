function [outputArg1,outputArg2] = discretizeCells(labelledImage, offset)
%DISCRETIZECELLS Summary of this function goes here
%   Detailed explanation goes here

idCells = unique(labelledImage(:))';
idCells(idCells == 0) = [];

boundingBoxesCells = regionprops3(labelledImage, 'BoundingBox');
for numCell = idCells
    currentBBox = boundingBoxesCells.BoundingBox(numCell, :);
    currentBBox = round(currentBBox) + [-offset -offset -offset currentBBox(1) + offset*2 currentBBox(2) + offset*2 currentBBox(3) + offset*2];
    %TODO: CHECK NEGATIVE VALUES AND OUT OF THE IMAGE VALUES
    try
        bboxImageOfCell = labelledImage(currentBBox(2): currentBBox(5), currentBBox(1) : (currentBBox(1) + currentBBox(4)), currentBBox(3):(currentBBox(3) + currentBBox(6)));
    catch ex
        
    end
end

end

