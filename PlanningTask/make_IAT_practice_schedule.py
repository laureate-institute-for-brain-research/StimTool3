# Make the Blocks Schedule 
import random



header = """Trial Types: 1 = "Flowers|Insect"; 2 = "Good|Bad"; 3 = "Flowers or Good|Insects or Bad"; 4 = "Flowers or Bad|Insects or Good", Target Stimuli (Words), Durations (.5 or 1), ExtraArgs (None)"""

## Make R1


def getFixationDuration():
   """
   Get Fixatio Duration 
   14 samples, average of 3 seconds

   Returns intger in seconds
   """
   fixation_durations = [2,2,2,2,2,2,3,3,3,3,4,4,5,5]
   duration = random.sample(fixation_durations,1)[0]
   return str(duration)
   

output  = open('IAT_Practice.schedule', 'w+')
output.write(header + '\n')
for block in range(1,5):
    print block
    blockfile = open('media/practice_block_%s.csv' % block, 'r')
    for idx, line in enumerate(blockfile):
        row = []
        if idx == 0:
            continue
        cols = line.replace('\n','').split(',')
        target_word = cols[0]
        left_word = cols[1]
        right_word = cols[2]
        correct = cols[3]

        row.append(str(block))
        row.append(target_word)
        row.append(getFixationDuration()) # Duration of the stimulus being shown
        row.append(left_word)
        row.append(right_word)
        row.append(correct)

        output.write(','.join(row) + '\n')
output.close()
