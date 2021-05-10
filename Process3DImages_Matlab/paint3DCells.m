function [] = paint3DCells(labelledImage, showingCells, colours)
%PAINT3DCELLS Summary of this function goes here
%   Detailed explanation goes here
    
    if isempty(showingCells)
        showingCells = (1:max(labelledImage(:)));
        showingCells(showingCells==0) = [];
    end
    
    if isempty(colours)
        colours = colorcube(double(max(labelledImage(:))));
        colours = colours(randperm(max(labelledImage(:))), :);
    end

    for numSeed = showingCells
        % Painting each cell
        [x,y,z] = ind2sub(size(labelledImage),find(labelledImage == numSeed));

        if (length(x)>500 && length(x)<50000)
            shp = alphaShape(y,x,z);
            pc = criticalAlpha(shp,'one-region');
            shp.Alpha = pc+3;
            plot(shp, 'FaceColor', colours(numSeed, :), 'EdgeColor', 'none', 'AmbientStrength', 0.3, 'FaceAlpha', 1);
            %pcshow([x,y,z], colours(numSeed, :));
            hold on;
        end
    end
    
    axis equal
    camlight left;
    camlight right;
    lighting flat
    material dull
    
    newFig = gca;
    newFig.XGrid = 'off';
    newFig.YGrid = 'off';
    newFig.ZGrid = 'off';
    hold off;
end

