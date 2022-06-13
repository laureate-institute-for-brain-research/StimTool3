

%Summarized Hue/Saturation/Value for each image
%Matlab's rgb2hsv converts the rgb values to hsv, and then we simply take the mean/sd for each image.

output_file = fopen('HSV-IAPS.csv', 'w');

image_names = textread('image_list-iaps.txt', '%s');
fprintf(output_file, 'ImageSet,File,hue_mean,hue_sd,saturation_mean, saturation_sd,value_mean, value_sd\n');
for i = 1:length(image_names)
%for i = 1:5
    img = imread(char(strcat('../media/IAPS20081_20/IAPS1_20Images/', image_names(i))));
    [h, s, v] = rgb2hsv(img);
    fprintf(output_file, '%s,%s,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f\n', 'iaps', char(image_names(i)), mean(mean(h)), std2(h), mean(mean(s)), std2(s), mean(mean(v)), std2(v));
end




fclose(output_file);
