# Make the Blocks Schedule 
import random



header = """Trial Types: 1a = "Death|Life" 1b = "Life | Death"; 2 = "Me|Not Me"; 3a = "Death or Me| Life or Not Me" 3b = "Life or Me | Death or Not Me"; 4a = "Death or Not Me | Life or Me"; 4b = "Life or Not Me | Death or Me", Target Stimuli (Words), Durations (.5 or 1), ExtraArgs (None)"""

## Make R1

# ITI Durations for R1
iti_2 = [2 for x in range(0,36)] # 2s, 36x
iti_3 = [3 for x in range(0,24)] # 3s, 24x
iti_4 = [4 for x in range(0,12)] # 4s, 12x
iti_5 = [5 for x in range(0,12)] # 5s, 12x

iti_durations = iti_2 + iti_3 + iti_4 + iti_5
random.shuffle(iti_durations)

total_ = 0
for dur in iti_durations:
   total_ = total_ + dur
print 'total durations for R1: ', total_

def getFixationDuration(idx):
   """
   Get Fixatio Duration 
   OLD: 14 samples, average of 3 seconds
   New: 
   Need to keep the total durations to under 232 total seconds but range from 2 - 5s
   Returns intger in seconds
   """
   global iti_durations
   return str(iti_durations[idx])
   

output  = open('IAT_run1.schedule', 'w+')
output.write(header + '\n')
trial_no = 0
for block in range(1,5):
   print block
   try:
      blockfile = open('media/block%s_ra.csv' % block, 'r')
      for idx, line in enumerate(blockfile):
         row = []
         if idx == 0:
            continue
         cols = line.replace('\n','').split(',')
         target_word = cols[0]
         left_word = cols[1]
         right_word = cols[2]
         correct = cols[3]

         row.append(str(block) + 'a')
         row.append(target_word)
         row.append(getFixationDuration(trial_no)) # Duration of the stimulus being shown
         row.append(left_word)
         row.append(right_word)
         row.append(correct)

         output.write(','.join(row) + '\n')
         trial_no += 1
   except IOError:
      # Probabl block 2
      blockfile = open('media/block2.csv', 'r')
      for idx, line in enumerate(blockfile):
         row = []
         if idx == 0:
            continue
         cols = line.replace('\n','').split(',')
         target_word = cols[0]
         left_word = cols[1]
         right_word = cols[2]
         correct = cols[3]

         row.append('2')
         row.append(target_word)
         row.append(getFixationDuration(trial_no)) # Duration of the stimulus being shown
         row.append(left_word)
         row.append(right_word)
         row.append(correct)

         output.write(','.join(row) + '\n')
         trial_no += 1
      pass

output.close()


# ITI Durations for R2
iti_2 = [2 for x in range(0,36)] # 2s, 36x
iti_3 = [3 for x in range(0,24)] # 3s, 24x
iti_4 = [4 for x in range(0,12)] # 4s, 12x
iti_5 = [5 for x in range(0,12)] # 5s, 12x

iti_durations = iti_2 + iti_3 + iti_4 + iti_5
random.shuffle(iti_durations)

total_ = 0
for dur in iti_durations:
   total_ = total_ + dur

print 'total duration for R2: ', total_
## Run 2
output  = open('IAT_run2.schedule', 'w+')
output.write(header + '\n')

trial_no = 0
for block in range(1,5):
   print block
   try:
      blockfile = open('media/block%s_rb.csv' % block, 'r')
      for idx, line in enumerate(blockfile):
         row = []
         if idx == 0:
            continue
         cols = line.replace('\n','').split(',')
         target_word = cols[0]
         left_word = cols[1]
         right_word = cols[2]
         correct = cols[3]

         row.append(str(block) + 'b')
         row.append(target_word)
         row.append(getFixationDuration(trial_no)) # Duration of the stimulus being shown
         row.append(left_word)
         row.append(right_word)
         row.append(correct)

         output.write(','.join(row) + '\n')
         trial_no += 1 # increment trial number
   except IOError:
      # Probabl block 2
      blockfile = open('media/block2.csv', 'r')
      for idx, line in enumerate(blockfile):
         row = []
         if idx == 0:
            continue
         cols = line.replace('\n','').split(',')
         target_word = cols[0]
         left_word = cols[1]
         right_word = cols[2]
         correct = cols[3]

         row.append('2')
         row.append(target_word)
         row.append(getFixationDuration(trial_no)) # Duration of the stimulus being shown
         row.append(left_word)
         row.append(right_word)
         row.append(correct)

         output.write(','.join(row) + '\n')
         trial_no += 1
      pass

output.close()
   

