


output_file = fopen('MCR_hsv_values_sds.csv', 'w');

drug_names = textread('drug_list.txt', '%s');
fprintf(output_file, 'file,hue_mean,hue_sd,saturation_mean, saturation_sd,value_mean, value_sd\n');
for i = 1:length(drug_names)
    img = imread(char(strcat('DrugCues/', drug_names(i))));
    [h, s, v] = rgb2hsv(img);
    fprintf(output_file, '%s,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f\n', char(drug_names(i)), mean(mean(h)), std2(h), mean(mean(s)), std2(s), mean(mean(v)), std2(v));
    
end



neutral_names = textread('neutral_list.txt', '%s');
for i = 1:length(neutral_names)
    img = imread(char(strcat('NeutralCues/', neutral_names(i))));
    [h, s, v] = rgb2hsv(img);
    fprintf(output_file, '%s,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f,%6.3f\n', char(neutral_names(i)), mean(mean(h)), std2(h), mean(mean(s)), std2(s), mean(mean(v)), std2(v));
    
end

fclose(output_file);