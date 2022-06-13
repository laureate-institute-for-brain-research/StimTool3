
import StimToolLib, os, random, operator, sys
from psychopy import visual, core, event, data, gui, sound, prefs
import gc
gc.collect()


class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several
    # functions don't need to be passed in as parameters
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
        self.HAND_ORI = 0 # The Orientation degree of the dial hand
        self.DIAL_RATING_LIMIT = 10 # number of clicks on either side to move marker
        self.volume = None # Default Volume, needs to be set by Volume Workup
        

event_types = {
    'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'TRIAL_ONSET': 3,
    'FIXATION_ONSET':4, 
    'AUDIO_ONSET':5, 
    'VIDEO_ONSET': 6,
    'IMAGE_ONSET': 7,
    'DIAL_RESPONSE':8, 
    'RATING_ONSET': 9,
    'RATING_BUTTON_RESPONSE': 10,
    'RATING_DIAL_RESPONSE': 11,
    'RATING_DIAL_LOCKED': 12,
    'TASK_END':StimToolLib.TASK_END}


def dial_stimuli(idx):
    """
    Snippet of Code for Dial Stim and response
    inside the while loop
    """
    g.arc.draw()
    g.hand.draw()
    g.gauge_text.text =  g.hand.ori
    # g.gauge_text.draw()
    g.win.flip()
    k = event.getKeys(keyList = [g.session_params['dial_right'],g.session_params['dial_left'],'z','escape'])
    if k:
        if k[0] == 'z': return 'skip' # Skip to next trial
        if k[0] == 'escape':
            # Stop Sound if pressing escape
            try:
                g.stims[idx].stop()
            except:
                pass
            raise StimToolLib.QuitException()

        if k[0] == g.session_params['dial_right']:
            # Only allow up to 90 degrees
            if g.hand.ori < 100:
                g.hand.ori = g.hand.ori + 1

        if k[0] == g.session_params['dial_left']:
            # only degress greather than 0 degrees.
            if g.hand.ori > 0:
                g.hand.ori = g.hand.ori - 1
        StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['DIAL_RESPONSE'], g.clock.getTime(), str(g.clock.getTime() - g.trial_onset), k[0], str(g.hand.ori), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])



