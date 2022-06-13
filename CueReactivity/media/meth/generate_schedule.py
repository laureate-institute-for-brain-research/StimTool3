#!/opt/apps/core/python/2.7.11/bin/python

from random import shuffle

meth_file = open('drug_image_list.txt', 'r')

meth_images = [[], [], [], [], [], []]


for l in meth_file.readlines():
   this_line = l.split()
   if this_line[0] == 'x':
      continue #injection images without hands
   meth_images[int(this_line[0])].append(this_line[1])

for i in range(1, len(meth_images)):
   shuffle(meth_images[i])


neutral_file = open('neutral_image_list.txt', 'r')

neutral_images = [[], [], [], [], [], []]


for l in neutral_file.readlines():
   this_line = l.split()
   neutral_images[int(this_line[0])].append(this_line[1])

for i in range(1, len(neutral_images)):
   shuffle(meth_images[i])


schedule_lines = []
iti_durations = ['8','8','8','10','10','12','12','12']
iti_idx = 0
shuffle(iti_durations)


schedule_lines.append('TrialTypes,Stimuli,Durations,ExtraArgs')
schedule_lines.append('090,media\\blank.png,10,')
box_values = ['0', '0', '0', '0', '0', '1']

for i in range(0,4): #four blocks, alternating between neutral and drug blocks
   shuffle(box_values)
   neutral_lines = [box_values[0] + '00,' + neutral_images[0][i] + ',5,']
   neutral_lines.append(box_values[1] + '01,' + neutral_images[1][i] + ',5,')
   neutral_lines.append(box_values[2] + '02,' + neutral_images[2][i] + ',5,')
   neutral_lines.append(box_values[3] + '03,' + neutral_images[3][i] + ',5,')
   neutral_lines.append(box_values[4] + '04,' + neutral_images[4][i] + ',5,')
   neutral_lines.append(box_values[5] + '05,' + neutral_images[5][i] + ',5,')
   shuffle(neutral_lines)
   neutral_lines.append('009,media\\meth\\urge_question.PNG,5,')
   neutral_lines.append('091,media\\fixation.png,' + iti_durations[iti_idx] + ',')
   iti_idx = iti_idx + 1
   shuffle(box_values)
   meth_lines = [box_values[0] + '10,' + meth_images[0][i] + ',5,']
   meth_lines.append(box_values[1] + '11,' + meth_images[1][i] + ',5,')
   meth_lines.append(box_values[2] + '12,' + meth_images[2][i] + ',5,')
   meth_lines.append(box_values[3] + '13,' + meth_images[3][i] + ',5,')
   meth_lines.append(box_values[4] + '14,' + meth_images[4][i] + ',5,')
   meth_lines.append(box_values[5] + '15,' + meth_images[5][i] + ',5,')
   shuffle(meth_lines)
   meth_lines.append('019,media\\meth\\urge_question.PNG,5,')
   meth_lines.append('091,media\\fixation.png,' + iti_durations[iti_idx] + ',')
   iti_idx = iti_idx + 1
   schedule_lines = schedule_lines + neutral_lines + meth_lines
   
schedule_lines = schedule_lines + ['090,media\\blank.png,10,']

schedule_out = open('MCR_T0_R1_RIGHT.schedule', 'w')
for l in schedule_lines:
   print l
   schedule_out.write(l + '\n')

schedule_out.close()





