
import time
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui, sound, constants
from psychopy.hardware import keyboard
import numpy
import json
from labjack import ljm

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.clock = None #global clock used for timing
        self.output = None #The output file
        self.msg = None
        self.ideal_trial_start = None #ideal time the current trial started
        self.trial = None #trial number
        self.trial_type = None #trial type
        self.calc_refresh_rate = 0.0166667 # default at 60hz, we calculate this in run_try() though
        self.response_duration = 3.0
        self.feedback_duration = 1.0
        self.rating_duration = 5.0
        self.test_iti = 0.25
        self.person_dict = {}
        self.name_stims = []
        self.first_trial = True
        self.first_fix_dur = 15 #seconds
        self.img_num_map = {'6':'20','5':'30','4':'40','3':'60','2':'70','1':'80'}

event_types = {
    'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'TRIAL_ONSET':3,
    'IMAGE_ONSET':4,
    'FIXATION':5,
    'RESPONSE':6,
    'ACCURACY':7,
    'FEEDBACK':8,
    'RATING_ONSET':9,
    'RATING_CHANGE':10,
    'RATING_SELECTION':11,
    'TASK_END':StimToolLib.TASK_END 
    }

# DRAW FUNCTIONS FOR TASK PHASES
def draw_fixation_phase():
    g.fixation.draw()
    # g.question_text.draw()

def draw_rating_question_phase():
    g.rating_text.draw()

def draw_rating_phase(change):
    g.rating_text.draw()
    if change is not None:
        if change == -1:
            g.slider.markerPos = g.slider.markerPos - 1
            if g.slider.markerPos < g.slider.ticks[0]:
                g.slider.markerPos = g.slider.ticks[0]
        elif change == 1:
            g.slider.markerPos = g.slider.markerPos + 1
            if g.slider.markerPos > g.slider.ticks[-1]:
                g.slider.markerPos = g.slider.ticks[-1]
    g.slider.draw()

def draw_response_phase(left_img,right_img,selection=None):
    g.fixation.draw()
    left_img.draw()
    right_img.draw()
    if selection is not None:
        #draw selection circle
        if selection == 'left':
            g.left_select.draw()
        else:
            g.right_select.draw()

def draw_feedback_phase(accuracy,feedback):
    if accuracy == 999:
        g.no_response.draw()
    elif accuracy == int(feedback):
        g.reward.draw()
    elif accuracy != int(feedback):
        g.zero.draw()

