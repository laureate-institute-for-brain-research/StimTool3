



ratings <- read.csv('meth_data5_summary.csv')

hsv <- read.csv('MCR_hsv_values.csv')
merged_data <- merge(ratings, hsv)

groupings <- read.table('image_categories.txt', header = TRUE)

merged_data <- merge(merged_data, groupings)

write.csv(merged_data, 'MCR_all_combined_predata.csv', row.names=FALSE)



hist(merged_data$value)
hist(merged_data$valence)


library(ggplot2)
library(gridExtra)
library(grid)

make_plotset <- function(data_to_plot, main_title, filename, group){
  p1 <- ggplot(data_to_plot, aes_string(x = 'valence', fill = group)) + 
    geom_histogram(binwidth = 0.5, alpha = 0.5, position = 'identity') + theme(legend.position="none")
  p2 <- ggplot(data_to_plot, aes_string(x = 'arousal', fill = group)) + 
    geom_histogram(binwidth = 0.5, alpha = 0.5, position = 'identity') + theme(legend.position="none")
  p3 <- ggplot(data_to_plot, aes_string(x = 'craving', fill = group)) + 
    geom_histogram(binwidth = 10, alpha = 0.5, position = 'identity') + theme(legend.position="none")
  p4 <- ggplot(data_to_plot, aes_string(x = 'typicality', fill = group)) + 
    geom_histogram(binwidth = 10, alpha = 0.5, position = 'identity') + theme(legend.position="none")
  p5 <- ggplot(data_to_plot, aes_string(x = 'hue', fill = group)) + 
    geom_histogram(binwidth = 0.1, alpha = 0.5, position = 'identity') + theme(legend.position="none")
  p6 <- ggplot(data_to_plot, aes_string(x = 'saturation', fill = group)) + 
    geom_histogram(binwidth = 0.1, alpha = 0.5, position = 'identity') + theme(legend.position="none")
  p7 <- ggplot(data_to_plot, aes_string(x = 'value', fill = group)) + geom_histogram(binwidth = 0.1, alpha = 0.5, position = 'identity')
  png(filename, width = 1400, height = 400)
  grid.arrange(p1, p2, p3, p4, p5, p6, p7, ncol = 7, top = textGrob(main_title, gp=gpar(fontsize = 50)))
  dev.off()
}

#plot histgrams including all images
make_plotset(merged_data, 'All Images', 'all_images.png', 'group')



#sort by craving--will select highest craving meth images and lowest craving controls
sorted_data <- merged_data[order(merged_data$craving),]

#will set to TRUE for images selected to be used
#this will be the 8 highest craving drug and lowest craving neutral images in each category
sorted_data$selected <- FALSE

#go forward, marking the first 8 in each category of control images for selection


names(sorted_data)

#number in each group that have been selected 
number_selected <- c(0, 0, 0, 0, 0, 0)

for (i in 1:nrow(sorted_data)){
  #x for injection instruments, category not used
  if (sorted_data[i, 'category'] == 'x' | sorted_data[i, 'group'] == 'drug'){
    next
  }
  this_category <- as.numeric(as.character(sorted_data[i, 'category'])) + 1
  if (number_selected[this_category] > 7){
    next
  }
  number_selected[this_category] <- number_selected[this_category] + 1
  sorted_data[i, 'selected'] <- TRUE
}



#number in each group that have been selected 
number_selected <- c(0, 0, 0, 0, 0, 0)

for (i in nrow(sorted_data):1){
  #x for injection instruments, category not used
  if (sorted_data[i, 'category'] == 'x' | sorted_data[i, 'group'] == 'control'){
    next
  }
  this_category <- as.numeric(as.character(sorted_data[i, 'category'])) + 1
  if (number_selected[this_category] > 7){
    next
  }
  number_selected[this_category] <- number_selected[this_category] + 1
  sorted_data[i, 'selected'] <- TRUE
}


selected_data <- sorted_data[sorted_data$selected,]



set.seed(123)
selected_data$in_set1 <- FALSE
#will randomize these
in_set1 <- c(FALSE, FALSE, FALSE, FALSE, TRUE, TRUE, TRUE, TRUE)
selected_data$category <- as.numeric(as.character(selected_data$category))


for (i in 0:5){
  selected_data[selected_data$category == i & selected_data$group == 'control', 'in_set1'] <- in_set1[sample(8)]
  selected_data[selected_data$category == i & selected_data$group == 'drug', 'in_set1'] <- in_set1[sample(8)]                                                                   
}



library(tableone)
control_tab <- CreateTableOne(vars = c('arousal', 'craving', 'typicality', 'valence', 'hue', 'saturation', 'value'),
                      strata = c('in_set1'), data = selected_data[selected_data$group == 'control',])
control_tab


drug_tab <- CreateTableOne(vars = c('arousal', 'craving', 'typicality', 'valence', 'hue', 'saturation', 'value'),
                              strata = c('in_set1'), data = selected_data[selected_data$group == 'drug',])
drug_tab

selected_data$group_set1 <- paste(selected_data$group, selected_data$in_set1)

write.csv(selected_data, 'MCR_selected_split.csv', row.names=FALSE)

make_plotset(selected_data, 'Selected Images', 'selected_images.png', 'group')
make_plotset(selected_data, 'Selected Images Split', 'selected_images_split.png', 'group_set1')

orig_selected <- read.csv('MCR_selected_split-orig.csv')



