

*****************************************************************SUMMARY**************************************************************************

This task is a bit of a combination between Hamed's Cue Reactivity task and Rajita Sinha's Alcohol/Stress reactivity task.
There are 3 conditions: Neutral, Drug(opioid), and Stress (negative IAPS images).
Each run is ~11 minutes and contains 4 blocks of images of the same type, with ratings after each block.




*****************************************************************TRIAL STRUCTURE******************************************************************

      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET



for image trials (occurring in blocks of 6) or fixations
		5s for stimuli, 8-12 or 31s for fixation		       		 0.2s 			
            	[            image                        ]                       ->    [blank]     ->           
      		^	    ^	         ^                                              ^
            IMAGE_ONSET	BOX_ONSET	BOX_RESPONSE			            BLANK_ONSET   
	


for rating trials, which occur in blocks of 4
            [     rating       question    shown      ]           ->
            ^              ^ ^ ^                ^     ^
      RATING_ONSET      RATING_CHANGE     RATING_LOCK FINAL_RATING



*****************************************************************INPUT DETAILS********************************************************************

EACH LINE CODES: one trial
COLUMN 1: Trial type (see below for a list of trial types)
COLUMN 2: Image to show
COLUMN 3: trial duration
COLUMN 4: not used
TRIAL ORDER: fixed

Schedule files are named:

      study-PASO_condition-[opioid|neutral|stress]_set-[1|2|3|4]

Schedule files are selected based on subject ID (ending in a 3 digit number) and visit
      subject ID mod 24 -> image set order (which set to display at which visit)
            0  -> 1234
            1  -> 1243
            2  -> 1324
            3  -> 1342
            4  -> 1423
            5  -> 1432
            6  -> 2134
            7  -> 2143
            8  -> 2314
            9  -> 2341
            10 -> 2413
            11 -> 2431
            12 -> 3124
            13 -> 3142
            14 -> 3214
            15 -> 3241
            16 -> 3412
            17 -> 3421
            18 -> 4123
            19 -> 4132
            20 -> 4213
            21 -> 4231
            22 -> 4312
            23 -> 4321
      subject ID mod 6 -> run order (which order to present images in during a visit)
            0  -> NOS
            1  -> NSO
            2  -> ONS
            3  -> OSN
            4  -> SNO
            5  -> SON

So, for example, for AA534:
      534 mod 24 = 6 -> 2134
            visit 1 will use image set 2
            visit 2 will use image set 1
            visit 3 will use image set 3
            visit 4 will use image set 4
      534 mod 6 = 0 -> NOS
            run 1 will have neutral images
            run 2 will have opioid images
            run 3 will have stress images

a file with run parameters is output for easy verification that things are working correctly, and to check to be sure things are balanced well-ish between participants
id		[subject ID]
id_mod_24	[number]
set_order	[4 digit order from above mapping]
id_mod_6	[number]
condition_order	[3 character order from above mapping]
visit		[V1|V2|V3|V4]
run		[1|2|3]
schedule_file	[schedule file selected/used based on above]

TRIAL TYPES:

000 -> fixation

011 -> neutral object
012 -> neutral object with hand
013 -> neutral tools
014 -> neutral tools with hands, simple
015 -> neutral tools with hands, complex
016 -> neutral tools with faces

021 -> opioid
022 -> opioid and hand
023 -> opioid instruments
024 -> opioid instruments and hands
025 -> opioid injection and hands
026 -> opioid activities and faces

note that stressful images, since they come from IAPS, do not have the same categories as the neutral/opioid images
030 -> stress


change the leading 0 to a 8 to indicate it is a box trial, where the subject should press a button to remove a border from the image 
For example:
810 -> valence rating after a neutral object

change the leading 0 to a 1..4 to indicate a valence/arousal/stress/desire rating
For example:
100 -> valence rating after fixation
200 -> arousal rating after fixation
300 -> stress rating after fixation 
400 -> urge rating after fixation

999 -> relaxation audio trial



*****************************************************************OUTPUT DETAILS*******************************************************************

INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

IMAGE_ONSET (3)
response_time: not used
response: not used
result: image shown

BOX_ONSET (4)
response_time: not used
response: not used
result: not used

BOX_RESPONSE (5)
response_time: time between BOX_ONSET and BOX_RESPONSE, or NA for no response
response: which button was pressed, or NA if no response
result: 0 for no response, 1 for first response in a box trial, 2 otherwise (i.e. for extra responses, button presses on non-box trials)

RATING_ONSET (6)
response_time: not used
response: not used
result: image shown, should have text for a question with 4 possible responses

RATING_CHANGE (7)
response_time: not used
response: not used
result: image shown, should have text for a question with 4 possible responses

RATING_LOCK (8)
response_time: not used
response: not used
result: image shown, should have text for a question with 4 possible responses

FINAL_RATING (9)
response_time: time between RATING_ONSET and RATING_LOCK, or NA if the subject never locked in a rating
response: selection chosen, from 1-9, or NA for no response
result: not used, or NA for no response

RELAXATION_ONSET (10)
response_time: not used
response: not used
result: audio file played