def do_rating(trial_type, duration, idx):
    """
    Run Rating Question
    """
    response_type = trial_type[0] # 2 = using dial, 3 = using butotn box
    question_type = trial_type[2] # 3 = identity, 4 = valence, 5 = arousal

    print('Response Type:%s, Question Type:%s' % (response_type, question_type))

    # Set Slider Things
    if question_type == '3':
        if g.run_params['media_type'] == 'audio': 
            g.rating_question.text = "Identity: How much did this clip relate to your identity as a native person?"
        if g.run_params['media_type'] == 'video':
            g.rating_question.text = "Identity: How much did this video relate to your identity as a native person?"
        if g.run_params['media_type'] == 'image':
            g.rating_question.text = "Identity: How much did these pictures relate to your identity as a native person?"
        
        g.slider = visual.Slider(g.win, ticks = range(9), labels = ['0','50', '100'],pos = (0,0), size = (1.5,.1), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.08)

        # if response_type == '2': 
        g.DIAL_RATING_LIMIT = 10
        # g.slider.ticks = range(101) # Hack to make the ticks be less than what they are
       
    # Valence Question
    if question_type == '4': 
        if g.run_params['media_type'] == 'audio': 
            g.rating_question.text = "Valence: Rate your mood in response to this clip. "
        if g.run_params['media_type'] == 'video':
            g.rating_question.text = "Valence: Rate your mood in response to this video."
        if g.run_params['media_type'] == 'image':
            g.rating_question.text = "Valence: Rate your mood in response to these pictures."
        g.slider = visual.Slider(g.win, ticks = range(9), labels = ['negative', 'neutral', 'positive'],
        pos = (0,-.3), size = (1.5,.1), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.08)

    # calm Question
    if question_type == '5': 
        if g.run_params['media_type'] == 'audio': 
            g.rating_question.text = "Arousal: Rate your arousal in response to this clip. "
        if g.run_params['media_type'] == 'video':
            g.rating_question.text = "Arousal: Rate your arousal in response to this video."
        if g.run_params['media_type'] == 'image':
            g.rating_question.text = "Arousal: Rate your arousal in response to these pictures."
        g.slider = visual.Slider(g.win, ticks = range(9), labels = ['calm', 'middle', 'excited'],
        pos = (0,-.3), size = (1.5,.1), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.08)

    if response_type == '2':
        g.slider.ticks = range(101)
        response_keys = [g.session_params['dial_left'],g.session_params['dial_right'], g.session_params['dial_select'], 'z']
    else:
        response_keys = [g.session_params['left'], g.session_params['right'], g.session_params['select'], 'z']

    # Actual Slider stuff
    marker_pos = int(len(g.slider.ticks) / 2)
    now = g.clock.getTime()

    ## TEst
    # print(g.slider.__dict__)

    # Dial Limit - number of keys total consecutively to 
    # Constitute a marker move
    DIAL_RIGHT_LIMIT = 0
    DIAL_LEFT_LIMIT = 0
    g.win.flip()
    locked = False
    last_key = ''

    StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['RATING_ONSET'], g.clock.getTime(), 'NA', 'NA', g.rating_question.text, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    while g.clock.getTime() <= g.ideal_trial_start:
        StimToolLib.check_for_esc()
        g.rating_question.draw()
        g.slider.draw()

        # Draw SAM Faces for Valence and Arousal
        if question_type == '4': g.happy_scale.draw()
        if question_type == '5': g.calm_scale.draw()
        g.win.flip()

        resp = event.getKeys(response_keys)

        # Check if key was pressed
        if len(resp) == 0: continue

        # Exit out of loop if z pressed
        if resp[0] == 'z': break

        ## Incrementing for Button Box
        if response_type == '3' and resp[0] == g.session_params['left'] and not locked:
            # Check if it's past limit
            if marker_pos >= 0:
                marker_pos -= 1
            g.slider.markerPos = marker_pos
            StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['RATING_BUTTON_RESPONSE'], g.clock.getTime(), str(g.clock.getTime() - g.trial_onset), resp[0],str(g.slider.markerPos), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

        if response_type == '3' and resp[0] == g.session_params['right'] and not locked:
            if marker_pos <= len(g.slider.ticks) - 1:
                marker_pos += 1
            g.slider.markerPos = marker_pos
            StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['RATING_BUTTON_RESPONSE'], g.clock.getTime(), str(g.clock.getTime() - g.trial_onset), resp[0],str(g.slider.markerPos), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

        if response_type == '3' and resp[0] == g.session_params['select'] and not locked:
            # Locked in 
            # write to file
            g.slider.marker.fillColor = 'red'  
            locked = True
            StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['RATING_BUTTON_RESPONSE'], g.clock.getTime(), str(g.clock.getTime() - g.trial_onset), resp[0],str(g.slider.markerPos), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            pass

        ## Response Dial
        if response_type == '2' and resp[0] == g.session_params['dial_left'] and not locked:
            # Dont use threshold on quetion type 3
            # if question_type != '3':
            #     if (last_key == g.session_params['dial_left']) and (DIAL_LEFT_LIMIT <= g.DIAL_RATING_LIMIT):
            #         DIAL_LEFT_LIMIT += 1
            #         continue
                
            #     last_key = g.session_params['dial_left']
            #     # Reset DIAL LIMIT
            #     DIAL_LEFT_LIMIT = 0
            if marker_pos >= 0:
                marker_pos -= 1
            g.slider.markerPos = marker_pos
            StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['RATING_DIAL_RESPONSE'], g.clock.getTime(), str(g.clock.getTime() - g.trial_onset), resp[0],str(g.slider.markerPos), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

        if response_type == '2' and resp[0] == g.session_params['dial_right'] and not locked:
            # if question_type != '3':
            #     if (last_key == g.session_params['dial_right']) and  (DIAL_RIGHT_LIMIT <= g.DIAL_RATING_LIMIT):
            #         DIAL_RIGHT_LIMIT += 1
            #         continue
            #     last_key = g.session_params['dial_right']
            #     DIAL_RIGHT_LIMIT = 0
            if marker_pos <= len(g.slider.ticks) - 1:
                marker_pos += 1
            g.slider.markerPos = marker_pos
            StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['RATING_DIAL_RESPONSE'], g.clock.getTime(), str(g.clock.getTime() - g.trial_onset), resp[0],str(g.slider.markerPos), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

        if response_type == '2' and resp[0] == g.session_params['dial_select']:
            # Locked in 
            # write to file
            g.slider.marker.fillColor = 'red'  # fill the Marker Circle after subject locks in
            # g.slider.color = 'red' # color is not a slider attribute
            last_key = g.session_params['dial_select']
            locked = True
            StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['RATING_DIAL_LOCKED'], g.clock.getTime(), str(g.clock.getTime() - g.trial_onset), resp[0],str(g.slider.markerPos), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            pass

    g.slider = None
            

            


