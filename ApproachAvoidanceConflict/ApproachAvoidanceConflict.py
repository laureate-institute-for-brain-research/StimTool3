
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from psychopy import prefs
import StimToolLib, os, random, operator
from psychopy import visual, event, core, data, gui, sound
from psychopy.hardware import joystick


import time
from psychopy.visual.secondorder import EnvelopeGrating


class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.clock = None #global clock used for timing
        self.x = None #+ fixation stimulus
        self.output = None #The output file
        self.msg = None
        self.ideal_trial_start = None #ideal time the current trial started
        self.this_trial_output = '' #will contain the text output to #print for the current trial
        self.left_av_runway = None #runway images with aversive stimuli on the left or right
        self.right_av_runway = None
        #self.resk = None
        self.fig = None #figure images
        self.fig_select = None
        self.fig_center = [0,0.06]
        self.fig_select_center = [0,0.06]
        self.bars_low = []
        self.bars_mid = []#red bars indicating points: [0] will be left, [1] will be right
        self.bars_high = []
        self.move_distance = 0.132 #number of normalized units between locations (distance to move for selection)
        self.select_length = 4 #amount of time subject has to make a decision
        self.image_length = 4 #duration the image stimulus is displayed for each trial 6
        self.total_reward = 0 #total number of points the subject has earned and will be paid
        self.total_reward_shown=0 #total that waill be displayed to subject
        self.result_length = 2 #duration of result screen (you got ___ pts, total pts) 2
        self.small_reward = None #sounds to play for small and large rewards
        self.big_reward = None
        self.instructions = ['''Now you are going to have a chance to practice the task.''']
        self.trial = 0 #the trial number we are currently on, used for recording events
        self.trial_type = None #the trial type string to be printed out
        self.title = 'Approach Avoidance Conflict'
        self.total_trials = 30
        self.run_order = False # Intialize the the run_order variable



event_types = {'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'FIXATION_ONSET':3, 
    'DECISION_ONSET':4, 
    'SELECTOR_MOVEMENT':5, 
    'FINAL_LOCATION':6, 
    'OUTCOME_SIDE':7, 
    'NEGATIVE_OUTCOME_SHOWN':8, 
    'POSITIVE_OUTCOME_SHOWN':9, 
    'POINTS_AWARDED':10,
    'TOTAL_POINTS':11,
    'VAS_RATING':12, 
    'POST_RATING':13,
    'RIGHT_MAX':14,
    'LEFT_MAX':15,
    'TASK_END':StimToolLib.TASK_END}


def draw_bars(bars_to_draw):
    for b in bars_to_draw:
        b.draw()
        
        
def joystick_select(trial_type, left_reward, right_reward, start_location, iti, current_location, response_recorded, selected, this_runway, bars_to_draw, decision_onset,init_button_value):
    #now = g.clock.getTime()
    #print(now)
    event.clearEvents()
    if not selected:
        sensitivity = .02 #the higher this value the more sensitive the joystick will be to hand movement
        response_recorded = True
        this_runway.draw()
        draw_bars(bars_to_draw)
        now=g.clock.getTime()
        joystick_pos = g.joystick.getX()
        #print(joystick_pos)
        j_mark=joystick_pos

        # print(g.joystick.getAllAxes()) 
        
        #non-pivot method
        if abs(joystick_pos) < 0.220: #tolerance to remove joystick spring offset in 0 position (without this figure will appear to move on its own)
            joystick_pos = 0
        current_location=current_location + (joystick_pos * sensitivity)
    
        #pivot method
        #current_location=(joystick_pos * 4)
        
        if current_location >= 4: # constrain max rightward position at 4
            current_location = 4
        elif current_location <= -4: # constrain max leftward position at -4
            current_location = -4
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SELECTOR_MOVEMENT'], now, now - decision_onset, str(joystick_pos) + ' (' + str(j_mark) + ')' , str(current_location) , None, None)
        g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
        g.fig.draw() 
        
        button_value=g.joystick.getButton(g.session_params['joy_forward'])
        if button_value:
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_LOCATION'], now, now - decision_onset, 'locked', current_location, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.fig_select.pos = [g.fig_select_center[0] + g.move_distance * current_location, g.fig_select_center[1]]
            selected = True
            g.fig_select.draw()
        
        event.clearEvents() #clear event buffer so that it doesn't get clogged
        g.win.flip()
        
        #now=g.clock.getTime()
        #StimToolLib.just_wait(g.clock,now+0.02)       
    return current_location, selected


