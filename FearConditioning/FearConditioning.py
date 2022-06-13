
import StimToolLib, os, random, operator, sys
from psychopy import visual, core, event, data, gui, sound, prefs

#Stop signal task

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.clock = None #global clock used for timing
        self.x = None #X fixation stimulus
        self.output = None #The output file
        self.msg = None
        self.ideal_trial_start = None #ideal time the current trial started
        self.trial = None #trial number
        self.trial_type = None #current trial type
        self.offset = 0.008 #8ms offset--request window flip this soon before it needs to happen->should get precise timing this way
        self.stimuli = None #X and O stimuli
        self.average_sound_latency = 0 #correction for latency beteween calling sound.play() and the sound actually playing
        self.update_RT_during_scan = False #whether or not to update the average RT every block during the scanning run
        self.scream_offset = 0.5 #how long into the CS+ to play the scream (changed from 1.4 to 0.5 because the scream is 1s long)

event_types = {'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'ARROW_ONSET':3, 
    'RESPONSE':4, 
    'IMAGE_ONSET':5, 
    'US':6,
    'SOUND':7,
    'RATING':8,
    'VALENCE_RATING_ONSET':9,
    'VALENCE_RATING_RESPONSE':10,
    'AROUSAL_RATING_ONSET':11,
    'AROUSAL_RATING_RESPONSE':12,
    'ANXIETY_RATING_ONSET':13,
    'ANXIETY_RATING_RESPONSE':14,
    'LEAD_IN_OUT':15,
    'TASK_END':StimToolLib.TASK_END}

    
    
def do_one_image_trial(trial_type):
    if trial_type == 2: #pick image and whether or not to play US from trial type
        image = g.fractals[0]
    else:
        image = g.fractals[1]
    #wait for 300ms
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 0.3)
    #show fractal
    g.background.draw()
    image.draw()
    g.win.flip()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['IMAGE_ONSET'], g.clock.getTime(), 'NA', 'NA', image._imName, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 0.3 + g.scream_offset)
    #play scream if CS+&US trial
    if trial_type == 4:
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['US'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.scream.play()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 0.3 + 1.5)
    g.background.draw()
    g.win.flip() #blank the screen
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 0.3 + 1.5 + 0.2)
    g.ideal_trial_start = g.ideal_trial_start + 2
    
def do_one_arrow_trial(trial_type):
    #wait for 300ms
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 0.3)
    #show arrow and record responses
    g.background.draw()
    g.arrows[trial_type].draw()
    g.win.flip()
    arrow_onset_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['ARROW_ONSET'], arrow_onset_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']])
    #event.getKeys(g.resk.values()) #clear pressed keys so that a very early press is not counted
    while g.clock.getTime() < g.ideal_trial_start + 0.3 + 2.5: #show arrow for 2.5s
        StimToolLib.check_for_esc()
        key = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']]) 
        if key:
            now = g.clock.getTime()
            if key[0] == g.session_params['left']: #record every response 
                if trial_type == 0:
                    correct = 1
                else:
                    correct = 0
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE'], now, now - arrow_onset_time, 0, correct, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            if key[0] == g.session_params['right']:
                if trial_type == 0:
                    correct = 0
                else:
                    correct = 1
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE'], now, now - arrow_onset_time, 1, correct, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            if key[0] == g.session_params['select']: #record if they press the select button--but don't draw the box
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE'], now, now - arrow_onset_time, 2, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                continue #skip drawing the box
            g.background.draw()
            g.arrows[trial_type].draw() 
            g.border.draw()
            g.win.flip()
    g.background.draw()
    #hide arrow and wait for 200ms
    g.win.flip() #blank the screen
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 3)
    g.ideal_trial_start = g.ideal_trial_start + 3
    
def do_one_trial(trial_type):
    g.background.draw() #start every trial with just the gray background
    g.win.flip()
    if trial_type < 2: #trial types 0 and 1: arrow trials
        do_one_arrow_trial(trial_type)
    elif trial_type == 5: #leadin/leadout trial
        StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['LEAD_IN_OUT'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + 4)
        g.ideal_trial_start = g.ideal_trial_start + 4
    else: #trial types 2, 3, 4: CS-, CS+, CS+&US trials
        do_one_image_trial(trial_type)

