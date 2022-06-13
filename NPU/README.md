# README for the NPU task

## SUMMARY

This task presetnts subjects with cues. There are 2 stimuluation devices. WN generator and Digitimer (shock)

## TRIAL STRUCTURE
```
      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET


|<-------total trial duration ------------->|
                                    
           -- N (no shock)   --
[       stim_text	     ] -> [ green circle  ] 
                            |     8s        |  
^ TRIAL_ONSET               ^ CUE_ONSET            
                                |  40 ms |
                                ^ WN_ONSET

  -- P(shock only during red sequre) --
[       stim_text	     ] -> [ red square  ] 
                            |     8s      |  
^ TRIAL_ONSET               ^ CUE_ONSET            
                                |  40 ms |
                                ^ WN_ONSET
                                  |100 ms|
                                  ^ SHOCK_ONSET

     -- U (shock at any time) --
[       stim_text	     ] -> [blue triangle] 
                            |     8s      |  
^ TRIAL_ONSET               ^ CUE_ONSET            
                                |  40 ms |
                                ^ WN_ONSET
                        |100 ms|
                         ^ SHOCK_ONSET
```


## INPUT DETAILS 
```
EACH LINE CODES: one trial
COLUMN 1: X_X_X_X X[0]->NPU X[1]->CUE(1=Show CUE|0=Dont Show) X[2]-> STARTLE(1=STARTLE|0=Dont Startle) X[3]->SHOCK(1=Shock|0=Dont Shock
COLUMN 2: not used
COLUMN 3: cue onset
COLUMN 4: startleonset_shockOnset
TRIAL ORDER IS: fixed
```

## OUTPUT DETAILS

Trial Types Decoding

4 numbers concactenaed by '_' underscore ie. 1_2

### first character:
 - N: No Shock
 - P: Predictable Shock (Shock only during red square)
 - U: Unpredictable Shocks (Shock any time)

### second number (CUES)
 - 0: Don't show cue (geometric shapes)
 - 1: Show cue

### third number (Startle/WN noise)
 - 0: Don't startle for this trial
 - 1: Initiate startle, look at startle onset to when it will fire

### 4th number (Shock)
 - 0: Don't shock for this trial
 - 1: Initiate shock, look at shockOnset onset to when it will fire


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
result: the fixation duration

STIMTEXT_ONSET (5)
response_time: not used
response: not used
result: not used

CUE_ONSET (6)
response_time: not used
response: duration of cue
result: not used

WN_ONSET (7)
response_time: not used
response: the duration of the white noise
result: not used

SHOCK_ONSET (8)
response_time: mot used
response: duration of the shock
result: not used

ANXIETY_RESPONSE (9)
response_time: mot used
response: increase/decrease
result: result anxiety rating (0 - 10)
```