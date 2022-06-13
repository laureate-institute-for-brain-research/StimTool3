# README for the Slider Task


# **SUMMARY**

Subjects are presented with a quiestion and slider.
They must respond to the question using 3 buttons. A left,right and select button.




# **TRIAL STRUCTURE**
```
[         instructions         ] ->
^                              ^
INSTRUCT_ONSET                 TASK_ONSET

[ show question ]
^
RESPONSE

```

# **INPUT DETAILS**

```
EACH LINE CODES: one trial
COLUMN 1: Question Type
COLUMN 2: Question
COLUMN 3: Sub Text
COLUMN 4: Audio Path 
COLUMN 5: Number of Choices
COLUMN 6: Ticks Position

TRIAL ORDER IS: fixed
```

# **OUTPUT DETAILS**

```
INSTRUCT_ONSET (0)
response_time: not used
response: not used
result: not used




RESPONSE (1)
response_time: time since when question is displayed
response: marker position
result: question text

```