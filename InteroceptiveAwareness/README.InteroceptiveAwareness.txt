README for the Interoceptive Awareness Task

*****************************************************************SUMMARY**************************************************************************

This task has two different interoceptive conditions and one exteroceptive condition.
The interoceptive conditions have either the word "Heart" or "Stomach" presented, and the subject is instructed to pay attention to sensations coming from his/her heart or stomach.
The exteroceptive condition has the word "Target" alternate between black and a shade of grey, with 7 different levels of change.
In the exteroceptive condition, the text alternates colors once a second.
In about half of trials, subjects are asked to rate the intensity of their sensations or the intensity of the color change.
They have 5 seconds to make a rating from 1 to 7

As it's implemented for the T1000, this task's run numbering is a little odd.  This is because there are three possible schedules, and two of them are used for each subject.
The schedules are named T1000_IA_T0_R1.schedule, T1000_IA_T0_R2.schedule, and T1000_IA_T0_R3.schedule.  These can be called individually and they will be run as called.
Alternatively, specifying either T1000_IA_T0_Random1.schedule or T1000_IA_T0_Random2.schedule will pick a random schedule of the 3.
This happens like this: the first time a random schedule is specified, a subject specific random order is stored in ../DATA/[SID]-T0-_IA-RX-PARA.txt.
This file stores two variables, schedule_1 and schedule_2--which are randomly chosen without replacement from the three possible schedules.  
If T1000_IA_T0_Random1.schedule is chosen, then schedule_1 is used, and if T1000_IA_T0_Random2.schedule is chosen, then schedule_2 is used.

*****REGARDLESS OF WHICH SCHEDULE IS USED, T1000_IA_T0_Random1.schedule produces an output file named AAXXX-T0-_IA-R1-_BEH.csv and T1000_IA_T0_Random2.schedule produces an output file called AAXXX-T0-_IA-R2-_BEH.csv*****
This is so the naming here matches up with the naming from the scanner.
To see which actual schedule(s) were run for a particular subject (that used random schedule(s)) check the mapping in ../DATA/[SID]-T0-_IA-RX-PARA.txt.  This file will only exist when random schedules are chosen

*****************************************************************TRIAL STRUCTURE******************************************************************

      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET

         10s
[interoceptive image or fixation] ->
^
IMAGE_ONSET

           10s, 1s between color changes
         [exteroceptive image] ->
         ^  ^  ^  ^  ^  ^  ^ ^
IMAGE_ONSET TARGET_COLOR_CHANGE

                  5s
            [rating trial] ->
            ^    ^ ^ ^   ^
RATING_ONSET RATING_CHANGE RATING_LOCK	FINAL_RATING

*****************************************************************INPUT DETAILS********************************************************************

EACH LINE CODES: one trial
COLUMN 1: Trial type (0->fixation, 1->heart, 2->stomach, 11-17->target with intensity of 1 to 7, 4->heart rating, 5->stomach rating, 6->target rating)
COLUMN 2: not used
COLUMN 3: trial duration
COLUMN 4: not used
TRIAL ORDER: fixed, but run order is randomized (2 of 3 possible schedules are presented in a random order)

0: fixation
1: heart
2: stomach
11: target intensity 1
12: target intensity 2
13: target intensity 3
14: target intensity 4
15: target intensity 5
16: target intensity 6
17: target intensity 7
4: heart rating
5: stomach rating
6: target rating
-1: heartbeat
-2: breath
-3: head
-4: lungs
-11: heartbeat response
-12: breath response
-13: head response
-14: lungs response


Note that ratings are treated as separate trials.  So every "heart rating" trial should be immediately after a "heart" trial.

Duration is the length of the trial--this should always be 10 for interoception/exteroception trials and 5 for rating trials.
Duration will be variable for fixation trials.

Each subject does two runs in the scanner.  These two runs are randomly selected from three possible, which makes 6 total orders.
When the program is run, it checks for a file named data/[SID]_IA.order.  If this file exists, it should have two (different) space separated integers 1, 2, or 3.  If not, it is created randomly.  Scanning run 1 will be the first integer and run 2 will be the second integer in this file.


*****************************************************************OUTPUT DETAILS*******************************************************************

INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

IMAGE_ONSET (3)
onset time for fixation, heart, stomach, or target
response_time: not used
response: not used
result: not used

TARGET_COLOR_CHANGE (4)
marks each time the color of the target stimulus changes
response_time: not used
response: not used
result: color the target changed to

RATING_ONSET (5)
marks the onset of a rating period.
response_time: not used
response: not used
result: not used

RATING_CHANGE (6)
each time the subject moves the rating selector
response time: the time between this change and RATING_ONSET
response: is 1 for up and -1 for down
result: the current rating after making this change

FINAL_RATING (7)
response_time: the time between RATING_ONSET and FINAL_RATING, or 'NA' if the subject does not lock in a rating
response: the selected rating (or the current rating at the end of the 5s selection period)
result: not used



