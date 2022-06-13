library(reshape2)
long_data <- read.csv('meth_data6_withincompletes.csv', stringsAsFactors = FALSE)





long_data$text[long_data$text == '<p>After seeing this picture, please describe your mood, from negative to positive</p>'] <- 'valence'
long_data$text[long_data$text == '<p>After seeing this picture, please describe level of arousal, from calm to excited</p>'] <- 'arousal'
long_data$text[long_data$text == '<p>How much can this picture induce drug craving in an active methamphetamine user</p>'] <- 'craving'
long_data$text[long_data$text == '<p>How frequently does an active methamphetamine user see scenes like this image during his/her methamphetamine use?</p>'] <- 'typicality'
long_data$text[long_data$text == '<p>Is this picture related to methamphetamine and its use or not?</p>'] <- 'related'
long_data$response[long_data$response == 'NULL'] <- NA
long_data$response <- as.numeric(as.character(long_data$response))
long_data$file <- basename(long_data$url)
#plot individual subject responses by question number

#get rid of trailing spaces in subject IDs
long_data$subjectId <- substr(long_data$subjectId, 1, 5)

groupings <- read.table('image_categories.txt', header = TRUE)
long_data <- merge(groupings, long_data)

library(ggplot2)
library(gridExtra)
library(grid)

#exclude impossible valence/arousal responses
dim(long_data)
long_data <- long_data[!(long_data$text == 'valence' & !(long_data$response %in% 1:9)),]
dim(long_data)
long_data <- long_data[!(long_data$text == 'arousal' & !(long_data$response %in% 1:9)),]
dim(long_data)
long_data <- long_data[!(long_data$text == 'related' & !(long_data$response %in% 0:1)),]
dim(long_data)

for (subject in unique(long_data$subjectId)){
  data_to_plot <- long_data[long_data$subjectId == subject,]
  p1 <- ggplot(data = data_to_plot[data_to_plot$text == 'valence',]) + 
    #geom_line(aes(x = orderNum, y = response)) +
    geom_point(aes(x = orderNum, y = response, color = group)) + ggtitle('valence')
  p2 <- ggplot(data = data_to_plot[data_to_plot$text == 'arousal',]) + 
    #geom_line(aes(x = orderNum, y = response)) +
    geom_point(aes(x = orderNum, y = response, color = group)) + ggtitle('arousal')
  p3 <- ggplot(data = data_to_plot[data_to_plot$text == 'craving',]) + 
    #geom_line(aes(x = orderNum, y = response)) +
    geom_point(aes(x = orderNum, y = response, color = group)) + ggtitle('craving')
  p4 <- ggplot(data = data_to_plot[data_to_plot$text == 'typicality',]) + 
    #geom_line(aes(x = orderNum, y = response)) +
    geom_point(aes(x = orderNum, y = response, color = group)) + ggtitle('typicality')
  filename <- paste(subject, 'responses.png', sep = '_')
  png(filename, width = 1400, height = 400)
  grid.arrange(p1, p2, p3, p4, ncol = 4, top = textGrob(subject, gp=gpar(fontsize = 50)))
  dev.off() 
  
}

#exclude bad subjects
long_data <- long_data[!(long_data$subjectId %in% c('AV614', 'AN590', 'AS924')),]


longer_data <- melt(long_data, id.vars = c('subjectId', 'text', 'url', 'file'))

#extract just the file name
#longer_data$file <- basename(longer_data$url)

longer_data$value[longer_data$value == 'NULL'] <- NA
longer_data$value <- as.numeric(as.character(longer_data$value))

longer_data <- longer_data[longer_data$variable == 'response',]

#wide_data <- dcast(longer_data, formula = subjectId ~ text + file, value.var = 'value')

#mean_responses <- colMeans(wide_data[,names(wide_data) != 'subjectId'], na.rm = TRUE)



summary_values <- aggregate(longer_data[, c('value', 'text', 'file')], by = list(text = longer_data$text, file = longer_data$file), 
                            FUN = mean, na.rm = TRUE)
summary_values <- summary_values[, 1:3]

wide_summary_values <- dcast(summary_values, formula = file ~ text)




write.csv(wide_summary_values, 'meth_data6_summary.csv', row.names=FALSE)


#make a summary file with the mean/sd of each measure to report in the supplement
mean_values <- aggregate(longer_data[, c('value', 'text', 'file')], by = list(text = longer_data$text, file = longer_data$file), 
                            FUN = mean, na.rm = TRUE)
