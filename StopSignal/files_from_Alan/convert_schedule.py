
import os, random
from psychopy import visual, core, event, data, gui, sound




original = open('Trials.trl', 'r')
original.readline()

output = open('ScheduleP.csv', 'w')
output.write('TrialTypes,Stimuli,Durations,ExtraArgs\n')
for line in original:
    all_values = line.split()
    tone = all_values[0]
    shape = all_values[2]
    time = all_values[4]
    if int(shape) > 2:
        shape = str(int(shape) - 7)
    elif int(shape) == 2:
        shape = '0'
    trial_type = tone + shape
    output.write(trial_type + ',,' + str(float(time) / 1000)+ ',\n')
    