def do_one_trial(trial_type, left_img, right_img, iti_dur, isi_dur, feedback):

    # DEV - SKIP RATINGS FOR NOW
    if trial_type == 'RATING':
        # g.win.flip()
        return
    
    delay_flag = False
    left_num = trial_type.split('_')[0]
    right_num = trial_type.split('_')[1]
    
    # person = g.person_dict[trial_type.split("_")[0]]
    # name_stim = g.name_stims.pop(0)
    # left_img.pos = [-0.5,0]
    # right_img.pos = [0.5,0]

    # if g.first_trial:
    #     g.first_trial = False
    #     g.fixation.draw()
    #     g.win.flip()
    #     mark_time = g.clock.getTime()
    #     # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #     StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['FIXATION'], mark_time, 'NA', 'NA', g.first_fix_dur, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #     for x in range(int(round(g.first_fix_dur/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the fixation and draws the person selection
    #         if event.getKeys(["escape"]):
    #             raise StimToolLib.QuitException()
    #         g.fixation.draw()
    #         g.win.flip()

    # mark_time = g.clock.getTime()
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    # ____ DRAW IMAGES AND CHECK FOR SELECTION ____
    selection = None
    accuracy = 999
    draw_response_phase(left_img, right_img, selection)
    g.win.flip()
    mark_time = g.clock.getTime()
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['TRIAL_ONSET'], mark_time, 'NA', f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', f'{feedback}', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['IMAGE_ONSET'], mark_time, 'NA', f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', f'{left_img.image} {right_img.image}', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.clearEvents()
    for x in range(int(round(g.response_duration/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the person selections and draws the delay phase
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys([g.session_params['left'], g.session_params['right']], timeStamped=g.clock)
        if resp and selection is None:
            if resp[0][0] == g.session_params['left']:
                selection = 'left'
                if left_num < right_num:
                    accuracy = 1
                else:
                    accuracy = 0
                StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['RESPONSE'], resp[0][1], resp[0][1] - mark_time, 'left', left_img.image, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['ACCURACY'], resp[0][1], resp[0][1] - mark_time, 'left', accuracy, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[0][0] == g.session_params['right']:
                selection = 'right'
                if right_num < left_num:
                    accuracy = 1
                else:
                    accuracy = 0
                StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['RESPONSE'], resp[0][1], resp[0][1] - mark_time, 'right', right_img.image, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['ACCURACY'], resp[0][1], resp[0][1] - mark_time, 'right', accuracy, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        draw_response_phase(left_img, right_img, selection)
        g.win.flip()

    # # ____ ISI ____
    # g.fixation.draw()
    # g.win.flip()
    # mark_time = g.clock.getTime()
    # # StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['FIXATION'], mark_time, 'NA', 'NA', isi_dur, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # for x in range(int(round(isi_dur/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the fixation and draws the person selection
    #     if event.getKeys(["escape"]):
    #         raise StimToolLib.QuitException()
    #     g.fixation.draw()
    #     g.win.flip()

    # ____ FEEDBACK ____
    # draw_feedback_phase(name_stim,feedback,yes_selected,no_selected)
    draw_feedback_phase(accuracy,feedback)
    g.win.flip()
    mark_time = g.clock.getTime()
    if accuracy == 999:
        feedback_mark = 'no response'
    elif accuracy == int(feedback):
        feedback_mark = 'reward'
    elif accuracy != int(feedback):
        feedback_mark = 'zero'
    StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['FEEDBACK'], mark_time, 'NA', f'{feedback}_{accuracy}', feedback_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    for x in range(int(round(g.feedback_duration/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the feedback phase and starts next trial
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        # draw_feedback_phase(name_stim,feedback,yes_selected,no_selectd)
        draw_feedback_phase(accuracy,feedback)
        g.win.flip()

    # ____ END TRIAL AND ITI ____
    g.fixation.draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    # StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['FIXATION'], mark_time, 'NA', 'NA', iti_dur, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    for x in range(int(round(iti_dur/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the fixation and draws the person selection
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        g.fixation.draw()
        g.win.flip()

def do_one_test_trial(trial_type, left_img, right_img, iti_dur, isi_dur, feedback):
    
    delay_flag = False
    left_num = trial_type.split('_')[0]
    right_num = trial_type.split('_')[1]

    # ____ DRAW IMAGES AND CHECK FOR SELECTION ____
    selection = None
    accuracy = 999
    draw_response_phase(left_img, right_img, selection)
    g.win.flip()
    mark_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['TRIAL_ONSET'], mark_time, 'NA', trial_type, f'{feedback}', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['IMAGE_ONSET'], mark_time, 'NA', trial_type, f'{left_img.image} {right_img.image}', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.clearEvents()
    for x in range(int(round(g.response_duration/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the person selections and draws the delay phase
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys([g.session_params['left'], g.session_params['right']], timeStamped=g.clock)
        if resp and selection is None:
            if resp[0][0] == g.session_params['left']:
                selection = 'left'
                if left_num < right_num:
                    accuracy = 1
                else:
                    accuracy = 0
                StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['RESPONSE'], resp[0][1], resp[0][1] - mark_time, 'left', f'{left_img.image}', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['ACCURACY'], resp[0][1], resp[0][1] - mark_time, 'left', accuracy, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[0][0] == g.session_params['right']:
                selection = 'right'
                if right_num < left_num:
                    accuracy = 1
                else:
                    accuracy = 0
                StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['RESPONSE'], resp[0][1], resp[0][1] - mark_time, 'right', f'{right_img.image}', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['ACCURACY'], resp[0][1], resp[0][1] - mark_time, 'right', accuracy, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            # draw_response_phase(left_img, right_img, selection)
            # g.win.flip()
            # break # break loop at response
        draw_response_phase(left_img, right_img, selection)
        g.win.flip()

    if selection is None:
        # ____ FEEDBACK ____
        draw_feedback_phase(accuracy,feedback)
        g.win.flip()
        mark_time = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['FEEDBACK'], mark_time, 'NA', 'NA', 'no_response', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        for x in range(int(round(g.feedback_duration/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the feedback phase and starts next trial
            if event.getKeys(["escape"]):
                raise StimToolLib.QuitException()
            draw_feedback_phase(accuracy,feedback)
            g.win.flip()

    # ____ END TRIAL AND ITI ____
    g.fixation.draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    # StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, f'{g.img_num_map[left_num]}_{g.img_num_map[right_num]}', event_types['FIXATION'], mark_time, 'NA', 'NA', iti_dur, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    for x in range(int(round(g.test_iti/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the fixation and draws the person selection
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        g.fixation.draw()
        g.win.flip()

def do_one_happy_rating_trial(trial_type):
    # ____ DRAW HAPPY RATING QUESTION ____
    change = None
    selected = False
    # draw_response_phase(left_img, right_img, selection)
    g.happy_slider.marker.fillColor = 'red'
    g.happy_slider.markerPos = 50 # default mid start
    g.happy_text.draw()
    g.happy_slider.draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    resp_time = None
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_ONSET'], mark_time, 'NA', 'NA', '50', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.kb.clearEvents()
    for x in range(int(round(g.response_duration/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = g.kb.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']], waitRelease = False, clear=False)
        if resp and not selected and resp[-1].duration is None:
            if resp[-1].name == g.session_params['left']:
                change = -1
                # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[-1].name == g.session_params['right']:
                change = 1
                # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[-1].name == g.session_params['select']:
                selected = True
                g.happy_slider.marker.fillColor = 'yellow'
                resp_time = g.clock.getTime() - mark_time
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_SELECTION'], g.clock.getTime(), resp_time, 'NA', g.happy_slider.markerPos, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        if change is not None:
            if change == -1:
                g.happy_slider.markerPos = g.happy_slider.markerPos - 1
                if g.happy_slider.markerPos < g.happy_slider.ticks[0]:
                    g.happy_slider.markerPos = g.happy_slider.ticks[0]
            elif change == 1:
                g.happy_slider.markerPos = g.happy_slider.markerPos + 1
                if g.happy_slider.markerPos > g.happy_slider.ticks[-1]:
                    g.happy_slider.markerPos = g.happy_slider.ticks[-1]
            resp = None
            change = None
        g.happy_text.draw()
        g.happy_slider.draw()
        g.win.flip()
    # g.win.flip()
    # g.win.flip() # get back on stable flips

    # # 0.5 sec of yellow
    # g.fixation.draw()
    # g.win.flip()
    # mark_time = g.clock.getTime()
    # # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION'], mark_time, 'NA', 'NA', '1.0', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # for x in range(int(round(0.5/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the fixation and draws the person selection
    #     if event.getKeys(["escape"]):
    #         raise StimToolLib.QuitException()
    #     g.fixation.draw()
    #     g.win.flip()

    # 0.5 sec of fixation
    g.fixation.draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION'], mark_time, 'NA', 'NA', '0.5', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    for x in range(int(round(0.25/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the fixation and draws the person selection
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        g.fixation.draw()
        g.win.flip()

def do_one_rating_trial(trial_type, left_img, right_img, iti_dur, isi_dur, feedback):

    selected = False
    g.valence_rating_slide.draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['INSTRUCT_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    while not selected: # stop one refresh early so that the following refresh clears the person selections and draws the delay phase
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys([g.session_params['right']], timeStamped=g.clock)
        if resp and not selected:
            if resp[0][0] == g.session_params['right']:
                selected = True
    # a few extra flips to get back on track since the timing for this phase is not strict
    g.win.flip()
    g.win.flip()

    # ____ SHOW REWARD ____
    g.reward.draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION'], mark_time, 'NA', 'NA', '2', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    for x in range(int(round(2.0/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the feedback phase and starts next trial
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        g.reward.draw()
        g.win.flip()

    # ____ DRAW FIRST VALENCE RATING QUESTION ____
    rating = 2
    selected = False
    # draw_response_phase(left_img, right_img, selection)
    g.valence_rating_text.draw()
    g.valence_rate.draw()
    g.selection_boxes[rating].draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_ONSET'], mark_time, 'NA', 'NA', rating, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.clearEvents()
    while not selected: # stop one refresh early so that the following refresh clears the person selections and draws the delay phase
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']], timeStamped=g.clock)
        if resp and not selected:
            if resp[0][0] == g.session_params['left']:
                rating = rating - 1
                if rating < 0:
                    rating = 0
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[0][0] == g.session_params['right']:
                rating = rating + 1
                if rating > 4:
                    rating = 4
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[0][0] == g.session_params['select']:
                selected = True
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_SELECTION'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.valence_rating_text.draw()
        g.valence_rate.draw()
        g.selection_boxes[rating].draw()
        g.win.flip()
    # a few extra flips to get back on track since the timing for this phase is not strict
    g.win.flip()
    g.win.flip()

    # ____ SHOW ZERO ____
    g.zero.draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION'], mark_time, 'NA', 'NA', '2', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    for x in range(int(round(2.0/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the feedback phase and starts next trial
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        g.zero.draw()
        g.win.flip()

    # ____ DRAW SECOND VALENCE RATING QUESTION ____
    rating = 2
    selected = False
    # draw_response_phase(left_img, right_img, selection)
    g.valence_rating_text.draw()
    g.valence_rate.draw()
    g.selection_boxes[rating].draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_ONSET'], mark_time, 'NA', 'NA', rating, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.clearEvents()
    while not selected: # stop one refresh early so that the following refresh clears the person selections and draws the delay phase
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']], timeStamped=g.clock)
        if resp and not selected:
            if resp[0][0] == g.session_params['left']:
                rating = rating - 1
                if rating < 0:
                    rating = 0
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[0][0] == g.session_params['right']:
                rating = rating + 1
                if rating > 4:
                    rating = 4
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[0][0] == g.session_params['select']:
                selected = True
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_SELECTION'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.valence_rating_text.draw()
        g.valence_rate.draw()
        g.selection_boxes[rating].draw()
        g.win.flip()
    # a few extra flips to get back on track since the timing for this phase is not strict
    g.win.flip()
    g.win.flip()

    selected = False
    g.arousal_rating_slide.draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['INSTRUCT_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    while not selected: # stop one refresh early so that the following refresh clears the person selections and draws the delay phase
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys([g.session_params['right']], timeStamped=g.clock)
        if resp and not selected:
            if resp[0][0] == g.session_params['right']:
                selected = True
    # a few extra flips to get back on track since the timing for this phase is not strict
    g.win.flip()
    g.win.flip()

    # ____ SHOW REWARD ____
    g.reward.draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION'], mark_time, 'NA', 'NA', '2', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    for x in range(int(round(2.0/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the feedback phase and starts next trial
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        g.reward.draw()
        g.win.flip()

    # ____ DRAW FIRST AROUSAL RATING QUESTION ____
    rating = 2
    selected = False
    # draw_response_phase(left_img, right_img, selection)
    g.arousal_rating_text.draw()
    g.arousal_rate.draw()
    g.selection_boxes[rating].draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_ONSET'], mark_time, 'NA', 'NA', rating, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.clearEvents()
    while not selected: # stop one refresh early so that the following refresh clears the person selections and draws the delay phase
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']], timeStamped=g.clock)
        if resp and not selected:
            if resp[0][0] == g.session_params['left']:
                rating = rating - 1
                if rating < 0:
                    rating = 0
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[0][0] == g.session_params['right']:
                rating = rating + 1
                if rating > 4:
                    rating = 4
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[0][0] == g.session_params['select']:
                selected = True
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_SELECTION'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.arousal_rating_text.draw()
        g.arousal_rate.draw()
        g.selection_boxes[rating].draw()
        g.win.flip()
    # a few extra flips to get back on track since the timing for this phase is not strict
    g.win.flip()
    g.win.flip()

    # ____ SHOW ZERO ____
    g.zero.draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION'], mark_time, 'NA', 'NA', '2', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    for x in range(int(round(2.0/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the feedback phase and starts next trial
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        g.zero.draw()
        g.win.flip()

    # ____ DRAW SECOND VALENCE RATING QUESTION ____
    rating = 2
    selected = False
    # draw_response_phase(left_img, right_img, selection)
    g.arousal_rating_text.draw()
    g.arousal_rate.draw()
    g.selection_boxes[rating].draw()
    g.win.flip()
    mark_time = g.clock.getTime()
    # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], mark_time, 'NA', 'NA', trial_type, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_ONSET'], mark_time, 'NA', 'NA', rating, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.clearEvents()
    while not selected: # stop one refresh early so that the following refresh clears the person selections and draws the delay phase
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']], timeStamped=g.clock)
        if resp and not selected:
            if resp[0][0] == g.session_params['left']:
                rating = rating - 1
                if rating < 0:
                    rating = 0
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[0][0] == g.session_params['right']:
                rating = rating + 1
                if rating > 4:
                    rating = 4
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            elif resp[0][0] == g.session_params['select']:
                selected = True
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_SELECTION'], resp[0][1], resp[0][1] - mark_time, 'NA', (rating + 1), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.arousal_rating_text.draw()
        g.arousal_rate.draw()
        g.selection_boxes[rating].draw()
        g.win.flip()
    # a few extra flips to get back on track since the timing for this phase is not strict
    g.win.flip()
    g.win.flip()

def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/SET.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status
    
def run_try():    
    
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="RME")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1 #the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]

    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)

    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    StimToolLib.general_setup(g)
    g.win.flip()
    g.win.flip()

    trial_types,images,durations,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    left_imgs = images[0]
    right_imgs = images[1]
    iti_durs = durations[0]
    isi_durs = durations[1]
    feedbacks = junk[0]

    StimToolLib.redirect_output(g.session_params)

    #set up MAIN stimuli
    g.win_ratio = g.win.size[0]/g.win.size[1]
    for stim in left_imgs:
        stim.units = 'norm'
        stim.pos = [-0.5,0]
        stim.size = [0.5, g.win_ratio*0.5]
    for stim in right_imgs:
        stim.units = 'norm'
        stim.pos = [0.5,0]
        stim.size = [0.5, g.win_ratio*0.5]
    g.fixation = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/fixation.png'), pos=[0,0], size = [0.25, g.win_ratio*0.25], units='norm')
    g.arousal_rating_slide = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide13.JPG'), pos=[0,0], size = [1, g.win_ratio*1], units='norm')
    g.valence_rating_slide = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide11.JPG'), pos=[0,0], size = [1, g.win_ratio*1], units='norm')
    g.reward = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/reward.bmp'), pos=[0,0], size = [1, g.win_ratio*1], units='norm')
    g.zero = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/zero.bmp'), pos=[0,0], size = [1, g.win_ratio*1], units='norm')
    g.left_select = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/selection.bmp'), pos=[-0.5,0], size = [0.8, g.win_ratio*0.8], units='norm')
    g.right_select = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/selection.bmp'), pos=[0.5,0], size = [0.8, g.win_ratio*0.8], units='norm')
    g.no_response = visual.TextStim(g.win, text='No Response Detected!', height=0.15, pos=[0,0], units='norm', color='red')
    g.yes = visual.TextStim(g.win, text='Yes', height=0.15, pos=[-0.5,-0.5], units='norm', color='white')
    g.no = visual.TextStim(g.win, text='No', height=0.15, pos=[0.5,-0.5], units='norm', color='white')
    # feedback_image = visual.ImageStim(g.win, units = 'norm', size = [1,1], pos = [0,0], image = 'media/reward.bmp')
    g.rating_text = visual.TextStim(g.win, text = 'How Do You Feel Right Now?', pos = [0,0.25], height = 0.18, wrapWidth = 35, color = 'white')
    g.valence_rate = visual.ImageStim(g.win, units = 'cm', size = [22.44,6.42], pos = [0,-7.0], image = os.path.join(os.path.dirname(__file__), 'media/valence2.bmp'))
    g.arousal_rate = visual.ImageStim(g.win, units = 'cm', size = [22.44,6.42], pos = [0,-7.0], image = os.path.join(os.path.dirname(__file__), 'media/arousal2.bmp'))
    g.b0_choice = visual.Rect(g.win, units = 'cm', width = 3.5, height = 6.2, lineColor = 'ForestGreen', lineWidth = 4.0, pos = [-9.4,-7.0])
    g.b1_choice = visual.Rect(g.win, units = 'cm', width = 3.5, height = 6.2, lineColor = 'ForestGreen', lineWidth = 4.0, pos = [-4.8,-7.0])
    g.b2_choice = visual.Rect(g.win, units = 'cm', width = 3.5, height = 6.2, lineColor = 'ForestGreen', lineWidth = 4.0, pos = [-0.2,-7.0])
    g.b3_choice = visual.Rect(g.win, units = 'cm', width = 3.5, height = 6.2, lineColor = 'ForestGreen', lineWidth = 4.0, pos = [4.4,-7.0])
    g.b4_choice = visual.Rect(g.win, units = 'cm', width = 3.5, height = 6.2, lineColor = 'ForestGreen', lineWidth = 4.0, pos = [8.9,-7.0])
    g.selection_boxes = [g.b0_choice,g.b1_choice,g.b2_choice,g.b3_choice,g.b4_choice]

    # set up RATING stimuli
    g.valence_rating_text = visual.TextStim(g.win, text='How PLEASANT or UNPLEASANT did you find that outcome?', height=0.1, pos=[0,0.75], units='norm', color='white')
    g.arousal_rating_text = visual.TextStim(g.win, text='How AROUSING did you find that outcome?', height=0.1, pos=[0,0.75], units='norm', color='white')
    g.happy_text = visual.TextStim(g.win, text='How happy are you?', height=0.1, pos=[0,0.75], units='norm', color='white')
    # g.slider = visual.Slider(g.win, ticks=[0,1,2,3,4,5,6,7,8,9,10], labels=['very bad','very good'], labelHeight = 0.1, pos = (0,0), size = (1.6,0.01), units = 'norm')
    g.slider = visual.Slider(g.win, ticks=[0,1,2,3,4,5,6,7,8,9,10], labels=['very bad','very good'], pos = (0,0), units = 'norm')
    g.happy_slider = visual.Slider(g.win, ticks=range(0,101), labelHeight=0.1, labels=['not happy at all','very happy'], pos = (0,0), units = 'norm', size = (1.6,0.01))
    # g.slider.marker.size = 0.1
    g.slider.markerPos = 5 # default mid start
    g.happy_slider.markerPos = 50 # default mid start
    g.slider.status = constants.STARTED
    g.slider.responseClock = g.clock # use our clock
    g.happy_slider.status = constants.STARTED
    g.happy_slider.responseClock = g.clock # use our clock
    g.blank = visual.Rect(g.win, pos=(0,0), fillColor='black', size = [2,2])

    start_time = data.getDateStr()
    fileName = os.path.join(g.prefix + '.csv')
    
    g.output = open(fileName, 'w')

    g.mouse = event.Mouse(visible=False)
    g.kb = keyboard.Keyboard()

    # options = [0.5,1.0,1.5]
    # for x in range(60):
    #     print(f'{random.sample(options,1).pop()} {random.sample(options,1).pop()}')

    g.calc_refresh_rate = g.win.getMsPerFrame()[2]/1000 # grab the median ms per frame and convert to seconds
    print(f'refresh rate is: {g.calc_refresh_rate}')
    g.win.flip()
    g.slider.draw() # initialize this... 
    g.blank.draw()
    g.win.flip()
    g.win.flip()
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.N_BACK_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)

    g.trial = 0
    if g.session_params['scan'] == 'True':
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    # g.win.recordFrameIntervals = True # set this so that we can check for dropped frames in the code
    # g.win.refreshThreshold = g.calc_refresh_rate*1.5
    # g.win.flip()
    # g.win.flip()
    # g.win.flip() # These flips initialize the g.win.frameIntervals list. We use it for checking dropped frames.
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.ideal_trial_start = instruct_end_time

    g.mouse = event.Mouse(visible=False)
    g.mouse.setVisible(0)

    for t,li,ri,itid,isid,f in zip(trial_types,left_imgs,right_imgs,iti_durs,isi_durs,feedbacks):
        g.trial_type = t

        if t == 'RATING':
            do_one_rating_trial(t,li,ri,itid,isid,f)
        elif t == 'HAPPY':
            do_one_happy_rating_trial(t)
        elif 'TEST' in g.run_params['run']:
            do_one_test_trial(t,li,ri,itid,isid,f)
        else:
            do_one_trial(t,li,ri,itid,isid,f)

        g.trial = g.trial + 1

    # g.thanks.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 10)
    g.msg.setColor([-1,-1,-1])