def key_select(trial_type, left_reward, right_reward, start_location, iti, current_location, response_recorded, selected, this_runway, bars_to_draw, decision_onset):
    key = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']]) #get any response keys pressed (just left, right, select)
    if key and not selected:
        if len(key) > 1:
            #print 'MULTIPLE KEYS.  SHOULD NOT HAPPEN'
            #print key
            pass
        if not response_recorded: #record time of first button press
            pass
        response_recorded = True
        this_runway.draw()
        draw_bars(bars_to_draw)
        now = g.clock.getTime()
        if key[0] == g.session_params['left'] and current_location > -4:#move selction left unless at end
            current_location = current_location - 1
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SELECTOR_MOVEMENT'], now, now - decision_onset, -1, current_location, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
            g.fig.draw()
        elif key[0] == g.session_params['right'] and current_location < 4: #move selection right unless at end 
            current_location = current_location + 1
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SELECTOR_MOVEMENT'], now, now - decision_onset, 1, current_location, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
            g.fig.draw()
        elif key[0] == g.session_params['select']: #lock in response_recorded
            print('HERE')
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_LOCATION'], now, now - decision_onset, 'not locked', current_location, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.fig_select.pos = [g.fig_select_center[0] + g.move_distance * current_location, g.fig_select_center[1]]
            selected = True
            g.fig_select.draw()
        else: #should only happen when the figure is at one end or the other
            g.fig.draw()
        g.win.flip()
    return current_location, selected

def selection_period(trial_type, left_reward, right_reward, start_location, iti):
    #handle period where the subject can make a selection
    this_runway = None
    if trial_type == '0 1': #right aversive
        this_runway = g.runway_0_1
    if trial_type == '1 0': #left aversive
        this_runway = g.runway_1_0
    if trial_type == '0 0': #no aversive
        this_runway = g.runway_0_0 
    if trial_type == '1 1': #both aversive
        this_runway = g.runway_1_1
    
    
    bars_to_draw = [] #the point bar(s) to draw
    if left_reward == 2:
        bars_to_draw.append(g.bars_low[0])
    if left_reward == 4:
        bars_to_draw.append(g.bars_mid[0])
    if left_reward == 6:
        bars_to_draw.append(g.bars_high[0])
    if right_reward == 2:
        bars_to_draw.append(g.bars_low[1])
    if right_reward == 4:
        bars_to_draw.append(g.bars_mid[1])
    if right_reward == 6:
        bars_to_draw.append(g.bars_high[1])
        
    # Clear Any Joystick Events
    event.clearEvents()

    response_recorded = False
    selected = False #set to true when the subject locks in a response
    current_location = start_location #can be any integer from -4 to 4
    g.fig.pos = [g.fig_center[0] + g.move_distance * current_location, g.fig_center[1]]
    this_runway.draw()
    draw_bars(bars_to_draw)
    g.fig.draw()
    g.win.flip()
    if g.session_params['joystick']:
        init_button_value=g.joystick.getButton(g.session_params['joy_forward'])
    decision_onset = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['DECISION_ONSET'], decision_onset, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['down']]) #clear response keys that may have been pressed already
    while g.clock.getTime() < g.ideal_trial_start + g.select_length + iti:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException
        
        if g.session_params['joystick']:
            current_location, selected = joystick_select(trial_type, left_reward, right_reward, start_location, iti, current_location, response_recorded, selected, this_runway, bars_to_draw, decision_onset, init_button_value)
        else:
            current_location, selected=key_select(trial_type, left_reward, right_reward, start_location, iti, current_location, response_recorded, selected, this_runway, bars_to_draw, decision_onset)
            
    if not selected:
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_LOCATION'], g.clock.getTime(), 'NA', 'NA', current_location, False, g.session_params['parallel_port_address'])    
    return current_location
    
