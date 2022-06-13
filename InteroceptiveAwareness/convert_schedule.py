
import os, random
from psychopy import visual, core, event, data, gui, sound




original = open('IASchedule3.csv', 'r')

output = open('T1000_IA_Schedule3.csv', 'w')
output.write('TrialTypes (0:fix; 1:heart; 2:stomach; 11-17:target_with_intensity; 4:heart_rating; 5:stomach_rating; 6:target_rating),Stimuli,Durations,ExtraArgs\n')
for line in original:
    all_values = line.split(',')
    print all_values
    if all_values[1] == 'NULL':
        output.write('0,,' + str(float(all_values[0]) / 1000) + ',\n')
    if all_values[1] == 'TargetDetection_event':
        output.write(str(10 + int(all_values[3])) + ',,10,\n')
    if all_values[1] == 'Heart_event':
        output.write('1,,10,\n')
    if all_values[1] == 'Stomach_event':
        output.write('2,,10,\n')
    if all_values[1] == 'TargetDetection_event+respose':
        output.write(str(10 + int(all_values[3])) + ',,10,\n')
        output.write('6,,5,\n')
    if all_values[1] == 'Heart_event+respose':
        output.write('1,,10,\n')
        output.write('4,,5,\n')
    if all_values[1] == 'Stomach_event+respose':
        output.write('2,,10,\n')
        output.write('5,,5,\n')
    
    