README for the Stop Signal Task

*****************************************************************SUMMARY**************************************************************************

This presents subjects with a series of either X or O stimuli.
The subject is to press the left button whenever an X appears and the right button when an O appears.
Some trials have a tone presented at some offset before the subject's mean reaction time.
This tone is a "stop signal", and the subject should not press either button in trials where it appears.

Prior to scanning, the subject does a practice run containing of four different blocks.
These blocks are designed to get an estimate of the subject's mean reaction time (MRT).
The first block contains no tones--MRT is computed and used in the second block.
The second block contains distractor tones but the instructions are to ignore them--MRT is computed and used in the third block.
The third block contains stop signal (SS) tones and the instructions are to skip responses when tones are presented--MRT is computed and used in the fourth block.
The fourth block contains SS tones and the instructions are to skip responses when tones are presented--MRT is computed and used in the scanner.
During the MRT workup procedure, MRT is computed using only go trials.

*****************************************************************TRIAL STRUCTURE******************************************************************

      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET

            1.3s          .2s        
         RESPONSE TRIAL_END  
            v  v  v
        [cue shown] -> [blank iti] ->  
        ^  ^           
CUE_ONSET STOP_SIGNAL      

        7.8s               .2s
[instruction slide] -> [blank iti] ->
^
INSTRUCT

*****************************************************************INPUT DETAILS********************************************************************

EACH LINE CODES: one trial
COLUMN 1: Trial type coded as follows: tens digit is 9->instruct slide, 1..6->stop signal at 0..500ms before MRT, ones digit: 0..2->instruct slide to show or 0->X/left, 1>O/right, negative values are used to indicate SS trials where the subject is instructed to ignore the tone.
COLUMN 2: not used
COLUMN 3: Duration of the trial (1.5 for response trials, 8 or 12 for instruct trials
COLUMN 4: not used
TRIAL ORDER IS: fixed

SCHEDULE FILES (and trial types for output files)
#tens digit: 9 codes instruct slide, 0 for go, 1..6 for tone at 0..500ms prior to average reaction time
#ones digit: 0..2 codes instruct slides or 0->X (left), 1->O (right)

*****************************************************************OUTPUT DETAILS*******************************************************************

INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

CUE_ONSET (3)
response_time: not used
response: not used
result: not used

STOP_SIGNAL (4)
response_time: difference between STOP_SIGNAL and CUE_ONSET
response: not used
result: 1 if the red stimulus was drawn, 0 otherwise (this happens when the subject responds before the stop signal)

RESPONSE (5)
response_time: difference between RESPONSE and CUE_ONSET
response: 0 or 1 for left or right side
result: 0 for incorrect side, 1 for correct side

TRIAL_END (6)
response_time: difference between first RESPONSE and CUE_ONSET, or NA for no response
response: 0 or 1 for left or right, NA for no response
result: 1 is good, 2 is failed to stop but correct side, 3 wrong side on go trial, 4 is wrong side and failed to stop, 5 is failed to go on go trial

INSTRUCT (7)
response_time: Average RTs for previous block--used as average RT for next block in practice and final average from practice is used for scanning
response: not used
result: 0..2 for which slide is shown