def select_result_display_image(final_location, left_sound, right_sound, left_image, right_image, trial_type):
    #based on the final location, pick which image to display
    #return 0 for left, 1 for right
    probability_right = (final_location + 5) / float(10)
    if random.random() < probability_right: #show the image on the right
        #g.this_trial_output = g.this_trial_output + ',R' screen_x 1920
        right_image.size = [g.session_params['screen_x'], g.session_params['screen_y']]
        right_image.draw()
        g.win.flip()
        right_sound.play()
        retval = 1
        now = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['OUTCOME_SIDE'], now, -1, 'NA', 1, False, g.session_params['parallel_port_address'])
        stim_shown = right_image._imName + ' ' + right_sound.fileName
        if trial_type[2] == '0': #positive on right
            g.this_trial_output = g.this_trial_output + ',0'
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['POSITIVE_OUTCOME_SHOWN'], now, 'NA', 'NA', stim_shown, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        else: 
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['NEGATIVE_OUTCOME_SHOWN'], now, 'NA', 'NA', stim_shown, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            #g.this_trial_output = g.this_trial_output + ',1'
    else: #show the image on the left
        #g.this_trial_output = g.this_trial_output + ',L'
        left_image.size = [g.session_params['screen_x'], g.session_params['screen_y']]
        left_image.draw()
        g.win.flip()
        left_sound.play()
        retval = 0
        now=g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['OUTCOME_SIDE'], now, 'NA', 'NA', -1, False, g.session_params['parallel_port_address'])
        stim_shown = left_image._imName + ' ' + left_sound.fileName
        if trial_type[0] == '0': #positive on left
            g.this_trial_output = g.this_trial_output + ',0'
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['POSITIVE_OUTCOME_SHOWN'], now, 'NA', 'NA', stim_shown, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        else: 
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['NEGATIVE_OUTCOME_SHOWN'], now, 'NA', 'NA', stim_shown, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    return retval
    
def show_reward(left_reward, right_reward, result, left_image, right_image):
    if result == 0:
        reward_amount = left_reward
        left_image.draw()
    else:
        reward_amount = right_reward
        right_image.draw()
    g.reward_text_1.setText('YOU MADE ' + str(int(reward_amount)) + ' CENTS')
    
    #print('g.total_reward:', str(g.total_reward))
    #print('reward_amount:',str(reward_amount))
    g.total_reward = g.total_reward + reward_amount
    g.total_reward_shown = g.total_reward_shown + reward_amount
    StimToolLib.write_var_to_file(g.subj_param_file, 'total_reward', g.total_reward)
    StimToolLib.write_var_to_file(g.subj_param_file, 'total_reward_shown', g.total_reward_shown)
    g.reward_text_2.setText('TOTAL: ' + str(int(g.total_reward_shown)))
    
    g.reward_rect.draw()
    
    g.reward_text_1.draw()
    g.reward_text_2.draw()
    g.win.flip()
    #to_play.play()
    #time_stamp()
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['POINTS_AWARDED'], now, 'NA', 'NA', reward_amount, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TOTAL_POINTS'], now, 'NA', 'NA', g.total_reward, False, g.session_params['parallel_port_address'])
    #g.this_trial_output = g.this_trial_output + ',' + str(int(reward_amount)) + ',' + str(int(g.total_reward))

    
def do_one_trial(trial_type, iti, left_reward, right_reward, start_location, left_sound, right_sound, left_image, right_image):
    #wait for iti
    g.x.draw()
    g.win.flip()
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION_ONSET'], now, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.x.draw()

    # Why is code below here?
    
    # if g.joystick.getButton(g.session_params['joy_forward']):
    #     g.joystick = joystick.Joystick(0) 
        #print str(g.clock.getTime()-now)
        #print '-----------------'
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + iti)
    #g.offset=g.joystick.getX()*-1
    #show runway
    final_location = selection_period(trial_type, left_reward, right_reward, start_location, iti)
    #show image
    result = select_result_display_image(final_location, left_sound, right_sound, left_image, right_image, trial_type)
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + iti + g.select_length + g.image_length)
    #show reward points/play sound
    show_reward(left_reward, right_reward, result, left_image, right_image)
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + iti + g.select_length + g.image_length + g.result_length)
    left_sound.stop()
    right_sound.stop()
    g.ideal_trial_start = g.ideal_trial_start + iti + g.select_length + g.image_length + g.result_length #update current time for next trial
    ##print outcome
    g.this_trial_output = g.this_trial_output + '\n'
 

def load_sounds(sound_files):
    directory = os.path.dirname(__file__)
    left_sounds = []
    right_sounds = []
    for i in range(len(sound_files[0])):
        left_sounds.append(sound.Sound(value=os.path.join(directory,sound_files[0][i]),volume=g.volume))
        right_sounds.append(sound.Sound(value=os.path.join(directory,sound_files[1][i]),volume=g.volume))
    return left_sounds, right_sounds
    
