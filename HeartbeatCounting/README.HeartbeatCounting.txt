README for the Heartbeat Counting Task

*****************************************************************SUMMARY**************************************************************************

This task has four different trial types, typically each done for 60 seconds.

Heartbeat tapping with guessing:
The subject presses a key in sync with his/her heartbeat and guesses when uncertain.

Tone tapping:
The subject presses a key in sync with a presented tone.

Heartbeat tapping without guessing:
The subject taps in sync with his/her heartbeat, but is instructed to tap ONLY when relatively certain.

Heartbeat tapping without guessing and with a breath hold:
The subject taps in sync with his/her heartbeat while performing a maximal inspiratory breath hold and is instructed only to tap when relatively certain.

*****************************************************************TRIAL STRUCTURE******************************************************************

     [instruct slide] -> 
     ^              ^
INSTRUCT_ONSET TASK_ONSET

[trial instructions ]       ->  [         trial                    ] -> [ stop screen ]      ->      [   vas ratings   ]     ->
 ^                               ^   ^ ^ ^ ^ ^ ^ ^  ^              ^                  ^                ^    ^   ^
TRIAL_INSTRUCT_ONSET    TRIAL_ONSET  TONE TAP TONE TAP      TRIAL_COMPLETE   STOP_SCREEN_END             VAS_RATING





*****************************************************************INPUT DETAILS********************************************************************
EACH LINE CODES: one trial
COLUMN 1: trial type (0->guess, 1->tone, 2->no guess, 3->breath hold no guess)
COLUMN 2: not used
COLUMN 3: trial duration
COLUMN 4: not used
TRIAL ORDER IS: fixed

*****************************************************************OUTPUT DETAILS*******************************************************************
trial types:
0: heartbeat with guessing
1: tone
2: heartbeat no guessing
3: heartbeat breath hold no guessing


INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

TRIAL_INSTRUCT_ONSET (3)
response_time: not used
response: not used
result: not used

TRIAL_ONSET (4)
response_time: not used
response: not used
result: not used

TONE (5)
response_time: not used
response: not used
result: not used

TAP (6)
response_time: not used
response: key pressed (should be down, might be left, up, or right)
result: not used

TRIAL_COMPLETE (8)
response_time: time between TRIAL_COMPLETE and TRIAL_ONSET
response: total number of taps this trial
result: not used

STOP_SCREEN_END (9)
response_time: time between TRIAL_COMPLETE and STOP_SCREEN_END
response: not used
result: not used

VAS_RATING (10)
response_time: time between rating being shown and answer given
response: rating from 0 to 100
result: VAS question asked
