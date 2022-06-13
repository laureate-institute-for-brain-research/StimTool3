# README for the Driving Task (Move-and-Go and Speed-Stop)

Goal of the task is to try and stop the car before the stop sign using a joystick

# *TRIAL STRUCTURE*

```
      [         instructions         ] ->
      ^                              ^
INSTRUCT_ONSET                   TASK_ONSET


Move-and-Go Trials
                           MOTION_ONSET  RESPONSE_PERIOD_ONSET
                                 v           v
[count down timer] -> [delay] -> [motion] -> [response period] ->
^  ^                  ^    ^                  ^ ^ ^          ^
BEEP           DELAY_ONSET FALSE_START       STICK_X        MOTION_RESPONSE_END
                                             STICK_Y
						               CAR_VELOCITY_AND_POSITION
                                       
                                       
                                       
Speed-Stop Trials
                                          RESPONSE_PERIOD_ONSET
                                                  v
[count down timer] -> [period before response] -> [response period] ->
^  ^           ^ ^                                ^  ^  ^
BEEP        BEEP FALSE_START                      STICK_X
                                                  STICK_Y
                                            CAR_VELOCITY_AND_POSITION

												 
Break
        [break] ->
        ^     ^
BREAK_ONSET BREAK_END

```
*INPUT DETAILS****

EACH LINE CODES: one block
COLUMN 1: trial type (0->move_go_instruct, 1->move_go, 2->speed_stop_instruct, 3->speed_stop, 4->break)
COLUMN 2: not used
COLUMN 3: number of trials in this block
COLUMN 4: not used
TRIAL ORDER IS: randomized


# *OUTPUT DETAILS*
In the output files, there are events that corresponds to a number.
See below for the explanation of each events.

## INSTRUCT_ONSET (1)
* response_time: not used
* response: not used
* result: not used

## TASK_ONSET (2)
* response_time: time between INSTRUCT_ONSET and TASK_ONSET
* response: not used
* result: not used

## BEEP (3)
* response_time: not used
* response: not used
* result: 0 for first two beeps, 1 for start (third) beep

## DELAY_ONSET (4)
* response_time: not used
* response: not used
* result: not used

## FALSE_START (5)
* response_time: time between FALSE_START and DELAY_ONSET (for Move-and-Go)or NA (for Speed-Stop)
* response: not used
* result: not used

## MOTION_ONSET (6)
* response_time: not used
* response: not used
* result: motion speed (in cm/s)

## RESPONSE_PERIOD_ONSET (7)
* response_time: time between MOTION_START and RESPONSE_PERIOD_START for move-go trials or time between third BEEP and RESPONSE_PERIOD_START for speed-and-stop trials
* response: not used
* result: car movement before response in cm (current car position +8, since it starts each trial at -8)

## CAR_POSITION_AND_VELOCITY (8)
* response_time: time between first response and CAR_VELOCITY_AND_POSITION
* response: car position (in cm)
* result: car velocity (in cm/s, calculated from STICK_Y and car position)

## STICK_X (9)
* response_time: time between first response and STICK_X
* response: stick X position [-1(left) to 1(right)]
* result: not used

## STICK_Y (10)
* response_time: time between first response and STICK_Y
* response: stick Y position [-1(pull) to 1(push)]
* result: not used

## MOTION_RESPONSE_END (11)
* response_time: time between MOTION_RESPONSE and MOVE_RESPONSE_END
* response: not used
* result: not used

## BREAK_ONSET (12)
* response_time: not used
* response: not used
* result: not used

## BREAK_END (13)
* response_time: time between BREAK_END and BREAK_ONSET
* response: not used
* result: not used