def final_screen():
    #g.final_sound.play()
    # if g.total_reward==g.total_reward_shown:
    #     g.msg.setText('Congratulations, you\'ve won $' + "{0:.2f}".format(g.total_reward/100) + '!')
    # else:
    #     g.msg.setText('Congratulations, you\'ve won $' + "{0:.2f}".format(g.total_reward/100) +'!\n(This includes your winnings from the trials you repeated.')
    # g.msg.draw()
    # g.msg.setText('\n\n\n\n\n\nPress the trigger button to continue.')
    # g.msg.draw()
    g.msgtop = visual.TextStim(g.win, text = '', units = 'norm', pos=(0,0), color = 'black', alignHoriz='center', font = 'helvetica')
    g.msgmid = visual.TextStim(g.win, text = '', units = 'norm', pos=(0,-.2), color = 'black', alignHoriz='center', font = 'helvetica')
    g.msgbottom = visual.TextStim(g.win, text = '', units = 'norm', pos=(0,-0.9), color = 'black', alignHoriz='center', font = 'helvetica')
    
    g.win.flip()
    if g.session_params['joystick']:
        while not g.joystick.getButton(g.session_params['joy_forward']):
            if g.total_reward==g.total_reward_shown:
                g.msgtop.setText('Congratulations, you\'ve won $' + "{0:.2f}".format(g.total_reward/100) + '!')
            else:
                g.msgtop.setText('Congratulations, you\'ve won $' + "{0:.2f}".format(g.total_reward/100) +'!')
                g.msgmid.setText('(This includes your winnings from the trials you repeated.)')
                #g.msgmid.pos = StimToolLib.getMSGPosition(g.msgmid, xonly = True)
                g.msgmid.draw()
        
            #g.msgtop.pos = StimToolLib.getMSGPosition(g.msgtop, xonly = True)
            g.msgtop.draw()
            g.msgbottom.setText('Press the trigger button to continue.')
            #g.msgbottom.pos = StimToolLib.getMSGPosition(g.msgbottom, xonly = True)
            g.msgbottom.draw()
            event.clearEvents('joystick')
            g.win.flip()
        g.msg.setPos([0,0])
    else:
        
        if g.total_reward==g.total_reward_shown:
            g.msgtop.setText('Congratulations, you\'ve won $' + "{0:.2f}".format(g.total_reward/100) + '!')
        else:
            g.msgtop.setText('Congratulations, you\'ve won $' + "{0:.2f}".format(g.total_reward/100) +'!')
            g.msgmid.setText('(This includes your winnings from the trials you repeated.)')
            #g.msgmid.pos = StimToolLib.getMSGPosition(g.msgmid, xonly = True)
            g.msgmid.draw()
                 #g.msgtop.pos = StimToolLib.getMSGPosition(g.msgtop, xonly = True)
        g.msgtop.draw()
        g.msgbottom.setText('Press the ENTER to continue.')
        #g.msgbottom.pos = StimToolLib.getMSGPosition(g.msgbottom, xonly = True)
        g.msgbottom.draw()
        g.win.flip()
        k = event.waitKeys(keyList = ['return', 'escape'])
        if k[0] == 'escape':
            raise QuitException()
        
    #g.final_sound.stop() #stop the sound if it's still playing
    #StimToolLib.just_wait(g.clock, g.ideal_trial_start + 30)

def get_vas_ratings():
    g.mouse.setVisible(1)
    top_text = visual.TextStim(g.win, text="Please rate how you feel", units='norm', height=0.1, color='black', pos=[0,0.7], wrapWidth=int(1.5))
    
    text_1 = visual.TextStim(g.win, text="PLEASANT", units='norm', height=0.05, color='black', pos=[0,0.33], wrapWidth=int(1600))
    scale_1 = visual.RatingScale(g.win, lineColor='Black', marker=visual.TextStim(g.win, text='l', units='norm', color='black'), precision=1, low=0, 
        high=100, textColor='Black', markerStart=50, scale=None, labels=['not at all', 'extremely'], tickMarks=[0,100], showValue=False, pos=(0,0.4), showAccept=False, acceptKeys='z')
    
    text_2 = visual.TextStim(g.win, text="UNPLEASANT", units='norm', height=0.05, color='black', pos=[0,-0.07], wrapWidth=int(1600))
    scale_2 = visual.RatingScale(g.win, lineColor='Black', marker=visual.TextStim(g.win, text='l', units='norm', color='black'), precision=1, low=0, 
        high=100, textColor='Black', markerStart=50, scale=None, labels=['not at all', 'extremely'], tickMarks=[0,100], showValue=False, pos=(0,0), showAccept=False, acceptKeys='z')
    
    text_3 = visual.TextStim(g.win, text="INTENSE", units='norm', height=0.05, color='black', pos=[0,-0.47], wrapWidth=int(1600))
    scale_3 = visual.RatingScale(g.win, lineColor='Black', marker=visual.TextStim(g.win, text='l', units='norm', color='black'), precision=1, low=0, 
        high=100, textColor='Black', markerStart=50, scale=None, labels=['not at all', 'extremely'], tickMarks=[0,100], showValue=False, pos=(0,-0.4), showAccept=False, acceptKeys='z')
    bot_text = visual.TextStim(g.win, text="Press enter when done", units='pix', height=50, color='black', pos=[0,-450], wrapWidth=int(1600))
    vas_start_time = g.clock.getTime()
    while True:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        if event.getKeys(["return"]):
            break
        #item.draw()
        text_1.draw()
        text_2.draw()
        text_3.draw()
        scale_1.draw()
        scale_2.draw()
        scale_3.draw()
        top_text.draw()
        bot_text.draw()
        g.win.flip()
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, -1, 'NA', event_types['VAS_RATING'], now, now - vas_start_time, str(scale_1.getRating()), 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, -2, 'NA', event_types['VAS_RATING'], now, now - vas_start_time, str(scale_2.getRating()), 'NA', False, g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, -3, 'NA', event_types['VAS_RATING'], now, now - vas_start_time, str(scale_3.getRating()), 'NA', False, g.session_params['parallel_port_address'])
    g.mouse.setVisible(0)
    
    
