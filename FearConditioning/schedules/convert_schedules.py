
import os, random
from psychopy import visual, core, event, data, gui, sound






def convert_one(run_num):
    original = open('cuerun' + run_num + '.tsf', 'r')

    output = open('T1000_FC_Schedule' + run_num + '.csv', 'w')
    output.write('TrialTypes (0->left arrow; 1->right arrow; 2->CS-; 3->CS+; 4->CS+ & US,Stimuli,Durations,ExtraArgs\n')

    done = False
    while not done:
        this_lines = []
        while True:
            try:
                this_lines.append(original.next())
            except StopIteration:
                return
            if this_lines[len(this_lines) - 1] == ';\n':
                break
        if len(this_lines) == 5: #CS+ or CS-, no stim
            if this_lines[3][4] == '6':
                output.write('3,,,\n')
            elif this_lines[3][4] == '5':
                output.write('2,,,\n')
            else: 
                print 'ERROR1'
                print this_lines
                core.quit()
        elif len(this_lines) == 6: #CS+ & US
            output.write('4,,,\n')
            print this_lines
            print ''
        elif len(this_lines) == 9: #arrow
            if this_lines[3][4] == '2': #left
                output.write('0,,,\n')
            elif this_lines[3][4] == '3': #right
                output.write('1,,,\n')
            else:
                print 'ERROR2'
                print this_lines
                core.quit()
        elif len(this_lines) == 4:
            print 'BLANK TRIAL'
        else:
            print 'ERROR3'
            print this_lines
            core.quit()
    output.close()
convert_one('3')