mean_values <- mean_values[, 1:3]
wide_mean_values <- dcast(mean_values, formula = file ~ text)
names(wide_mean_values) <- paste(names(wide_mean_values), 'mean', sep = '_')

sd_values <- aggregate(longer_data[, c('value', 'text', 'file')], by = list(text = longer_data$text, file = longer_data$file), 
                            FUN = sd, na.rm = TRUE)
sd_values <- sd_values[, 1:3]
wide_sd_values <- dcast(sd_values, formula = file ~ text)
names(wide_sd_values) <- paste(names(wide_sd_values), 'sd', sep = '_')

wide_summary_values <- cbind(wide_mean_values, wide_sd_values)


names(wide_summary_values)[1] <- 'file'

hsv_data <- read.csv('MCR_hsv_values_sds.csv')
all_data <- merge(wide_summary_values, hsv_data)


groupings <- read.table('image_categories.txt', header = TRUE)
#for groupings
#NEUTRAL
#0 -> neutral objects
#1 -> neutral objects with hands
#2 -> neutral tools
#3 -> neutral tools with hands
#4 -> neutral tools with hands, complex
#5 -> neutral tools with faces

#DRUG
#0 -> drug
#1 -> drug and hand
#2 -> drug instruments
#3 -> drug intruments and hands
#4 -> drug injection and hands
#5 -> drug activities and facese
#x -> drug injection instruments

groupings$description <- NA
groupings[groupings$group == 'control' & groupings$category == '0', 'description'] <- 'Neutral Objects'
groupings[groupings$group == 'control' & groupings$category == '1', 'description'] <- 'Neutral Objects with Hands'
groupings[groupings$group == 'control' & groupings$category == '2', 'description'] <- 'Neutral Tools'
groupings[groupings$group == 'control' & groupings$category == '3', 'description'] <- 'Neutral Tools with Hands, simple'
groupings[groupings$group == 'control' & groupings$category == '4', 'description'] <- 'Neutral Tools with Hands, complex'
groupings[groupings$group == 'control' & groupings$category == '5', 'description'] <- 'Neutral Tools with Faces'

groupings[groupings$group == 'drug' & groupings$category == '0', 'description'] <- 'Drug'
groupings[groupings$group == 'drug' & groupings$category == '1', 'description'] <- 'Drug and Hand'
groupings[groupings$group == 'drug' & groupings$category == '2', 'description'] <- 'Drug Instruments'
groupings[groupings$group == 'drug' & groupings$category == '3', 'description'] <- 'Drug Instruments and Hands'
groupings[groupings$group == 'drug' & groupings$category == '4', 'description'] <- 'Drug Injection and Hands'
groupings[groupings$group == 'drug' & groupings$category == '5', 'description'] <- 'Drug Activities and Faces'
groupings[groupings$group == 'drug' & groupings$category == 'x', 'description'] <- 'Drug Injection Instruments'

all_data <- merge(groupings, all_data)

write.csv(all_data[,c("file","description", "category", "group","valence_mean",   "valence_sd", "arousal_mean", "arousal_sd",
                    "craving_mean", "craving_sd", "related_mean", "related_sd", "typicality_mean","typicality_sd","hue_mean",       
                   "hue_sd", "saturation_mean", "saturation_sd", "value_mean", "value_sd")], 'meth_cue_summary.csv', row.names=FALSE)


###for each subject, get mean/sd for each image category
#so columns will be: subjectID, description, category, group, valence_mean, valence_sd, arousal_mean, arousal_sd, craving_mean, craving_sd, 
#related_mean, related_sd, typicality_mean, typicality_sd
merged_longer_data <- merge(longer_data, groupings)
individual_mean_values <- aggregate(merged_longer_data[, c('subjectId', 'value', 'text', 'description')], by = list(text = merged_longer_data$text, 
                                                                              description = merged_longer_data$description, subjectId = merged_longer_data$subjectId),
                                                                          FUN = mean, na.rm = TRUE)
individual_mean_values <- individual_mean_values[, c(1:3, 5)]
individual_wide_mean_values <- dcast(individual_mean_values, formula = subjectId + description ~ text)
names(individual_wide_mean_values) <- paste(names(individual_wide_mean_values), 'mean', sep = '_')
names(individual_wide_mean_values)[1] <- 'subjectId'
names(individual_wide_mean_values)[2] <- 'description'

