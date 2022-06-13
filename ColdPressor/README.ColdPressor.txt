README for the Cold Pressor Task

*****************************************************************SUMMARY**************************************************************************

This module records data for the cold pressor task.
The subject is presented with an instruction slide, then has a chance to practice making ratings with the mouse scroll wheel.
After that, there is one more instruction slide--hitting enter when the subject places his hand in the water begins the cold pressor trial and hitting enter again ends it when he removes his hand.

*****************************************************************TRIAL STRUCTURE******************************************************************

[instruction slide] -> [rating practice trial] -> [cold pressor trial]
^                                            ^
INSTRUCT_START                        TASK_START

-> [trial (rating practice or cold pressor)] -> 
   ^             ^   ^   ^   ^             ^
 TRIAL_START    MARKER_LOCATION        TRIAL_COMPLETE
 
*****************************************************************INPUT DETAILS********************************************************************

This task does not use an input file.
TRIAL ORDER IS: fixed

*****************************************************************OUTPUT DETAILS*******************************************************************

trial 0 is the practice trial, trial 1 is the trial using the ice bath

INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

TRIAL_ONSET (3)
response_time: not used
response: not used
result: not used

MARKER_LOCATION (4)
response_time: time between TRIAL_START and MARKER_LOCATION
response: location of marker on rating scale, scaled to be in the range [0,1]
result: not used

TRIAL_COMPLETE (5)
response_time: total time this trial took (duration of hand in water)
response: not used
result: not used

VAS_RATING (6)
response_time: time to make a response
response: Rating in the range [0,100]
result: Question asked