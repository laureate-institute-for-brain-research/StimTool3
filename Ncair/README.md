# README for the NCAIR Task

## SUMMARY

This task presents subjects with various types of media (images, videos and audio).
Followed by 3 questions asking about cultural identity, their valence and their arousal.

## TRIAL STRUCTURE
```
      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET


|<--------------------------------------total trial duration ---------------------------------------->|
                                    
                                        -- Audio Trial Type  --
[       stimulus	     ] -> [ identity ques ] -> [ valence ques ] -> [ arousal ques ] -> [ fixation ]
|  ~ duration of audio   |    |     5s        |    |     5s       |    |     5s       |    |~ variable|
^ AUDIO_ONSET                 ^ RATING_ONSET       ^ RATING_ONSET      ^ RATING_ONSET      ^FIXATION_ONSET         
^ TRIAL_ONSET
      ^DIAL_RESPONSE                              
                              | response      |    | response   |      | response   |     
                              ^ RATING_DIAL_RESPONSE
                                    ^ RATING_DIAL_LOCKED


                                        -- Video Trial Type  --
[       stimulus	     ] -> [ identity ques ] -> [ valence ques ] -> [ arousal ques ] -> [ fixation ]
|  ~ duration of video   |    |     5s        |    |     5s       |    |     5s       |    |~ variable|
^ VIDEO_ONSET                 ^ RATING_ONSET       ^ RATING_ONSET      ^ RATING_ONSET      ^FIXATION_ONSET         
^ TRIAL_ONSET
      ^DIAL_RESPONSE                              
                              | response      |    | response   |      | response   |
                              ^ RATING_DIAL_RESPONSE
                                          ^ RATING_DIAL_LOCKED

                                        -- Image Trial Type  --
[          4 images      ] -> [ identity ques ] -> [ valence ques ] -> [ arousal ques ] -> [ fixation ]
|6s| |6s| |6s| |6s|      |    |     5s        |    |     5s       |    |     5s       |    |~ variable|
^ IMAGE_ONSET                 ^ RATING_ONSET       ^ RATING_ONSET      ^ RATING_ONSET      ^FIXATION_ONSET         
     ^ IMAGE_ONSET
          ^ IMAGE_ONSET
               ^ IMAGE_ONSET
^ TRIAL_ONSET                          
                              | response      |    | response   |      | response   |
                              ^ RATING_BUTTON_RESPONSE
                                  

```


## INPUT DETAILS 
```
EACH LINE CODES: one trial
COLUMN 1: TrialTypes X_X X[0] -> Cultural|Comparator|Rating_Dial|Rating_Button|Fixation (0|1|2|3|4); X[1]:Stimuli Type 0-> Audio;1-> Video; 2-> Picture; 3->Rating_Identity; 4-> Rating_Valence; 5-> Rating_Arousalj; 6-> Fixation
COLUMN 2: not used
COLUMN 3: Duration
COLUMN 4: med path
TRIAL ORDER IS: fixed
```

## OUTPUT DETAILS

Trial Types Decoding

2 numbers concactenaed by '_' underscore ie. 1_2

### first number:
 - 0: Cultural
 - 1: Comparator
 - 2: Rating Dial
 - 3: Rating Button

### 2nd number (media type):
 - 0: Audio
 - 1: Video
 - 2: Image
 - 3: Rating - Identity Question
 - 4: Rating - Valence Question
 - 5: Rating - Arousal Question
 - 6: Fxation Trial


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

AUDIO_ONSET (5)
response_time: not used
response: the duration of the audio
result: the file path of the audio used

VIDEO_ONSET (6)
response_time: not used
response: the duration of the video
result: the file path of the video used

IMAGE_ONSET (7)
response_time: not used
response: the duration of the image
result: the file path of the image used

DIAL_RESPONSE (8)
response_time: time between STIM_ONSET and RESPONSE
response: t or b. rotated right/rotated left
result: 0 - 100

RATING_ONSET (9)
response_time: not used
response: not used
result: the question

RATING_BUTTON_RESPONSE (10)
response_time: time between RATING_ONSET and RATING_BUTTON_RESPONSE
response: 1/2/3
result: rating

RATING_DIAL_RESPONSE (11)
response_time: time between RATING_ONSET and RATING_DIAL_RESPONSE
response: t or b. rotated right/ rotated left
result: rating

RATING_DIAL_LOCKED (12)
response_time: time between RATING_ONSET and RATING_DIAL_RESPONSE
response: g. rotated right/ rotated left
result: rating
```