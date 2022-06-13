


trials <- read.csv('study-CAPSULE_task-SS_run-1_hand-R.schedule')

trials$block <- NA
block <- 0
for (i in 1:nrow(trials)){
  if (trials$TrialTypes[i] == 92){
    block <- block + 1
  }  else{
    trials$block[i]<- block
  }
}
trials$side <- as.character(trials$TrialTypes %% 2)

trials$TrialTypes.factor <- as.character(trials$TrialTypes)

library(tableone)
CreateTableOne(c('TrialTypes.factor', 'side'),strata = 'block', trials) 
