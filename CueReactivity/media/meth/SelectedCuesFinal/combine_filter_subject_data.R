

subjects_to_keep <- c("AL016", "AL473", "AL550", "AL914", "AM031", "AP299",
                      "AQ029", "AR005", "AR560", "AR868", "AT042", "AU922", "AV940", "AW653", "AW656",
                      "AW709", "AX387", "AX402", "AY394", "AZ007")


redcap_data <- read.csv('cue_rating_REDCAP_data.csv')

redcap_data <- redcap_data[redcap_data$record_id %in% subjects_to_keep,]
write.csv(redcap_data, 'cue_rating_REDCAP_data-filtered.csv', row.names = FALSE)


library(ggplot2)
library(reshape2)
t_result <- t.test(redcap_data$pre_ddq_desire_score, redcap_data$post_ddq_desire_score, paired = TRUE)
desire <- melt(redcap_data[, c('record_id', 'pre_ddq_desire_score', 'post_ddq_desire_score')])
p <- ggplot(desire) + geom_line(aes(x = variable, y = value, group = record_id, color = record_id)) +
  ggtitle(paste('Desire p = ', round(t_result$p.value, digits = 2))) + geom_point(aes(x = variable, y = value, group = record_id, color = record_id))
ggsave('desire.png', p)



t_result <- t.test(redcap_data$pre_ddq_neg_score, redcap_data$post_ddq_neg_score, paired = TRUE)
desire <- melt(redcap_data[, c('record_id', 'pre_ddq_neg_score', 'post_ddq_neg_score')])
p <- ggplot(desire) + geom_line(aes(x = variable, y = value, group = record_id, color = record_id)) +
  ggtitle(paste('Neg p = ', round(t_result$p.value, digits = 2))) + geom_point(aes(x = variable, y = value, group = record_id, color = record_id))
ggsave('neg.png', p)





t_result <- t.test(redcap_data$pre_ddq_controle_score, redcap_data$post_ddq_controle_score, paired = TRUE)
desire <- melt(redcap_data[, c('record_id', 'pre_ddq_controle_score', 'post_ddq_controle_score')])
p <- ggplot(desire) + geom_line(aes(x = variable, y = value, group = record_id, color = record_id)) +
  ggtitle(paste('Control p = ', round(t_result$p.value, digits = 2))) + geom_point(aes(x = variable, y = value, group = record_id, color = record_id))
ggsave('control.png', p)


png('post_desire.png')
hist(redcap_data$post_ddq_desire_score)
dev.off()

png('post_neg.png')
hist(redcap_data$post_ddq_neg_score)
dev.off()


png('post_control.png')
hist(redcap_data$post_ddq_controle_score)
dev.off()



