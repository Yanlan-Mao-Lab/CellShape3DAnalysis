function [tiff_stack] = readStackFile(stackFileName)
%READSTACKFILE Summary of this function goes here
%   Detailed explanation goes here
    tiff_info = imfinfo(stackFileName); % return tiff structure, one element per image
    tiff_stack = imread(stackFileName, 1) ; % read in first image

    %concatenate each successive tiff to tiff_stack
    for numZ = 2 : size(tiff_info, 1)
        temp_tiff = imread(stackFileName, numZ);
        tiff_stack = cat(3 , tiff_stack, temp_tiff);
    end
end