def get_post_ratings():
    
    msg=['''
The following are questions about the task you just completed related to gaining money and/or seeing negative
    or neutral pictures.  For each question, use the mouse to select the response that best describes your
                                                          opinion regarding the task.''']
    text = visual.TextStim(g.win, text=msg, units='norm', height=0.1, color='black', pos=[0,0], wrapWidth=int(1.5))
    g.mouse.setVisible(1)
    response_labels = ('      1\nNot at all', '2\n', '    3\nA little', '4\n', '       5\nQuite a bit', '6\n', '        7\nVery much')
    questions = open(os.path.join(os.path.dirname(__file__),'T1000_AAC_PostQuestions.csv'))
    i = -1 #index of current question
    for line in questions:
        resp,end_time,resp_time = StimToolLib.get_one_rating(line, response_labels, g.win, g.clock)
        StimToolLib.mark_event(g.output, i, 'NA', event_types['POST_RATING'], end_time, resp_time, resp, line.rstrip(), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        i = i - 1
    if int(resp) > 1:
        resp,end_time,resp_time = StimToolLib.get_text_response('Please describe (type) any other strategies used to manage emotions triggered by negative pictures.  Press enter when done.', g.win, g.clock)
        StimToolLib.mark_event(g.output, i, 'NA', event_types['POST_RATING'], end_time, resp_time, resp, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #r = StimToolLib.get_one_rating("When a NEGATIVE picture and sound were displayed, I tried to think about something unrelateed to the picture to distract myself:", response_labels, g.win)
    
def track_run():
    g.final_run=False
    if g.run_params['practice']: return 0
    if 'RX_A' in g.run_params['run']: return 1
    if 'RX_B' in g.run_params['run']: return 2
    if 'RX_C' in g.run_params['run']:
        g.final_run=True
        return 3
    return 0 # default

    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/AAC.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status

def get_schedule_file():
    # Get Schedule File
    # Return schedule path
    try:
        run_order = StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'run_order')
        g.run_order = run_order.split(',')
    except:
        print("error getting run_order. this is probably practice")
        pass
    
    # Find RX_ letter in the run
    if 'RX_A' in g.run_params['run']:
        # Return the first run in the order
        try:
            new_schedule_file = g.run_params['run'].replace('RX_A', 'RX_'+g.run_order[0])
        except:
            print("ERROR!! Not using the order form params file")
            return os.path.join(os.path.dirname(__file__), g.run_params['run'])

        return os.path.join(os.path.dirname(__file__), new_schedule_file)
    
    if 'RX_B' in g.run_params['run']:
        # Return the second run in the order
        try:
            new_schedule_file = g.run_params['run'].replace('RX_B', 'RX_'+g.run_order[1])
        except:
            print("ERROR!! Not using the order form params file")
            return os.path.join(os.path.dirname(__file__), g.run_params['run'])
        return os.path.join(os.path.dirname(__file__), new_schedule_file)

    if 'RX_C' in g.run_params['run']:
        # Return the third run in the order
        try:
            new_schedule_file = g.run_params['run'].replace('RX_C', 'RX_'+g.run_order[2])
        except:
            print("ERROR!! Not using the order form params file")
            return os.path.join(os.path.dirname(__file__), g.run_params['run'])
        return os.path.join(os.path.dirname(__file__), new_schedule_file)

    # if we get to here just return the correct corresponding run
    return os.path.join(os.path.dirname(__file__), g.run_params['run'])
    

def run_try():  
    #joystick.backend='pygame'
    #prefs.hardware['audioLib'] = ['pyo', 'pygame']
    # don't have the 'u' before the elements, that seems to break joystick functionality. I don't know why??
    #prefs.hardware['audioDriver'] = ['ASIO4ALL', 'ASIO','Audigy']
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="AAC")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            #print 'QUIT!'
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)

    g.prefix = StimToolLib.generate_prefix(g)
    g.subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '_' + g.run_params['param_file'])
    
    
    #Randomize order of AAC runs in task list (optional, ie if randomizer.schedule is not included in task list AAC runs will run normally in the order they are listed)
    #Randomizer.schedule must be run seperately (ie in a practice or setup task list) before the actual task list for changes to take effect
    # New Method of randomizing
    # Still uses the same random function, but writes the order of the runs to the params file as run_order
    if 'Randomizer' in g.run_params['run']:
        
        versions = ['A','B','C'] # run versions
        random.shuffle(versions)
        StimToolLib.write_var_to_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'run_order', ','.join(versions))
        return
    
    # If not randomizer, than use the versions from the run_order params.
    # If there isn't a run_order params, than use the own already on the task list
    schedule_file = get_schedule_file()
    

    
    #Volume workup
    #VolumeWorkup.schedule must be run first in order to set g.volume
    g.volume = StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'volume') #should have been set by volume workup run first
    if g.volume == None:
        ##TMP
        g.volume = 1
        #StimToolLib.error_popup('Could not read volume parameter from ' + g.subj_param_file + '. Did you run the volume workup first?')
    print("VOLUME IS:")
    print(g.volume)
    if g.session_params['joystick']:
        StimToolLib.general_setup(g, winType='pygame')
    else:
        StimToolLib.general_setup(g)
    # g.win.winType = 'pygame'
    # g.win.flip()
    joystick.backend = g.win.winType
    #Initialize joystick
    if g.session_params['joystick']:
        #pygame.init()
        #pygame.joystick.init()
        #pygame.joystick.init()
        nJoys = joystick.getNumJoysticks()
        if nJoys == 1:
            g.joystick = joystick.Joystick(0) 
            #g.joystick.init()
            #print(g.joystick)
            print("Name of Joystick %s" % g.joystick.getName())
        else:
            StimToolLib.error_popup("You don't have a joystick connected?")
    
    # g.win._eventDispatchers = []
    # print(g.win._eventDispatchers)
    #PReload stimuli
    trial_types,images,durations,sound_files = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    
    g.x = visual.TextStim(g.win, text="X", units='pix', height=50, color=[-1,-1,-1], pos=[0,0], bold=True, alignHoriz = 'center')
    g.left_images = images[0]
    g.right_images = images[1]
    itis = durations[0]
    left_rewards = durations[1]
    right_rewards = durations[2]
    start_locations = durations[3]
    g.left_sounds, g.right_sounds = load_sounds(sound_files)
    g.runway_0_0 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_0_0.png'), units='norm', size=(1.85,0.38))
    g.runway_0_0.borderColor = 'white'
    g.runway_0_1 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_0_1.png'), units='norm', size=(1.85,0.38))
    #g.runway_0_1.setBorderColor('white')
    g.runway_1_0 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_1_0.png'), units='norm', size=(1.85,0.38))
    #g.runway_1_0.setBorderColor('white')
    g.runway_1_1 = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Runway_1_1.png'), units='norm', size=(1.85,0.38))
    #g.runway_1_1.setBorderColor('white')
    g.fig = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/figure.png'), pos=[0,0.05], units='norm', size=(0.13,0.35))
    g.fig_select = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/figure_select.png'), pos=[0,0.05], units='norm', size=(0.13,0.37) )
    g.reward_text_1 = visual.TextStim(g.win, text="", units='norm', color='white', pos=[0,-0.48], bold=True, alignHoriz= 'center')
    #g.reward_text_1.pos = StimToolLib.getMSGPosition(g.reward_text_1)
    g.reward_text_2 = visual.TextStim(g.win, text="", units='norm', color='white', pos=[0,-0.6], bold=True, alignHoriz='center')
    #g.reward_text_2.pos = StimToolLib.getMSGPosition(g.reward_text_2)
    g.reward_rect=visual.Rect(g.win, units='norm', fillColor='black', opacity=0.5, height=.35, width=.75, pos=[0,-.5])
    left_bar_loc = [-0.855,0.02]
    right_bar_loc = [0.855, 0.02]
    g.bars_low.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_low.png'), pos=left_bar_loc, units='norm', size=(0.13,0.32)))
    g.bars_low.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_low.png'), pos=right_bar_loc, units='norm', size=(0.13,0.32)))
    g.bars_mid.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_mid.png'), pos=left_bar_loc, units='norm', size=(0.13,0.32)))
    g.bars_mid.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_mid.png'), pos=right_bar_loc, units='norm', size=(0.13,0.32)))
    g.bars_high.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_full.png'), pos=left_bar_loc, units='norm', size=(0.13,0.32)))
    g.bars_high.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_full.png'), pos=right_bar_loc, units='norm', size=(0.13,0.32)))
    g.congrats = visual.TextStim(g.win,text="Congratulations!",units='pix',pos=[0,405],color=[-1,-1,-1],height=100,wrapWidth=int(1600), bold=True)
    
    track_version = track_run() #track version is an integer value that corresponds to the run's place in this task's run order (in free mode track_version=1)
    print('TRACK VERSION:  ' + str(track_version))
    #Maintain a running total of the reward across runs that will be paid
    reset_total=StimToolLib.get_var_from_file(os.path.join(os.path.dirname(g.subj_param_file),'run_flags.txt'), 'AAC_reset_total')
    if reset_total:
        g.total_reward=0
        StimToolLib.write_var_to_file(os.path.join(os.path.dirname(g.subj_param_file),'run_flags.txt'), 'AAC_reset_total', False)
        StimToolLib.write_var_to_file(g.subj_param_file, 'total_reward', g.total_reward)
    else:
        g.total_reward=StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'total_reward')

    # Get total_reward
    g.total_reward = StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'total_reward')
    if g.total_reward is None:
        g.total_reward = 0
    

    #Maintain a running total of the reward across runs that is displayed
    recorded_trial_num=StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'trial_num')
    if track_version==1 or track_version==0:
        StimToolLib.write_var_to_file(g.subj_param_file, 'initial_reward', 0)
        initial_reward=0
    elif recorded_trial_num>int(g.total_trials/2-1): #If task is stopped during run after half the trials are complete the reward visible to the subject will carry over, otherwise it's reset to the initial value
        initial_reward=StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'total_reward_shown')
        StimToolLib.write_var_to_file(g.subj_param_file, 'initial_reward', initial_reward)
    else:
        initial_reward=StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'initial_reward')
    g.total_reward_shown=initial_reward
    
    start_time = data.getDateStr()
    #the commented out fileName was used before--but could lead to conflicts
    #fileName = os.path.join(g.prefix + '_R' + str(track_version) +'.csv')
    fileName = os.path.join(g.prefix + '.csv')
    g.output = open(fileName, 'w')
    StimToolLib.write_var_to_file(g.subj_param_file, 'output_run'+str(track_version), fileName)
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Schedule File:,' +  schedule_file + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')

    
    if g.session_params['joystick']:
        #do joystick test at the beginning--make this a function
        g.win.setColor('white')
        #g.msg.setColor([-1,-1,-1])
        g.win.flip()
    
    
        g.msg = visual.TextStim(g.win, text = '', units = 'norm', pos=(0,0), color = 'black', alignHoriz='center', font = 'helvetica')
        #g.msg.setText('1bcdefghijklmnopqrstuvwxyz12345678902bcdefghijklmnopqrstuvwxyz12345678903bcdefghijklmnopqrstuvwxyz12345678904bcdefghijklmnopqrstuvwxyz1234567890')
        g.msg.setText('press Enter')
        # For pygame, setting the text in the middle can't be done by anchoring text
        # So we need to se the positive manually. This is done by finding the length of the text and setting the position based of screen size
        #g.msg.pos = StimToolLib.getMSGPosition(g.msg)
        g.msg.draw()
        g.win.flip()

        event.clearEvents()
        while True:
            event.clearEvents()
            time.sleep(.5)
            key = event.getKeys(['return'])
            if key: break
        #event.waitKeys(keyList=['return'], clearEvents=True)
        circ = visual.Circle(g.win,units='pix',pos=(0,-100),radius=30,fillColor='red')
        circ.draw()
        g.win.flip()
            
        pressed=False

        # ######## Custom pygame backend for joystick ############
        # print('#####USING PYGAME as Joystick BACKEND')
        # pygame.display.init()
        # pygame.joystick.init()

        # g.joystick = pygame.joystick.Joystick(0)
        # g.joystick.init()
        #########################################################


        
        # print(g.joystick.get_name())
        # print('First X position %s' % g.joystick.get_axis(0))
        # g.joystick = joystick.Joystick(0) 
        g.msg.setColor('red')
        g.msg.setText('Move the the joystick all the way RIGHT and press the trigger button.')
        #g.msg.pos = StimToolLib.getMSGPosition(g.msg)
        
        #g.msg.color = 'red'
        event.clearEvents()

        # env1 = EnvelopeGrating(g.win, ori=0, units='norm', carrier='sin', envelope='sin', mask='gauss', sf=4, envsf=8, size=1, contrast=1.0, moddepth=0.0, envori=0, pos=[0, .5], interpolate=0)
        while not pressed:
            # env1.ori += 0.1
            # env1.draw()
            g.msg.draw()
            #pygame.event.pump()
            x = g.joystick.getX()
            # print(x)
            # print(g.joystick.get_axis(0))
            x_pix = x * g.session_params['screen_x']/2
            circ.pos=(x_pix,-100)
            circ.draw()
        
            #k = event.getKeys(keyList=['return'])
            if g.joystick.getButton(g.session_params['joy_forward']):
                pressed=True
                #StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['RIGHT_MAX'], sel_time, sel_time-instruct_end, x, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                # while g.joystick.getButton(g.session_params['joy_forward']):
                #     wait_for_release=True
                #     g.win.flip()
                #     event.clearEvents()
            g.win.flip()
            event.clearEvents()
        

        g.msg.setColor('black')
        g.msg.setText('Press enter to continue.')
        #g.msg.pos = StimToolLib.getMSGPosition(g.msg)
        g.msg.draw()
        g.win.flip()
        # evt.clear()
        # evt.get()
        
        event.clearEvents()
        while True:
            event.clearEvents()
            time.sleep(.5)
            key = event.getKeys(['return'])
            if key: break
        
        pressed=False
        #g.joystick = joystick.Joystick(0) 
        g.msg.setColor('blue')
        g.msg.setText('Move the the joystick all the way LEFT and press the trigger button.')
        #g.msg.pos = StimToolLib.getMSGPosition(g.msg)
        #g.msg.setColor('blue')
        circ.fillColor='blue'
        event.clearEvents()   
        while not pressed:
            g.msg.draw()
            # pygame.event.pump()
            x=g.joystick.getX()
            x_pix=x*g.session_params['screen_x']/2
            circ.pos=(x_pix,-100)
            circ.draw()
            if g.joystick.getButton(g.session_params['joy_forward']):
                pressed=True
                #StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['LEFT_MAX'], sel_time, sel_time-instruct_end, x, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.win.flip()
            event.clearEvents()   
        g.win.setColor('white')
        g.msg.setColor('black')
        g.win.flip() 
    

    StimToolLib.task_start(StimToolLib.AAC_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    
    ## OLD CODE
    # if g.run_params['practice']:
    #     StimToolLib.run_instructions_joystick(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'instructions_P','AAC_instruct_schedule_P.csv'), g)
    # else:
    #     #/JorgeCode
    #     StimToolLib.run_instructions_joystick(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'instructions_T','AAC_instruct_schedule_' + str(track_version) + '.csv'), g)

    ## New CODE checks for instruction_schedule in ruan params
    if g.session_params['joystick']:
        StimToolLib.run_instructions_joystick(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    else:
        StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)

    #Scan code
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    g.win.flip()

    # Set the Background Color
    g.win.setColor('white')
    g.win.flip()

    ## TESTING FINAL SCREEN
    #final_screen()
    #now = g.clock.getTime()
    #StimToolLib.just_wait(g.clock, now + 8)
    ################
       
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.ideal_trial_start = g.clock.getTime()  #since we aren't syncing with a scanner pulse, don't reset the clock at the beginning of the real task--times will be reletive to the task start as reported to BIOPAC
    g.x.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 8)
    g.ideal_trial_start = g.clock.getTime()
    event.clearEvents()
    for t,iti,left_r,right_r,start_l,left_s,right_s, left_i, right_i in zip(trial_types, itis, left_rewards, right_rewards, start_locations, g.left_sounds, g.right_sounds, g.left_images, g.right_images):
        g.trial_type = t[0] + t[2] + '_'+ str(int(left_r))  + str(int(right_r)) + '_'+str(int(start_l))
        StimToolLib.write_var_to_file(g.subj_param_file, 'trial_num', g.trial)
        event.clearEvents()
        do_one_trial(t,iti,left_r,right_r,start_l,left_s,right_s, left_i, right_i)
        g.trial = g.trial + 1
  

    if g.final_run:
        final_screen()
    








