README for the Bandit Task

*****************************************************************SUMMARY**************************************************************************

This task presents subjects with a series of slot machine games.  
Each game uses fixed probabilities for each machine, but these probabilities change between games.
Subjects are given a set of coins at the beginning of each game and allocate them one at a time.
The outcome for each trial is either positive or negative, depicted using a sound and either a green or red coin.
Subjects are instructed to use any strategy they can to acquire the most points (green coins).

*****************************************************************TRIAL STRUCTURE******************************************************************

      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET


[                 block                      ]  -> ... -> [final result]
^                                                         ^            ^
BLOCK_ONSET                               FINAL_RESULT_ONSET   FINAL_RESULT_OFFSET

 [trial] -> [trial]  -> ... ->  [game result] ->
                                ^           ^
                  BLOCK_RESULT_ONSET   BLOCK_RESULT_OFFSET


   [     trial     ] ->
   ^           ^       
TRIAL_ONSET  SELECTION  

*****************************************************************INPUT DETAILS********************************************************************

EACH LINE CODES: one block
COLUMN 1: number of trials for this block (always 16 here)
COLUMN 2: not used
COLUMN 3: three floats in the range [0,1] specifying the probabilities for the three lottos
COLUMN 4: not used
TRIAL ORDER IS: randomized

RANDOMIZATION SCHEME:
The trial order is shuffled for each subject, but the placement of the three lotteries remains fixed within each trial.


	
*****************************************************************OUTPUT DETAILS*******************************************************************

The end of a trial is always SELECTION time + ~0.25s because of the time that the border is highlighted
Trial type is the three probabilities separated by dashes (e.g. 0.6661-0.1447-0.7227)	

INSTRUCT_ONSET (1)
response_time: not used
response: not used
result: not used

TASK_ONSET (2)
response_time: time between INSTRUCT_ONSET and TASK_ONSET
response: not used
result: not used

BLOCK_ONSET (3)
response_time: not used
response: not used
result: not used

TRIAL_ONSET (4)
response_time: not used
response: not used
result: not used
		
SELECTION (5)
response_time: time between TRIAL_ONSET and selection
response: lotto selected (1, 2, or 3)
result: 0 or 1 for loss or win (result is shown 0.25s after SELECTION)

BLOCK_RESULT_ONSET (6)
reponse_time: not used
response: not used
result: points earned this game

BLOCK_RESULT_OFFSET (7)
response_time: difference between GAME_RESULT_OFFSET and GAME_RESULT_ONSET 
respone: not used
result: not used

FINAL_RESULT_ONSET (8)
response_time: time between BLOCK_ONSET and FINAL_RESULT_0NSET (time this block took to complete)
response: not used
result: amount earned ($5 or $10)

FINAL_RESULT_OFFSET (9)
response_time: time between FINAL_RESULT_OFFSET and FINAL_RESULT_ONSET
response: not used
result: total points earned 