individual_sd_values <- aggregate(merged_longer_data[, c('subjectId', 'value', 'text', 'description')], by = list(text = merged_longer_data$text, 
                                                                     description = merged_longer_data$description, subjectId = merged_longer_data$subjectId),
                                    FUN = sd, na.rm = TRUE)
individual_sd_values <- individual_sd_values[, c(1:3, 5)]
individual_wide_sd_values <- dcast(individual_sd_values, formula = subjectId + description ~ text)
names(individual_wide_sd_values) <- paste(names(individual_wide_sd_values), 'sd', sep = '_')
names(individual_wide_sd_values)[1] <- 'subjectId'
names(individual_wide_sd_values)[2] <- 'description'

individual_data <- merge(individual_wide_mean_values, individual_wide_sd_values)


###
individual_mean_values <- aggregate(merged_longer_data[, c('subjectId', 'value', 'text')], by = list(text = merged_longer_data$text, 
                                                          group = merged_longer_data$group, subjectId = merged_longer_data$subjectId),
                                    FUN = mean, na.rm = TRUE)
individual_mean_values <- individual_mean_values[, c(1:3, 5)]
individual_wide_mean_values <- dcast(individual_mean_values, formula = subjectId + group ~ text)
names(individual_wide_mean_values) <- paste(names(individual_wide_mean_values), 'mean', sep = '_')
names(individual_wide_mean_values)[1] <- 'subjectId'
names(individual_wide_mean_values)[2] <- 'description'

individual_sd_values <- aggregate(merged_longer_data[, c('subjectId', 'value', 'text')], by = list(text = merged_longer_data$text, 
                                                          group = merged_longer_data$group, subjectId = merged_longer_data$subjectId),
                                  FUN = sd, na.rm = TRUE)
individual_sd_values <- individual_sd_values[, c(1:3, 5)]
individual_wide_sd_values <- dcast(individual_sd_values, formula = subjectId + group ~ text)
names(individual_wide_sd_values) <- paste(names(individual_wide_sd_values), 'sd', sep = '_')
names(individual_wide_sd_values)[1] <- 'subjectId'
names(individual_wide_sd_values)[2] <- 'description'

individual_overall_data <- merge(individual_wide_mean_values, individual_wide_sd_values)
individual_overall_data$description <- as.character(individual_overall_data$description)
individual_overall_data$description[individual_overall_data$description == 'control'] <- 'Neutral Overall'
individual_overall_data$description[individual_overall_data$description == 'drug'] <- 'Drug Overall'

###
individual_data <- rbind(individual_data, individual_overall_data)


write.csv(individual_data[order(individual_data$subjectId),], 'individual_category_by_ratings.csv', row.names = FALSE)


#also get just overall category means/sds


this_mean <- aggregate(all_data[, c('valence_mean', 'description')], by = list(description = all_data$description), FUN = mean, na.rm = TRUE)
this_mean <- this_mean[,1:2]
names(this_mean)[2] <- paste(names(this_mean)[2], '_mean', sep = '')
this_sd <- aggregate(all_data[, c('valence_mean', 'description')], by = list(description = all_data$description), FUN = sd, na.rm = TRUE)
this_sd <- this_sd[,1:2]
names(this_sd)[2] <- paste(names(this_sd)[2], '_sd', sep = '')
all_category_summaries <- merge(this_mean, this_sd)

for (i in c('arousal', 'craving', 'related', 'typicality', 'hue', 'saturation', 'value')){
  this_mean <- aggregate(all_data[, c(paste(i, '_mean', sep = ''), 'description')], by = list(description = all_data$description), FUN = mean, na.rm = TRUE)
  this_mean <- this_mean[,1:2]
  names(this_mean)[2] <- paste(names(this_mean)[2], '_mean', sep = '')
  this_sd <- aggregate(all_data[, c(paste(i, '_mean', sep = ''), 'description')], by = list(description = all_data$description), FUN = sd, na.rm = TRUE)
  this_sd <- this_sd[,1:2]
  names(this_sd)[2] <- paste(names(this_sd)[2], '_sd', sep = '')
  all_category_summaries <- merge(all_category_summaries, this_mean)
  all_category_summaries <- merge(all_category_summaries, this_sd)
}

write.csv(all_category_summaries, 'overall_category_stats.csv', row.names = FALSE)












