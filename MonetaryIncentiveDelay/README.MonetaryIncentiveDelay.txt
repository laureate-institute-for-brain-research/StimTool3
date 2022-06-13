README for the Monitary Incentive Delay Task

*****************************************************************SUMMARY**************************************************************************

Each trial begins with a cue indicating the amount of money that can be won or lost.
After that cue, there is a variable delay (2.25-3s) followed by the brief presentation of a target.
The target is presented for somewhere around 250ms, and this period is adjusted based on subject reaction times.
Specifically, the win rate for each of the six conditions is used separately and if it is greater than 66%, the target duration is decreased by 20ms and if it is less than 66%, the target duration is increased by 20ms.
If the subject presses the response button during the target (but not during the delay period immediately before the target), then the amount signalled by the cue will be won on gain trials and not lost on loss trials.
If the subject misses the target, then the amount will not be earned on gain trials and will be lost on loss trials.

*****************************************************************TRIAL STRUCTURE******************************************************************

      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET

    2s             2s                2s                  2s          2-6s
[Cue Shown] -> [Delay] -> [Delay - Target - blank] -> [Result] -> [Fixation]
^              ^                   ^     ^                        ^
CUE_ONSET    DELAY_ONSET TARGET_ONSET TARGET_OFFSET     FIXATION_ONSET
                          ^           ^          ^    ^
                          ----RESPONSE_PRESSED----   RESULT_ONSET
                                                     TOTAL_REWARD
						   


*****************************************************************INPUT DETAILS********************************************************************

EACH LINE CODES: one trial
COLUMN 1: trial type (codes below)
COLUMN 2: not used
COLUMN 3: variable delay before target onset (uniformly distributed between 0.25 and 1), length of variable ITI (2,4, or 6s with an average of 4s)
COLUMN 4: not used
TRIAL ORDER IS: fixed

TARGET_ONSET will have ideal delay as result

TRIAL TYPE:
0: -$0 condition
1: -$1 condition
2: -$5 condition
3: +$0 condition
4: +$1 condition
5: +$5 condition

Durations has two space separated values.

The first is the variable delay before target onset.  
These values range from 0.25 to 1 and are sampled from 0.25 + Uniform(0,0.75)

The second value is the length of the variable ITI, which is 2, 4, or 6 seconds with an average of 4s.
*****************************************************************OUTPUT DETAILS*******************************************************************
TRIAL TYPE:
0: -$0 condition
1: -$1 condition
2: -$5 condition
3: +$0 condition
4: +$1 condition
5: +$5 condition

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

DELAY_ONSET (4)
response_time: not used
response: not used
result: not used

TARGET_ONSET (5)
response_time: not used
response: not used
result: indicates ideal target duration

RESPONSE_PRESSED (6)
When the first response for a trial is recorded.  This can be anytime between the start of the variable portion of the delay (2s after the start of the delay, lasting 0.25 to 0.75s) and when the result is shown.  
response_time: either time elapsed since TARGET_ONSET, or -1 for early response
response: always 1
result: 0 for miss, 1 for hit

TARGET_OFFSET (7)
when the target disappears.  
response_time: not used
response: not used
result: is the actual duration of target presentation, which should be ~result of TARGET_ONSET

RESULT_ONSET (8)
when the result message is shown.
response_time: not used
response: not used
result: the message that was shown ($0, +$0, +$1, +5, -$0 -$1, -$5)

TOTAL_REWARD (9)
the total reward accumulated so far
response_time: not used
response: not used
result: total reward accumulated so far

FIXATION_ONSET (10)
when the variable iti begins
response_time: not used
response: not used
result: not used