def play_sound_or_get_rating():
    msg = visual.TextStim(g.win,text='Play the sound, then rate the intensity of the sound',units='norm',pos=[-0.8,-0.5],color=[1,1,1],height=0.1,wrapWidth=1.6, alignHoriz = 'left', alignVert='top')
    scale_labels = ['Play\nSound', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    volume_scale = visual.RatingScale(g.win, lineColor='White', precision=1, low=0, high=10, singleClick=False, leftKeys=g.session_params['left'], rightKeys=g.session_params['right'], mouseOnly = False, marker=visual.TextStim(g.win, text='l', units='norm', color='red'),
        textColor='White', scale=None, labels=scale_labels,  pos=(0,-0.25), showAccept=False, stretch=2, tickMarks=range(0,11), markerStart = 0)
    start_time = g.clock.getTime()
    while volume_scale.noResponse: 
        StimToolLib.check_for_esc()
        msg.draw()
        volume_scale.draw()
        g.win.flip()
    end_time = g.clock.getTime()
    if volume_scale.getRating() == 0:
        g.white_noise.play()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SOUND'], end_time, end_time - start_time, 'NA', g.white_noise.getVolume(), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    else:
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING'], end_time, end_time - start_time, volume_scale.getRating(), g.white_noise.getVolume(), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    return volume_scale.getRating()
    
def one_volume_rating(sound_intensity):
    g.white_noise.setVolume(sound_intensity)
    rating = 0
    while rating == 0: #will be 0 for trials when the subject plays the sound
        rating = play_sound_or_get_rating()
    return rating
    
def volume_workup():
    g.trial = 0
    g.trial_type = -1
    g.white_noise = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/400msecWN.wav'), volume=0)
    rating = 0
    sound_intensity = 0
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #StimToolLib.show_title(g.win, g.title)
    StimToolLib.show_instructions(g.win, g.volume_workup_instructions)
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    while rating < 8:
        sound_intensity = sound_intensity + 0.1
        rating = one_volume_rating(sound_intensity)
        g.trial = g.trial + 1
    return sound_intensity

def get_one_count():
    while True:
        myDlg = gui.Dlg(title="Rating")
        myDlg.addField('Enter Rating Here')
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            continue
        try:
            retval = int(thisInfo[0]) 
            break
        except ValueError:
            pass
    return retval

def get_anxiety_rating():
    
    scale_1 = visual.RatingScale(g.win, lineColor='White', precision=1, low=0, high=100, singleClick=False, mouseOnly = False, marker=visual.TextStim(g.win, text='l', units='norm', color='red'),
        textColor='White', scale=None, pos=(0,-.35), showAccept=False, stretch=2.85, markerStart = 50)
    msg = visual.TextStim(g.win,text="",units='norm',pos=[-0,-.5],color=[1,1,1],height=.2,wrapWidth=2, alignHoriz = 'center', alignVert='top')
    msg.setText('Anxiety')
    
    msg.draw()
    scale_1.draw()
    g.win.flip()
    start_time = g.clock.getTime()
    rating = get_one_count()
    end_time = g.clock.getTime()
    return rating, end_time, end_time - start_time
    
def get_end_ratings():
    if g.run_params['practice']: 
        StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['final_instructions']), g)
    for i in range(2):
        g.fractals[i].units='norm'
        #stimulus images are presented at 360x600 pixels
        #y size in normalized units needs to be 1.2 to go from the top of the rating bar to the top of the screen
        #need to calculate x width given screen's dimensions
        image_ratio = 360.0 / 600
        screen_ratio = float(g.session_params['screen_x']) / g.session_params['screen_y']
        norm_y = 1.2
        norm_x = norm_y * image_ratio / screen_ratio
        g.fractals[i].size=(norm_x, norm_y)
        #g.fractals[i].size=(.6, 1.2)
        g.fractals[i].pos=(0, .37)
        g.fractals[i].autoDraw = True
        g.happiness_sound.play()
        rating, end_time, response_time = StimToolLib.get_valence_or_arousal(True, 'How happy or unhappy does this image make you feel?', g)
        StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['VALENCE_RATING_RESPONSE'], end_time, response_time, rating, i, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.happiness_sound.stop()
        g.excitement_sound.play()
        rating, end_time, response_time = StimToolLib.get_valence_or_arousal(False, 'How calm or excited does this image make you feel?', g)
        StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['AROUSAL_RATING_RESPONSE'], end_time, response_time, rating, i, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.excitement_sound.stop()
        #g.anxiety_sound.play()
        rating, end_time, response_time = get_anxiety_rating()
        StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['ANXIETY_RATING_RESPONSE'], end_time, response_time, rating, i, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        #g.anxiety_sound.stop()
        g.fractals[i].autoDraw = False
        if g.run_params['practice']: #for practice run, only rate the image once (there is only one fractal shown for practice)
            break
    g.win.flip()

def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/FC.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        #StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_END'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
        
    StimToolLib.task_end(g)
    return g.status
    
