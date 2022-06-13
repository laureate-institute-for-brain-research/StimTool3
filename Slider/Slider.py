from psychopy import prefs

import StimToolLib, os, random, operator, csv
from psychopy import visual, core, event, data, gui, sound

from psychopy.visual.windowwarp import Warper
import math
class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.warper = None
        self.clock = None #global clock used for timing
        self.x = None #+ fixation stimulus
        self.output = None #The output file
        self.msg = None
        
event_types={
    'INSTRUCT_ONSET': 0,
    'RESPONSE': 1,
    'TASK_END':StimToolLib.TASK_END}



def doHappyRating(question):
    """
    Do Happy Rating
    """
    question_type = question[0]
    question_text = question[1]
    question_subtext = question[2]
    audio_path = question[3]
    number_of_choices = int(question[4])
    choices_nums = range(number_of_choices)
    question_lables = question[5:]

    topTextstim = visual.TextStim(g.win, text = question_text, units = 'norm', pos = (0,0.7), height = .1, wrapWidth = 1.5)

    subTextstim = visual.TextStim(g.win, text = question_subtext.replace("\\n",'\n'), units = 'norm', pos = (0,0.3), height = .07, wrapWidth = 1.5)
    
    
    g.win.flip()

    if audio_path != 'None':
        s  = sound.Sound(value =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', audio_path))
        s.play()
    slider = visual.Slider(g.win, ticks=choices_nums, labels=question_lables, pos=(0,0), size= (1.5,.1),
        units='norm', flip=False, style='rating', granularity=1, readOnly=False, color='white', font='Helvetica Bold',
        labelHeight = .08)
    
    rating_start = g.clock.getTime()
    maker_pos = int(len(choices_nums) / 2)

    show_confirm_response = False
    first_response = True

    while True:
        g.win.flip()
        StimToolLib.check_for_esc()
        topTextstim.draw()
        subTextstim.draw()
        g.happy_image.draw()
        slider.draw()

        if show_confirm_response: g.confirmTexttim.draw()

        resp = event.getKeys([g.run_params['left'],g.run_params['right'], g.run_params['select'] ])

        # No response, don't go further
        if len(resp) == 0: continue

        # Clicked the left button
        if resp[0] == g.run_params['left']:
            # Decreament Marker
            if first_response:
                # For Even numbers, starting marker should be 1 tick above middle
                if number_of_choices % 2 == 0:
                    maker_pos = int( number_of_choices / 2) - 1
                # For odd numbers, starting marker is the cieling, or just the middle int()
                else:
                    maker_pos = int (number_of_choices / 2) -1
                first_response = False
            else:
                # Decreament Marker
                maker_pos -= 1

            # If already on the last choices continue
            if maker_pos <= min(choices_nums) -1:
                maker_pos += 1 # Increment the number back
                continue
            slider.markerPos = maker_pos
        if resp[0] == g.run_params['right']:

            if first_response:
                # For Even numbers, starting marker should be 1 tick above middle
                if number_of_choices % 2 == 0:
                    maker_pos = int( number_of_choices / 2)
                # For odd numbers, starting marker is the cieling, or just the middle int()
                else:
                    maker_pos = int (number_of_choices / 2) + 1
                first_response = False
            else:
                maker_pos += 1
                
            if maker_pos >= max(choices_nums) + 1:
                maker_pos -= 1
                continue
            slider.markerPos = maker_pos
        if resp[0] == g.run_params['select']:
            
            r = slider.getRating()
            if slider.markerPos is None: 
                show_confirm_response = True
                continue
             
            if audio_path != 'None': s.stop()
            now = g.clock.getTime()
            StimToolLib.mark_event(g.output, question_type, 'NA', event_types['RESPONSE'], now, now - rating_start, slider.markerPos,question_text, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            return


def doCalmRating(question):
    """
    Do Fear Rating
    """
    question_type = question[0]
    question_text = question[1]
    question_subtext = question[2]
    audio_path = question[3]
    number_of_choices = int(question[4])
    choices_nums = range(number_of_choices)
    question_lables = question[5:]

    topTextstim = visual.TextStim(g.win, text = question_text, units = 'norm', pos = (0,0.7), height = .1, wrapWidth = 1.5)

    subTextstim = visual.TextStim(g.win, text = question_subtext.replace("\\n",'\n'), units = 'norm', pos = (0,0.3), height = .07, wrapWidth = 1.5)

    
    if audio_path != 'None':
        s  = sound.Sound(value =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', audio_path))
        s.play()

    slider = visual.Slider(g.win, ticks=choices_nums, labels=question_lables, pos=(0,0), size= (1.5,.1),
        units='norm', flip=False, style='rating', granularity=1, readOnly=False, color='white', font='Helvetica Bold',
        labelHeight = .08)
    
    rating_start = g.clock.getTime()
    maker_pos = int(len(choices_nums) / 2)
    show_confirm_response = False
    first_response = True
    while True:
        g.win.flip()
        StimToolLib.check_for_esc()
        topTextstim.draw()
        subTextstim.draw()
        g.calm_image.draw()
        slider.draw()
        if show_confirm_response: g.confirmTexttim.draw()
        
        resp = event.getKeys([g.run_params['left'],g.run_params['right'], g.run_params['select'] ])

        # No response, don't go further
        if len(resp) == 0: continue

        # Clicked the left button
        if resp[0] == g.run_params['left']:
            if first_response:
                # For Even numbers, starting marker should be 1 tick above middle
                if number_of_choices % 2 == 0:
                    maker_pos = int( number_of_choices / 2) - 1
                # For odd numbers, starting marker is the cieling, or just the middle int()
                else:
                    maker_pos = int (number_of_choices / 2) -1
                first_response = False
            else:
                # Decreament Marker
                maker_pos -= 1

            # If already on the last choices continue
            if maker_pos <= min(choices_nums) -1:
                maker_pos += 1 # Increment the number back
                continue
            slider.markerPos = maker_pos
        if resp[0] == g.run_params['right']:
            if first_response:
                # For Even numbers, starting marker should be 1 tick above middle
                if number_of_choices % 2 == 0:
                    maker_pos = int( number_of_choices / 2)
                # For odd numbers, starting marker is the cieling, or just the middle int()
                else:
                    maker_pos = int (number_of_choices / 2) + 1
                first_response = False
            else:
                maker_pos += 1

            if maker_pos >= max(choices_nums) + 1:
                maker_pos -= 1
                continue
            slider.markerPos = maker_pos
        if resp[0] == g.run_params['select']:
            r = slider.getRating()
            if slider.markerPos is None: 
                show_confirm_response = True
                continue
            now = g.clock.getTime()
            if audio_path != 'None': s.stop()
            StimToolLib.mark_event(g.output, question_type, 'NA', event_types['RESPONSE'], now, now - rating_start, slider.markerPos,question_text, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            return

def doOtheRating(question):
    """
    Show Rating
    """
    question_type = question[0]
    question_text = question[1]
    question_subtext = question[2]
    audio_path = question[3]
    number_of_choices = int(question[4])
    choices_nums = range(number_of_choices)
    question_lables = question[5:]


    topTextstim = visual.TextStim(g.win, text = question_text, units = 'norm', pos = (0,0.7), height = .1, wrapWidth = 1.5)

    subTextstim = visual.TextStim(g.win, text = question_subtext.replace("\\n",'\n'), units = 'norm', pos = (0,0.3), height = .07, wrapWidth = 1.5)

    g.win.flip()

    if audio_path != 'None':
        s  = sound.Sound(value =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', audio_path))
        s.play()


    slider = visual.Slider(g.win, ticks=choices_nums, labels=question_lables, pos=(0,0), size= (1.5,.1),
        units='norm', flip=False, style='rating', granularity=1, readOnly=False, color='white', font='Helvetica Bold',
        labelHeight = .08)
    
    rating_start = g.clock.getTime()

    # Marker position is in the middle
    maker_pos = int(len(choices_nums) / 2)
    show_confirm_response = False
    
    first_response = True
    while True:
        g.win.flip()
        StimToolLib.check_for_esc()
        topTextstim.draw()
        subTextstim.draw()
        slider.draw()
        if show_confirm_response: g.confirmTexttim.draw()

        resp = event.getKeys([g.run_params['left'],g.run_params['right'], g.run_params['select'] ])

        # No response, don't go further
        if len(resp) == 0: continue

        # Clicked the left button
        if resp[0] == g.run_params['left']:

            if first_response:
                # For Even numbers, starting marker should be 1 tick above middle
                if number_of_choices % 2 == 0:
                    maker_pos = int( number_of_choices / 2) - 1
                # For odd numbers, starting marker is the cieling, or just the middle int()
                else:
                    maker_pos = int (number_of_choices / 2) -1
                first_response = False
            else:
                # Decreament Marker
                maker_pos -= 1

            # If already on the last choices continue
            if maker_pos <= min(choices_nums) -1:
                maker_pos += 1 # Increment the number back
                continue
            slider.markerPos = maker_pos
        if resp[0] == g.run_params['right']:

            if first_response:
                # For Even numbers, starting marker should be 1 tick above middle
                if number_of_choices % 2 == 0:
                    maker_pos = int( number_of_choices / 2)
                # For odd numbers, starting marker is the cieling, or just the middle int()
                else:
                    maker_pos = int (number_of_choices / 2) + 1
                first_response = False
            else:
                maker_pos += 1

            if maker_pos >= max(choices_nums) + 1:
                maker_pos -= 1
                continue
            slider.markerPos = maker_pos
        if resp[0] == g.run_params['select']:
            r = slider.getRating()
            if slider.markerPos is None: 
                show_confirm_response = True
                continue
            now = g.clock.getTime()
            if audio_path != 'None': s.stop()
            StimToolLib.mark_event(g.output, question_type, 'NA', event_types['RESPONSE'], now, now - rating_start, slider.markerPos,question_text, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            return


def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/RT.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status


def set_warper():
    g.warper = Warper(g.win, warp=None, warpfile = "", warpGridsize = 300, eyepoint = [0.5, 0.5], flipHorizontal = True, flipVertical = False)
    g.warper.changeProjection(warp= None, flipHorizontal = True)
    print('Flipping Screen')


def show_breathing_timer():
    """
    Runs then breathing Timer
    """
    breathing_duration = 60 # breathing load for 60 seconds
    start_time = g.clock.getTime()
    midText = visual.TextStim(g.win, text = 'Breathing Period', units = 'norm', pos = (0,.8), height = .1)

    timer = breathing_duration 
    timerstim = visual.TextStim(g.win, text = str(timer), units = 'norm', pos = (0,0), height = .15)
    event.clearEvents()
    while g.clock.getTime() <=  + start_time + breathing_duration:

        StimToolLib.check_for_esc()
        midText.draw() # Draw Text

        # Draw Timer
        timer =  "%i" % int((start_time + breathing_duration) - g.clock.getTime())
        timerstim.setText(timer)
        timerstim.draw()

        g.win.flip()

        # Pressin 's' key will skip timer
        resp = event.getKeys(['s'])
        if len(resp) == 0: continue
        if resp[0] == 's': break # 
    
    g.win.flip()
    s = sound.Sound(value = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media','stai_audio','aiff', 'remove_load.mp3.aiff' ))
    s.play()
    text_stim = visual.TextStim(g.win, text = 'We will now remove the breathing load.\n\nPress C to continue', units = 'norm', pos = (0,0), height = .1)
    text_stim.draw()
    g.win.flip()
    event.clearEvents() # Clear Events in the event buffer
    k = event.waitKeys(keyList=[ 'c', 'C', 'escape'])
    s.stop()
    if k[0] == 'escape': raise StimToolLib.QuitException

def show_one_slide(slide_path, audio_path = None):
    """
    """
    duration = None
    if audio_path:
        s = sound.Sound(value = audio_path)
        duration = s.getDuration()
        s.play()
    g.win.flip()
    slideStim = visual.ImageStim(g.win, image = slide_path)
    slideStim.draw()
    g.win.flip()
    now = g.clock.getTime()
    StimToolLib.just_wait(g.clock, now + 1) # wait 1 second
    k = event.waitKeys(keyList=[ 
        g.session_params[g.run_params['select_1']],  g.session_params[g.run_params['select_2']], 'escape'],
        clearEvents = True)
    # If it gets to here, than should stop
    if audio_path: s.stop()
    if k[0] == 'escape': raise StimToolLib.QuitException
    return k

def run_try():  
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="Slider")
        myDlg.addField('Run Number', choices=schedules, initial=str(g.run_params['run']))
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            #print 'QUIT!'
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    StimToolLib.general_setup(g, useFBO=True)

    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])


    # Get the Schedule
    # Question_Type, Question, Number of Choices, Ticks Position
    questions = []
    schedule = open(schedule_file, 'r')
    for idx,line in enumerate(schedule):
        if idx == 0:
            continue
        row = line.replace('\n','').split(',')
        questions.append(row)


    g.clock = core.Clock()
    start_time = data.getDateStr()
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    g.subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '_' + g.run_params['param_file'])
    fileName = os.path.join(g.prefix + '.csv')
    #g.prefix = 'DP-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  schedule_file + ',Event Codes:,' + str(sorted_events) + ',Trial Types are coded as follows: 8 bits representing [valence neut/neg/pos] [target_orientation H/V] [target_side left/right] [duration .5/1] [valenced_image left/right] [cue_orientation H/V] [cue_side left/right]\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.SLIDER_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #StimToolLib.show_title(g.win, g.title)
    #g.output.write('Trial_Type:-1:negative;0:neutral;1:positive,Image,ITI_Onset,ITI_startle,Stimulus_onset,Stimulus_startle,Valence_Rating,Valence_rating_time,Arousal_rating,Arousal_rating_time\n')
    
    # Flip screen if mock_scan param is set
    try:
        if g.session_params['mock_scan']:
            print(g.session_params['mock_scan'])
            if str(g.session_params['mock_scan']) == 'True':
                print('Flip')
                set_warper()
    except Exception as e:
        print(e)

    g.confirmTexttim = visual.TextStim(g.win, text = 'Please enter a response', units = 'norm', pos = (0,-0.7), height = .1)
    g.happy_image = visual.ImageStim(g.win, image = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'happy_scale.PNG' ), units = 'norm', pos = (0,0.3), size = (1.8,.4))
    g.calm_image = visual.ImageStim(g.win, image = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'calm_scale.PNG' ), units = 'norm',pos = (0,0.3), size =(1.8,.4))

    g.breathing_slide = visual.ImageStim(g.win, image = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media','instructions','bk_pilot_mock_scan_instructions', 'Slide19.jpeg' ), pos = (0,0))
    # Run 
    #StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), g.run_params['instruction_schedule']), g)
    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), g.run_params['instruction_schedule']), g)

    try:
        if g.run_params['breathing_duration']:

            g.win.flip()
            s = sound.Sound(value =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media','instructions','Slide28.mp3.aiff' ))
            s.play()
            now = g.clock.getTime()
            g.breathing_slide.draw() # Show Breathing Slide
            g.win.flip()
            #StimToolLib.just_wait(g.clock, now + int(g.run_params['breathing_duration']))
            # Wait for admin to press the 'b' key to continue
            event.clearEvents() # Clear Events in the event buffer
            k = event.waitKeys(keyList=[ 'b', 'escape'])
            if k[0] == 'b':
                s.stop()
                show_breathing_timer()
            if k[0] == 'escape': raise StimToolLib.QuitException

    except:
        pass

    g.win.flip()
    begin_stim = visual.TextStim(g.win, text = 'Are you ready to begin rating?\n\nPress the RIGHT button start.', units = 'norm', pos = (0,0), height = .1)
    s = sound.Sound(value =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media','instructions','Slide19.mp3.aiff' ))
    s.play()
    now = g.clock.getTime()
    begin_stim.draw()
    g.win.flip()
    event.clearEvents() # Clear Events in the event buffer
    k = event.waitKeys(keyList=[ g.run_params['right'], 'escape'])
    s.stop() # Stop Audio when they pressed right
    if k[0] == 'escape': raise StimToolLib.QuitException

    # Run Slider Questions
    for question in questions:
        question_type = question[0]
        g.first_response = True
        if question_type == 'happy': doHappyRating(question)
        elif question_type == 'calm': doCalmRating(question)
        else: doOtheRating(question)

    g.win.flip()
