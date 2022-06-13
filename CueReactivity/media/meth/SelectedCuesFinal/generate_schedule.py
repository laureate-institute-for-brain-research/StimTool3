#!/opt/apps/core/python/2.7.11/bin/python

from random import shuffle
from random import seed

seed(123)

image_file = open('MCR_selected_split.csv', 'r')

meth_images_pre = [[], [], [], [], [], []]
meth_images_post = [[], [], [], [], [], []]

neutral_images_pre = [[], [], [], [], [], []]
neutral_images_post = [[], [], [], [], [], []]

neutral_path = 'media\\meth\\SelectedCuesFinal\\NeutralCues\\'
drug_path = 'media\\meth\\SelectedCuesFinal\\DrugCues\\'
for l in image_file.readlines()[1:]: #skip header line, build lists of images
   this_line = l.split(',')
   index = int(this_line[9])
   fname = this_line[0]
   if this_line[10] == 'control':
      image_fullpath = neutral_path + fname
      if this_line[12] == 'TRUE':
         neutral_images_pre[index].append(image_fullpath)
      else:
         neutral_images_post[index].append(image_fullpath)
   if this_line[10] == 'drug':
      image_fullpath = drug_path + fname
      if this_line[12] == 'TRUE':
         meth_images_pre[index].append(image_fullpath)
      else:
         meth_images_post[index].append(image_fullpath)


print meth_images_pre
print meth_images_post
print neutral_images_pre
print neutral_images_post




for i in range(0, 6):
   shuffle(meth_images_pre[i])
   shuffle(meth_images_post[i])

   shuffle(neutral_images_pre[i])
   shuffle(neutral_images_post[i])




def generate_one(neutral_images, meth_images, output_name):
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

   schedule_out = open(output_name, 'w')
   for l in schedule_lines:
      print l
      schedule_out.write(l + '\n')

   schedule_out.close()


generate_one(neutral_images_pre, meth_images_pre, 'MCR_T0_R1_RIGHT.schedule')


generate_one(neutral_images_post, meth_images_post, 'MCR_T0_R2_RIGHT.schedule')


















