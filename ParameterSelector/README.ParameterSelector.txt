README for the Rest task

*****************************************************************SUMMARY**************************************************************************

This "task" is a way to select parameters for a session, e.g. visit number in a study that has many visits (which would make selecting from a huge number of schedules difficult).

*****************************************************************TRIAL STRUCTURE******************************************************************

NA


*****************************************************************INPUT DETAILS********************************************************************

This task uses a somewhat different input format.
Each line in a .schedule file specifies a dropdown in the form of a dictionary.
Each key in that dictionary is an option in the dropdown, and each value is another dictionary, containing a set of session_parameters to set.


*****************************************************************OUTPUT DETAILS*******************************************************************

RESPONSE (1)
response_time: time the dialogue box was up before it was answered
response: response entered into the box
result: actual question text used

TASK_END (99)
response_time: not used
response: not used
result: not used


