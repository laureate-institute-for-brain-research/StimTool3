README for the Tap-To-Safety Task

# SUMMARY

**This task consists of the following five parts:**</br></br>
<ins>Part A (fear acquisition):</ins> This part displays stimuli one at a time onscreen, has participants make ratings, and sometimes administers shocks (or, depending on the version of the task, negative imagery). The shocks are paired with one of the three stimulus-types. <br/>
<ins>Part B Training:</ins> This part involves multiple tapping routines. The first serves the purpose of determining an individuals tapping capabilities (an 
upper level on how much effort they can exert). The last serves the purpose of allowing a participant to practice appropriate effort and to provide 
feedback related to different amounts of taps in relation to their previously identified effort limit.<br/>
<ins>Part B:</ins> This part is similar to Part A, however, the participant is now given the opportunity to neutralize the negative outcome by tapping on some trials. The shocks are paired with one of the three stimulus-types, just like in Part A.<br/>
<ins>Part C:</ins> This is the same as Part B, except that new stimuli are introduced which are never paired with shock.<br/>
<ins>Part D:</ins> This is the same as Part B, except that no shocks are delivered.<br/>

# TRIAL STRUCTURE PART A
``` 
    1.0s | 2.0s                            4.0s                                  0.0s ~ 2.0s                          1.0s                  3.0s ~ 9.0s
[Stimuli Presented] --------> [       Rating Displayed       ] -------------> [Post Rating Pause] --> [Shock (sometimes) + Red Outline] -> [    ITI    ]
^                             ^               ^^^            ^                ^                       ^                                    ^
TRIAL_ONSET / STIM_ONSET      RATING_ONSET  RATING_CHANGE    FINAL_RATING     PAUSE_ONSET             SHOCK_ONSET and/or OUTLINE_ONSET     FIXATION_ONSET
```
# TRIAL STRUCTURE PART B
```
    1.0s | 2.0s                             4.0s                                     2.0                4.0s
[Stimuli Presented] --------> [       Rating Displayed       ] -------------> [Tap Soon Screen] --> [Tap Now Screen] -->
^                             ^               ^^^            ^                ^                     ^          ^^^
TRIAL_ONSET / STIM_ONSET      RATING_ONSET  RATING_CHANGE    FINAL_RATING     TAP_SOON              TAP_ONSET  TAPS

             4.0s                                  0.0s ~ 2.0s                          1.0s                  3.0s ~ 9.0s 
[    Second Rating Displayed   ] -------------> [Post Rating Pause] --> [Shock (sometimes) + Red Outline] -> [    ITI    ]
^               ^^^            ^                ^                       ^                                    ^
RATING_ONSET  RATING_CHANGE    FINAL_RATING     PAUSE_ONSET             SHOCK_ONSET and/or OUTLINE_ONSET     FIXATION_ONSET
```
# TRIAL STRUCTURE PART C
``` 
   1.0s | 2.0s                               4.0s                                     2.0                4.0s
[Stimuli Presented] --------> [       Rating Displayed       ] -------------> [Tap Soon Screen] --> [Tap Now Screen] -->
^                             ^               ^^^            ^                ^                     ^          ^^^
TRIAL_ONSET / STIM_ONSET      RATING_ONSET  RATING_CHANGE    FINAL_RATING     TAP_SOON              TAP_ONSET  TAPS

             4.0s                                  0.0s ~ 2.0s                          1.0s                  3.0s ~ 9.0s 
[    Second Rating Displayed   ] -------------> [Post Rating Pause] --> [Shock (sometimes) + Red Outline] -> [    ITI    ]
^               ^^^            ^                ^                       ^                                    ^
RATING_ONSET  RATING_CHANGE    FINAL_RATING     PAUSE_ONSET             SHOCK_ONSET and/or OUTLINE_ONSET     FIXATION_ONSET
```
# TRIAL STRUCTURE PART D
``` 
   1.0s | 2.0s                               4.0s                                     2.0                 4.0s
[Stimuli Presented] --------> [       Rating Displayed       ] -------------> [Tap Soon Screen] --> [Tap Now Screen] -->
^                             ^               ^^^            ^                ^                     ^          ^^^
TRIAL_ONSET / STIM_ONSET      RATING_ONSET  RATING_CHANGE    FINAL_RATING     TAP_SOON              TAP_ONSET  TAPS

             4.0s                                  0.0s ~ 2.0s                  1.0s                 3.0s ~ 9.0s 
[    Second Rating Displayed   ] -------------> [Post Rating Pause] --> [No Shock + Red Outline] -> [    ITI    ]
^               ^^^            ^                ^                       ^                           ^
RATING_ONSET  RATING_CHANGE    FINAL_RATING     PAUSE_ONSET             OUTLINE_ONSET               FIXATION_ONSET
```

