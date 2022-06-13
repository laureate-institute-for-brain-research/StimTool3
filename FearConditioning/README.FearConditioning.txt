README for the Fear Conditioning Task

*****************************************************************SUMMARY**************************************************************************

This task presents subjects with either an arrow or a fractal.
When an arrow is presented, the task is to press the button corresponding to the arrow's direction as quickly as possible (right or left).
No response is required during trials where a fractal is presented.
Two different fractals are presented: one is the CS+ and the other is the CS- (counterbalanced across subjects).
Sometimes there is an aversive scream presented during the CS+.

There is a simple volume workup procedure that's presented before the runs in the scanner.
A rating scale is shown with one location used to play a 400ms white noise sound and the other locations used to rate the intensity of that sound.
The subject is instructed to continue to play and rate the sound as many times as necessary.
The volume starts at 10% and increases by 10% increments until the subject rates the intensity at 8 or higher. (possibly change this scheme at some point)

There is also a practice run that takes place outside the scanner and does not contain any aversive stimuli.

Three runs take place during scanning.
The first two runs contain the US and are used for fear acquisition.
The third run does not contain any US presentations and is used for extinction.
After (each run?) subjects are asked to rate how unhappy/happy, calm/excited, and anxious each of the two fractals make them feel.

*****************************************************************TRIAL STRUCTURE******************************************************************

      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET

Volume Workup
                                               RATING >= 8
[ set volume ] -> [play sound or make rating] -------------> [save and quit]
^                  ^            SOUND         |            |
|                  |<--------------------------            |
|                            RATING < 8                    |
|<----------------------------------------------------------
				   
				   


Arrow Trial

  0.3s       2.5s       0.2s
[blank] -> [arrow] -> [blank] ->
           ^   ^
   ARROW_ONSET RESPONSE

Fractal Trial

 0.3s       1.5s       0.2s
[blank] -> [image] -> [blank] ->
           ^   ^
 IMAGE_ONSET  US
 
 
 Post Ratings
         [       rating        ]
         ^                     ^
 VALENCE_RATING_ONSET     VALENCE_RATING_RESPONSE
 AROUSAL_RATING_ONSET     AROUSAL_RATING_RESPONSE
 ANXIETY_RATING_ONSET     ANXIETY_RATING_RESPONSE
 
*****************************************************************INPUT DETAILS********************************************************************

EACH LINE CODES: one trial
COLUMN 1: Trial type (0->left arrow, 1->right arrow, 2->CS-, 3->CS+, 4->CS+&US, 5->4s blank for lead in/lead out)
COLUMN 2: not used
COLUMN 3: not used
COLUMN 4: not used
TRIAL ORDER IS: fixed


*****************************************************************OUTPUT DETAILS*******************************************************************

Trial Types:
-1: rating
0: left arrow
1: right arrow
2: CS-
3: CS+
4: CS+ & US
5: 4s of blank--only used for lead in and lead out

INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

ARROW_ONSET (3)
response_time: not used
response: not used
result: not used

RESPONSE (4)
response_time: ARROW_ONSET and RESPONSE
response: 0 or 1 for left or right, 2 if they press the 'response' button
result: 0 or 1 for incorrect or correct, NA if they press the 'response' button--and the box is not shown

IMAGE_ONSET (5)
response_time: not used
response: not used
result: not used

US (6)
response_time: not used
response: not used
result: not used

SOUND (7)
response_time: time between the start of [play sound or make rating] and the sound
response: not used
result: sound intensity (0 to 1)

RATING (8)
response_time:time between the start of [play sound or make rating] and the sound
response: rating (1 to 10)
result: sound intensity

VALENCE_RATING_ONSET (9)
response time: not used
response: not used
result: 0 for CS-, 1 for CS+

VALENCE_RATING_RESPONSE (10)
response time: time since VALENCE_RATING_ONSET
response: rating from 1 to 5
result: 0 for CS-, 1 for CS+

AROUSAL_RATING_ONSET (11)
response time: not used
response: not used
result: 0 for CS-, 1 for CS+

AROUSAL_RATING_RESPONSE (12)
response time: time since AROUSAL_RATING_ONSET
response: rating from 1 to 5
result: 0 for CS-, 1 for CS+

ANXIETY_RATING_ONSET (13)
response time: not used
response: not used
result: 0 for CS-, 1 for CS+

ANXIETY_RATING_RESPONSE (14)
response time: time since ANXIETY_RATING_ONSET
response: rating from 1 to 5
result: 0 for CS-, 1 for CS+