def run_try():  
#def run_try(SID, raID, scan, resk, run_num='Practice'):
    #g.resk = resk
    
    #param_filename = os.path.dirname(__file__) + '/data/' + g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + 'FC.params'
    #cs_order = StimToolLib.get_var_from_file(param_filename, 'order') #read counterbalance param from file, or pick it and put one and put it in the dialogue box
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="FC")
        myDlg.addField('Run Number', choices=schedules, initial=str(g.run_params['run']))
    
        
        #myDlg.addField('CS Order', choices=['0', '1'], initial=cs_order) #only ask for the order if it hasen't been picked already--to avoid the operator accidentally changing it
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1#the user hit cancel so exit 

        g.run_params['run'] = thisInfo[0]
        #volume = StimToolLib.get_var_from_file(param_filename, 'volume')
        volume = 1 #set to max volume...possibly change this if we decide to adjust it for different subjects
        if volume == None:
            StimToolLib.error_popup('Fear Conditioning run without doing volume workup first! To pick a volume for this subject manually, edit ' + param_filename + ' and run again')
        #if len(thisInfo) > 1: #just got a CS+/- order from dialogue box--save it to a file
        #    cs_order = thisInfo[1]
        #    StimToolLib.write_var_to_file(param_filename, 'order', cs_order)
    StimToolLib.general_setup(g)
    volume = 1 #may need to change this if we decide to use different volumes for different subjects
    
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_FC_Schedule' + str(g.run_params['run']) + '.csv')
    trial_types,junk,junk,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    
    start_time = data.getDateStr()
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    
    g.prefix = StimToolLib.generate_prefix(g)
    subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['param_file']) #will store Blue_Pull in subject specific parameter file
    cs_order = StimToolLib.get_var_from_file(subj_param_file, 'cs_order') #read counterbalance param from file, or pick it and put one and put it in the dialogue box
    #if order:
    #    order_already_selected = True
    if cs_order == None:
        cs_order = ['0', '1'][random.randint(0,1)] #pick a random direction--will be overwritten by subject number (even/odd) if possible
        try:
            val = int(g.session_params['SID'][len(g.session_params['SID']) - 1]) #initialize counterbalancing based on even/odd subj numbers
            if val % 2 == 0:
                cs_order = '0'
            else:
                cs_order = '1'
        except ValueError:
            pass #in case subj number does not end in an integer
        StimToolLib.write_var_to_file(subj_param_file, 'cs_order', cs_order)
    
    fileName = os.path.join(g.prefix + '.csv')
    #subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['param_file'])
    #g.prefix = 'FC-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + ',Trial Types are coded as follows: 0->left arrow; 1->right arrow; 2->CS-; 3->CS+; 4->CS+&US, volume=' + str(volume) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    
    if g.run_params['volume_test']: #volume workup/test
        #volume = volume_workup()
        volume = 0.6
        StimToolLib.write_var_to_file(subj_param_file, 'volume', volume)
        return 0
    #volume = StimToolLib.get_var_from_file(subj_param_file, 'volume')
    volume = 1 #may need to change this if we decide to use different volumes for different subjects
    if not volume:
        StimToolLib.error_popup('Volume not selected! Run volume test first.')

    text_height = 80
    g.instruct_images = []

    
    g.arrows = [] #left and right arrows
    g.arrows.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/GrayLeft.gif'), units='pix'))
    g.arrows.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/GrayRight.gif'), units='pix'))
    g.fractals = [] #CS- and CS+
    #g.fractals.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/fractal1.jpg'), units='pix', size=(360, 600)))
    #g.fractals.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/fractal2.jpg'), units='pix', size=(360, 600)))
    
    g.fractals.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  g.run_params['image_1']), units='pix', size=(360, 600)))
    g.fractals.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  g.run_params['image_2']), units='pix', size=(360, 600)))
    
    if g.run_params['practice']: #practice run, only show fractal not used in the scanner
        g.fractals = []
        #g.fractals.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/fractal3.jpg'), units='pix', size=(360, 600)))
        #g.fractals.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/fractal3.jpg'), units='pix', size=(360, 600)))
        
        g.fractals.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  g.run_params['practice_image']), units='pix', size=(360, 600)))
        g.fractals.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  g.run_params['practice_image']), units='pix', size=(360, 600)))
    if cs_order == '1':
        g.fractals.reverse()
    g.border = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media','YellowFrame.gif'), units='pix', mask=os.path.join(os.path.dirname(__file__),  'media/frame_mask.gif'))
    g.background = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media','Gray800_600.gif'), units='pix')
    g.scream = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/Scream2sx3B.wav'), volume=volume)
    
    g.anxiety_sound = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'FC_Anxiety.aiff'), volume=g.session_params['instruction_volume'])
    g.excitement_sound = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'FC_Excitement.aiff'), volume=g.session_params['instruction_volume'])
    g.happiness_sound = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'FC_Happiness.aiff'), volume=g.session_params['instruction_volume'])

    StimToolLib.task_start(StimToolLib.FEAR_CONDITIONING_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #StimToolLib.show_title(g.win, g.title)
    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    #if g.run_params['practice']:
    #    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'FC_instruct_scheduleP.csv'), g)
        #StimToolLib.show_instructions(g.win, g.prac_instructions)
    #else:
    #    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'FC_instruct_scheduleS.csv'), g)
        #StimToolLib.show_instructions(g.win, g.scan_instructions)

    g.trial = 0
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    g.win.flip()
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    g.ideal_trial_start = instruct_end_time

    for t_type in trial_types:
        g.trial_type = t_type
        do_one_trial(int(t_type))

        g.trial = g.trial + 1
    StimToolLib.just_wait(g.clock, g.clock.getTime() + 1) #wait 1 second so the total task length is an even number of seconds and ends on a TR
    get_end_ratings()

    
  
 


