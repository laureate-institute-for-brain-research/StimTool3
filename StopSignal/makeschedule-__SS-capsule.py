#!/opt/apps/core/python3/3.7.2/bin/python3

import random
random.seed(1234)

#create a schedule file for the capsule version of the stop signal task
#in order to have more trials per condition for us in ERP analysis, we decided
#to have just two conditions (500ms/easy, 100ms/hard), 300 trials, and 150 stop/150 go


#92 is instructions/break
#to match T1K, will have 7 of them--one at the beginning, one at the start of hte run,
#one at the end, and 5 in the middle
#so trials will be broken into 6 blocks of 50, with 25 go, 12 or 13 easy, and 13 or 12 hard

fout = open('study-CAPSULE_task-__SS_run-1_hand-X.schedule', 'w')


fout.write('TrialTypes,Stimuli,Durations,ExtraArgs\n')
fout.write('92,,8.0,\n')


#for go trials, will need 75 00 and 75 01
#so, blocks will either have 13/12 or 12/13 00 and 01s
#for stop trials, will need 75 2X (hard), 75 6X (easy), where X is half/half 0 and 1 (for left and right responses)

all_gos = ['00,,1.5,\n'] * 75 + ['01,,1.5,\n'] * 75
random.shuffle(all_gos)

easy_stops = ['60,,1.5,\n'] * 37 + ['61,,1.5,\n'] * 38
random.shuffle(easy_stops)

hard_stops = ['20,,1.5,\n'] * 38 + ['21,,1.5,\n'] * 37
random.shuffle(hard_stops)


for block in list(range(5)):
	if block % 2 == 0:
		these_trials = all_gos[0:25] + easy_stops[0:13] + hard_stops[0:12]
		all_gos = all_gos[25:]
		easy_stops = easy_stops[13:]
		hard_stops = hard_stops[12:]
	else :
		these_trials = all_gos[0:25] + easy_stops[0:12] + hard_stops[0:13]
		all_gos = all_gos[25:]
		easy_stops = easy_stops[12:]
		hard_stops = hard_stops[13:]

	random.shuffle(these_trials)
	for t in these_trials:
		fout.write(t)
	fout.write('92,,12.0,\n')


fout.close()






