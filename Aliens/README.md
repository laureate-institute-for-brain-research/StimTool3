# README for the Attention Faces Task

## SUMMARY

This task presents subjects with a a face image and a row of letters.
The subjects must press the left key when they see an N in the letters and press the right key when they see an X

## TRIAL STRUCTURE
```
      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET

|<------------- total trial duration ------------->|
[      stimulus	  ] -> [            isi            ]
|   	200 ms 	  |    |    ~ variable duration    |
^ STIM_ONSET           ^ FIXATION_ONSET
^ TRIAL_ONSET                              
                         |         response                |
                         ^ RESPONSE                        ^ OUTCOME
```


## INPUT DETAILS 
```
EACH LINE CODES: one trial
COLUMN 1: TrialTypes (*_*_*) [0] = 1 -> Shuffle/Not Shuffle; [2] -> 'N'/'X'; [3] -> 1/2/3 Face Type
COLUMN 2: Stimuli
COLUMN 3: Durations
COLUMN 4: not used
TRIAL ORDER IS: fixed
```

## OUTPUT DETAILS

Trial Types:

3 numbers concactenaed by '_' underscore ie. 1_2_1
first number:
 - 1: Shuffled Letters
 - 2: Not Suffled, in other words, all the same letter
2nd number:
 - 1: Means there is an 'N' in the string of letters
 - 2: Means there is an 'X' in the string of letters

3rd number:
 - 1: Fearful Face
 - 2: Neutral Face
  -3: Combination (used onlyd during practice)

```
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

FIXATION_ONSET (4)
response_time: not used
response: not used
result: the iti duration

STIM_ONSET (5)
response_time: not used
response: the file path of the image used
result: the string letter used

RESPONSE (6)
response_time: time between STIM_ONSET and RESPONSE
response: 0 or 1 for left or right
result: 0 or 1 for incorrect or correct

OUTCOME (7)
response_time: ent of TRIAL. should be (200ms + isi duration)
response: 0, 1 or 2 . 0 for never pressed, 1 for pressed left, 2, for pressed right
result: 0 or 1 for incorrect or correct
```