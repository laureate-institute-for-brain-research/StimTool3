README for the GoNoGo Task

# TODO
# SUMMARY
Participants view a fixation cross, with a jittered duration from 700-1100 ms (M = 900 ms) followed by one of four letter stimuli (e.g., A, B, C, D; duration = 250 ms) followed by a blank screen for 450 ms. Three letters will function as a “go” stimulus and 1 will function as a no-go stimulus on 25% of trials. A total of 280 trials will be used (70 per stimulus).
# TRIAL STRUCTURE WIN
``` 
 700-1100ms              250ms                450ms    
[ Fixation ] --> [   Letter Display   ] --> [Blank Screen]
^                ^              ^^^         ^     
FIXATION      LETTER_ONSET   RESPONSE    BLANK_ONSET
```

# INPUT DETAILS

```
EACH LINE CODES: one trial<br/>
COLUMN 1: TrialTypes - Letter
COLUMN 2: Stimuli - Not used
COLUMN 3: Durations - fixation stimuli blank
COLUMN 4: ExtraArgs - G=GO or N=NOGO

TRIAL ORDER: fixed
```

# OUTPUT DETAILS

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
result: Letter

FIXATION (4)
response_time: not used
response: not used
result: fixation duration

LETTER_ONSET (5)
response_time: not used
response: not used
result: letter

RESPONSE (5)
response_time: time between RESPONSE and LETTER_ONSET
response: not used
result: Go=G or NoGo=N 

BLANK_ONSET (5)
response_time: not used
response: not used
result: duration
```
