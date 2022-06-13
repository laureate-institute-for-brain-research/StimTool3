README for the Fear Conditioning Task

*****************************************************************SUMMARY**************************************************************************

The neurosociometer measures the participant's response to social evaluation.
In it, a video is shown that is believed to be another participant evaluating the one completing the task.
Trials consist of 10, 11, 12, or 13 second video clips, with adjective selection occurring 7-8s into the clip.
During the task, participants can rate how they feel--to decide, add persistent rating selection to the bottom of the screen?

*****************************************************************TRIAL STRUCTURE******************************************************************

      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET

                    10-13s                                  
   [         adjective trial             ] ->                   
   ^                     ^                                      
TRIAL_ONSET         AJECTIVE_SELECTION
               ^     ^     ^    
              RATING_RESPONSE   

 

*****************************************************************INPUT DETAILS********************************************************************

EACH LINE CODES: one trial/instruct/fixation
COLUMN 1: Trial type (0->neutral, 1->positive, -1->negative)
COLUMN 2: top image, left image, right image
COLUMN 3: time in video when selection is made
COLUMN 4: adjective selected, video to play
TRIAL ORDER IS: fixed


*****************************************************************OUTPUT DETAILS*******************************************************************

Trial Types:
0->neutral
1->positive
-1->negative

INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

TRIAL_ONSET (3)
response_time: video clip duration
response: not used
result: video clip shown

ADJECTIVE_SELECTION (4)
response_time: not used
response: not used
result: adjective selected

RATING_RESPONSE (5)
response_time: time between previous ADJECTIVE_SELECTION and this RATING_RESPONSE
response: 1=Very Bad, 2=Bad, 3=Good, 4=Very Good
result: adjective selected for previous ADJECTIVE_SELECTION



