README for the GoNoGo Task

# TODO
# SUMMARY
Participants view a fixation cross, with a jittered duration from 700-1100 ms (M = 900 ms) followed by one of four letter stimuli (e.g., A, B, C, D; duration = 250 ms) followed by a blank screen for 450 ms. Three letters will function as a “go” stimulus and 1 will function as a no-go stimulus on 25% of trials. A total of 280 trials will be used (70 per stimulus).
# TRIAL STRUCTURE WIN
``` 
 1200-1600ms            250ms                1800ms                  variable_time    
[ Fixation ] --> [   Word Display   ] --> [Blank Screen] --> [        Question       ]
^                ^                        ^                  ^               ^^^^^^   
FIXATION      LETTER_ONSET                BLANK_ONSET        QUESTION_ONSET  RESPONSE 
```

# INPUT DETAILS

```
EACH LINE CODES: one trial<br/>
COLUMN 1: TrialTypes - Word
COLUMN 2: Stimuli - Not used
COLUMN 3: Durations - fixation stimuli blank
COLUMN 4: ExtraArgs - Not used

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

FIXATION (3)
response_time: not used
response: not used
result: fixation duration

WORD_ONSET (4)
response_time: not used
response: not used
result: word

BLANK_ONSET (5)
response_time: time between RESPONSE and LETTER_ONSET
response: not used
result: not used

QUESTION_ONSET (6)
response_time: not used
response: not used
result: not used

RESPONSE (7)
response_time: time between QUESTION_ONSET and RESPONSE
response: not used
result: YES or NO
```