# INPUT DETAILS

```
EACH LINE CODES: one trial<br/>
COLUMN 1: TrialTypes - pavCS, neutCS, GEN-dummyN, GEN-NAnx, GEN-NRisk, GEN-PNRisk, GEN-PNAnx, neutCSE
COLUMN 2: Stimuli - the path to the stim image used
COLUMN 3: Durations - PostRatingPause and ITI (space separated)
COLUMN 4: ExtraArgs - (<ANX|RISK|NONE>_<VIRTUAL-SHOCK|SHOCK|NO-SHOCK>_<NEUT|NO-NEUT> = (<2|1|0>_<2|1|0>_<1|0>))

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
result: lane length

PRACTICE_ONSET (3) [NOT USED]
response_time: not used
response: not used
result: not used

MAIN_ONSET (4) [NOT USED]
response_time: not used
response: not used
result: not used

BLOCK_ONSET (5) [NOT USED]
response_time: not used
response: not used
result: not used

TRIAL_ONSET (6)
response_time: not used
response: not used
result: flags (<ANX|RISK|NONE>_<VIRTUAL-SHOCK|SHOCK|NO-SHOCK>_<NEUT|NO-NEUT> = (<2|1|0>_<2|1|0>_<1|0>))

STIM_ONSET (7)
response_time: not used
response: not used
result: stimulus image path

RATING_ONSET (8)
response_time: not used
response: 'ANX' or 'RISK' for rating type
result: starting marker position

RATING_CHANGE (9)
response_time: not used
response: direction moved (left or right)
result: new marker position

FINAL_RATING (10)
response_time: not used
response: 'select' if a selection was made or 'NA' if no selection was made
result: final marker position

PAUSE_ONSET (11) [NOTE: post rating blank screen pause]
response_time: not used
response: not used
result: not used

SHOCK_ONSET (12)
response_time: not used
response: shock duration or 'NA' if not a real shock
result: 'NA' or 'virtual' if not a real shock

OUTLINE_ONSET (13) [NOTE: This is marks when the red outline boxes the screen]
response_time: not used
response: not used
result: not used

TAP_SOON (14) [NOTE: This is marks when the tap soon screen appears]
response_time: not used
response: not used
result: not used

TAP_ONSET (15) [NOTE: This marks when recorded tapping begins]
response_time: not used
response: Tap Average recording for session
result: not used

TAPS (16) [NOTE: One mark for each tap during the tap now section of a trial]
response_time: not used
response: not used
result: Current tap count for the trial

FIXATION_ONSET (17)
response_time: not used
response: not used
result: fixation duration

ERROR_TAPS (18)
response_time: not used
response: not used
result: tap count in context where taps are not needed/allowed

CHAR_POS (19)
response_time: not used
response: not used
result: character position on screen ~(-1.0 to +1.0) (left to right on screen)

SHIELD_SIZE (20)
response_time: not used
response: not used
result: Percentage representing shield size/strength displayed - int((shield_opacity/(max_shield=0.8))*100)

SCORE_CHANGE (21)
response_time: not used
response: Amount added
result: Total score
```