def do_one_trial(idx):
    """
    Function for 1 trial

    Parameters
    ----------
    idx : int, rquired
        The integer or trial number, used to grab duration, stim, file, etc from already made array
    """
    g.hand.ori = 50 # All start at 45 degree
    g.win.flip()

    trial_start_time = g.clock.getTime()
    
    # Mediai Types
    # Audio = 0, Video=1 , Picture=2, Rating_Identity=3, Rating_Valence=4, Rating_Arousal=5, Fixation = 6
    media_type = g.trial_types[idx][2] 

    print('%i %s' % (idx, g.trial_types[idx]))
    g.trial_onset = g.clock.getTime()
    StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['TRIAL_ONSET'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])


    # next Trial Start
    media_duration = 6 # default

    event.clearEvents()
    # Simulus Presentation based on media type
    # Audio
    if media_type == '0':
        media_duration = g.stims[idx].getDuration()
        # Next Trial Start
        g.ideal_trial_start = g.ideal_trial_start + media_duration
        g.fixation.color = 'yellow'
        g.stims[idx].play()
        # print(g.stims[idx].__dict__)
        StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['AUDIO_ONSET'], g.clock.getTime(), 'NA', str(media_duration), g.stims[idx].fileName, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        while g.clock.getTime() <= trial_start_time + media_duration:
            g.fixation.draw() # Show stim
            if dial_stimuli(idx) == 'skip': break

    # Video
    if media_type == '1':
        media_duration = g.stims[idx].duration
        # Next Trial Start
        g.ideal_trial_start = g.ideal_trial_start + media_duration
        g.stims[idx].draw()
        # print(g.stims[idx].__dict__)
        StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['VIDEO_ONSET'], g.clock.getTime(), 'NA', str(media_duration), g.stims[idx].filename, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        while g.stims[idx].status != visual.FINISHED:
            g.stims[idx].draw()
            if dial_stimuli(idx) == 'skip': break
            #g.win.flip()

    # Image
    if media_type == '2':
        media_duration = 6 
        # Next Trial Start
        g.ideal_trial_start = g.ideal_trial_start + media_duration
        # print(g.stims[idx].__dict__)
        StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['IMAGE_ONSET'], g.clock.getTime(), 'NA', str(media_duration), g.stims[idx]._imName, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        while g.clock.getTime() <= trial_start_time + media_duration:
            g.stims[idx].draw() # Show stim
            k = event.getKeys(keyList = ['escape', 'z'])
            if k and k[0] == 'escape': raise StimToolLib.QuitException()
            if k and k[0] == 'z': break
            g.win.flip()

    # Rating,
    # 3, 4, 5
    if media_type == '3' or media_type == '4' or media_type == '5':
        rating_duration = float(g.iti_durations[idx]) 
        g.ideal_trial_start = g.ideal_trial_start + rating_duration
        ttype = g.trial_types[idx]
        do_rating(ttype, rating_duration, idx)

    
    # Fixation ITI
    if media_type == '6':
        iti_duration = float(g.iti_durations[idx])
        g.ideal_trial_start = g.ideal_trial_start + iti_duration
        g.fixation.color = 'white'
        g.win.flip()
        now = g.clock.getTime()
        StimToolLib.mark_event(g.output,g.trial,g.trial_types[idx], event_types['FIXATION_ONSET'], g.clock.getTime(), 'NA', 'NA', str(iti_duration), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        while g.clock.getTime() <= g.ideal_trial_start:
            
            # Allow escape
            k = event.getKeys(['escape'])
            if k and k[0] == 'escape': raise  StimToolLib.QuitException()
            g.fixation.draw()
            g.win.flip()

        
def initialize_stimulus():
    """
    Create array of the psychopy stimulus
    
    Returns
    Array of psychopy image/sound/or video
    """
    g.stims = []

    for idx,trial_type in enumerate(g.trial_types):
        stim_path = g.stim_paths[idx] # eg.g media/fold1/stimfile.png
        media_type = trial_type[2]

        full_stim_path = os.path.join(os.path.dirname(__file__),stim_path)
        print(full_stim_path)

        if media_type == '0':
            # Media type 0 is Audio
            # Size is the screen_x,screen_y
            g.stims.append(sound.Sound(value =full_stim_path, volume = g.volume ))
            
        elif media_type == '1':
            # Media type 1 is Video
            g.stims.append(visual.MovieStim3(g.win, full_stim_path, size=[g.session_params['screen_x'], g.session_params['screen_y']],
                       flipVert=False, flipHoriz=False, loop=False, units='pix', pos=[0, 0], volume = g.volume))
        elif media_type == '2':
            # Media type 2 is Picture
            g.stims.append(visual.ImageStim(g.win, image = full_stim_path, units = 'pix', size = [g.session_params['screen_x'], g.session_params['screen_y']] ))

        else:
            # Still append, its probaably a ratings trial
            g.stims.append('None')


    return g.stims





def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/NC.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        #StimToolLib.mark_event(g.output,g.trial,'NA', 'NA', event_SK_END'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
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
        myDlg = gui.Dlg(title="NC")
        myDlg.addField('Run Number', choices=schedules, initial=str(g.run_params['run']))
    
        
        #myDlg.addField('CS Order', choices=['0', '1'], initial=cs_order) #only ask for the order if it hasen't been picked already--to avoid the operator accidentally changing it
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1#the user hit cancel so exit 

        g.run_params['run'] = thisInfo[0]
        
        #if len(thisInfo) > 1: #just got a CS+/- order from dialogue box--save it to a file
        #    cs_order = thisInfo[1]
        #    StimToolLib.write_var_to_file(param_filename, 'order', cs_order)


   
    StimToolLib.general_setup(g, winType = 'pyglet')

    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    
    g.prefix = StimToolLib.generate_prefix(g)
    g.subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '_' + g.run_params['param_file'])

    print("g.run_params['run'] = %s" %  g.run_params['run'] )
   

    
    # # If Ranomizer just generated
    if 'Randomizer' in g.run_params['run_id']:

        # A = Cultral Audo
        # B = Comparator Audio
        # C = Cultural Video
        # D = Comparator Video
        possible_run_orders = [
            ['A', 'B', 'C', 'D'],
            ['B', 'A', 'C', 'D'],
            ['A', 'B', 'D', 'C'],
            ['B', 'A', 'D', 'C'],
        ]
        chosen = random.sample(possible_run_orders, 1)[0]
        StimToolLib.write_var_to_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'run_order', ','.join(chosen))
        return

    if '_RX_' in g.run_params['run']:
        # Need to use the order
        print('GETTING RUN ORDER FROM PARAMS')
        try:
            run_order = StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'run_order').split(',')
        except:
            StimToolLib.error_popup('Could not read run order parameter from ' + g.subj_param_file + '. Did you run the ranndomizer?')
        
        print("RUN ORDER: ")
        print(run_order)

        # Set the run schdule based on the order
        if '_RX_A' in g.run_params['run']:   g.run_params['run'] = g.run_params['run'].replace('_RX_A','_RX_%s' % run_order[0] )
        elif '_RX_B' in g.run_params['run']: g.run_params['run'] = g.run_params['run'].replace('_RX_B','_RX_%s' % run_order[1] )
        elif '_RX_C' in g.run_params['run']: g.run_params['run'] = g.run_params['run'].replace('_RX_C','_RX_%s' % run_order[2] )
        elif '_RX_D' in g.run_params['run']: g.run_params['run'] = g.run_params['run'].replace('_RX_D','_RX_%s' % run_order[3] )
        
        print("NEW g.run_params['run'] = %s" % g.run_params['run'] )
        # Getting New Params 
        # Uncomment below if we think we want to grap all the run paramatesrs as well. Proabably unlikely since instructions we want the same
        #StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), g.run_params['run'][0:-9] + '.params'), g.run_params)


    print("RUN PARAMS")
    print(g.run_params)

    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_FC_Schedule' + str(g.run_params['run']) + '.csv')
    g.trial_types,blank,g.iti_durations, g.stim_paths = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    
    start_time = data.getDateStr()

    
    g.volume = StimToolLib.get_var_from_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'volume') #should have been set by volume workup run first
    if g.volume == None:
        StimToolLib.error_popup('Could not read volume parameter from ' + g.subj_param_file + '. Did you run the volume workup first?')

    
    
    fileName = os.path.join(g.prefix + '.csv')
    #subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['param_file'])
    #g.prefix = 'FC-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Version_2. Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + ',TrialTypes X_X X[0] -> Cultural|Comparator|Rating_Dial|Rating_Button (0|1|2|3); X[1]:Stimuli Type 0-> Audio;1-> Video; 2-> Picture; 3->Rating_Identity; 4-> Rating_Valence; 5-> Rating_Arousal, volume=' + str(g.volume) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    

    text_height = 80
    
    # Task Media Only used for this task
    g.fixation = visual.TextStim(g.win, text = '+', units = 'norm', color = 'white', pos = (0,0), height = .4)
    g.stim_text = visual.TextStim(g.win, text = 'Playing Audio', units = 'norm', pos = (0,0), color = 'white', height = .4)

    # DIal Components
    g.DIAL_LOC_POS = (.9 * (g.session_params['screen_x']/2), -.9 * (g.session_params['screen_y'] /2))
    g.arc = visual.ImageStim(g.win, image = os.path.join(os.path.dirname(__file__),'media','arc_with_anchors_100.png'), units = 'pix', pos = g.DIAL_LOC_POS)
    g.hand = visual.ImageStim(g.win, image = os.path.join(os.path.dirname(__file__),'media','left_hand.png'), units = 'pix', pos = g.DIAL_LOC_POS, ori=50)

    g.GAUGE_LOC_POS = (.95 * g.session_params['screen_x'], -.85 * g.session_params['screen_y'])
    g.gauge_text = visual.TextStim(g.win, text = g.hand.ori, color = 'white', pos = g.GAUGE_LOC_POS)
 
    # Ratings Questions stuff
    g.rating_question = visual.TextStim(g.win, text = '', units = 'norm', pos = (0,.7), color = 'white',height = .15, wrapWidth=1.5 )
    g.slider = None
    
    # SAM Faces
    g.calm_scale = visual.ImageStim(g.win, image = os.path.join(os.path.dirname(__file__),'media','calm_scale_with_dots.png'), units = 'norm', size = (1.8,.6), interpolate = True, pos = (0,.1))
    g.happy_scale = visual.ImageStim(g.win, image = os.path.join(os.path.dirname(__file__),'media','happy_scale_with_dots.png'), units = 'norm', size = (1.8,.6), interpolate = True, pos = (0,.1))

    # Get the String Array List to show letters
    #print g.trial_types
    g.iti_durations = g.iti_durations[0]
    g.stim_paths = g.stim_paths[0]


    #print(g.stim_paths)
    # hide the mouse
    if g.mouse: g.mouse.setVisible(False)

    
    # Intialize the Stimulus Depending on the type
    initialize_stimulus()

    print(g.stims)

    StimToolLib.task_start(StimToolLib.NCAIR_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output,'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    #timToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    #StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    response_type_param = 'dial'
    try:
        response_type_param = g.run_params['response_type']
    except:
        # Probably doesn't have the repsonse_type params
        pass

    if response_type_param == 'dial':
        StimToolLib.run_instructions_dial(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    else:
        StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)

    g.trial = 0
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win, five_only = True)

    else:
        StimToolLib.wait_start(g.win)
    g.win.flip()
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output,'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    g.ideal_trial_start = instruct_end_time

    # Wait 8 seconds after scanner start
    while g.clock.getTime() <= instruct_end_time + 8:
        g.fixation.draw()
        g.win.flip()
        k = event.getKeys(['escape', 'z'])
        if k:
            if k[0] == 'escape': raise StimToolLib.QuitException()
            if k[0] == 'z': break
        
    #####StimToolLib.just_wait(g.clock, g.clock.getTime() + 8)
    g.ideal_trial_start = instruct_end_time + 8

    indices = range(len(g.trial_types))
    g.trial = 0
    for idx in  indices:
        do_one_trial(idx)

        g.trial = g.trial + 1
    StimToolLib.just_wait(g.clock, g.clock.getTime() + 1) #wait 1 second so the total task length is an even number of seconds and ends on a TR
