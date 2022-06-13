
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
        self.face_duration = 1 # 0.2
        self.left_pos = (-.4, -.4) # location of the YES
        self.righ_pos = (.4, -.4) # location of the NO

event_types = {
    'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'TRIAL_ONSET': 3,
    'FIXATION_ONSET':4, 
    'STIM_ONSET':5,
    'CHOICE_ONSET': 6,
    'RESPONSE':7, 
    'OUTCOME': 8,
    'TASK_END':StimToolLib.TASK_END}




def get_stim_instruct(ttype):
    """
    Returns the text strin given trial type
    """
    if ttype == '1':
        return 'I am'
    if ttype == '2':
        return 'My best friend is'
    if ttype == '3':
        return 'This word is positive'
    return ''

def do_one_trial(idx):
    """
    Function for 1 trial

    Parameters
    ----------
    idx : int, rquired
        The integer or trial number, used to grab duration, stim, file, etc from already made array
    """
    g.win.flip()

    trial_start_time = g.clock.getTime()
    g.trial_type = g.trial_types[idx]
    correct_response = int(g.trial_type[2])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], trial_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    iti_duration = float(g.iti_durations[idx]) / 1000 # Divide by 1000 since it's in ms
    g.ideal_trial_start = g.ideal_trial_start + 6 # netx ideal trial start
    

     # Set the text to the string
    
    g.cue_instruct.setText(text = get_stim_instruct(g.trial_type[0])) # set instruction question
    g.stim_text.setText(text = g.cues[idx]) # set word
    g.stim_text.bold = True
    #print(g.stim_text)

    stim_start_time = g.clock.getTime()
    
    event.clearEvents() #clear old keypresses
    responded = False
    response_result = 0
    result = 0
    response_time = 'NA'

    word_respnose = 'NA'
    
    question_shown = False
    question_with_cue_shown = False

    # Flags for marking events
    stim_marked = False
    choice_marked = False


    while g.clock.getTime() <= g.ideal_trial_start:

        # Draw the question text for 1.5seconds

        g.cue_instruct.draw()

        
        # Draw the question and the cue word
        if (g.clock.getTime() > stim_start_time + 2.5):
            g.stim_text.draw()

            g.yes.draw()
            g.no.draw()

            question_with_cue_shown = True
           
        if responded:
            g.choice_square.draw()
            #g.x_mark.draw()

        resp = event.getKeys([g.session_params['left'], g.session_params['right'], 'escape'])
        if resp: #subject pressed a key
            if resp[0] == "escape":
                raise StimToolLib.QuitException()
            
            # Get Respose anytime a button is pressed
            now = g.clock.getTime()

            # Make sure its after cue is shown
            if question_with_cue_shown:

                response_time  = now - stim_start_time

                if resp[0] == g.session_params['left']:
                    response_result = 1
                    key_response = 0 # left is always 0
                    word_respnose = 'Yes'
                    g.choice_square.pos = g.left_pos
                else:
                    response_result = 2
                    key_response = 1 # right is always 1
                    word_respnose = 'No'
                    g.choice_square.pos = g.righ_pos
                responded = True

                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE'], now, response_time, key_response, word_respnose, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            
            if correct_response == response_result: 
                result = 1 # 1 if correct, 0 if incorrect
                
            
        g.win.flip()

        # Mark events
        if not stim_marked:
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['STIM_ONSET'], g.clock.getTime(), 'NA', 'NA', g.cue_instruct.text, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            stim_marked = True

        if question_with_cue_shown and not choice_marked:
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['CHOICE_ONSET'], g.clock.getTime(), 'NA', 'NA', g.stim_text.text, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            choice_marked = True

            
    
    end_time = g.clock.getTime()
    # Last Ooutcome
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['OUTCOME'], end_time, response_time,response_result,result, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])


    # ISI
    g.win.flip()
    g.fixation.draw()
    g.win.flip()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION_ONSET'], g.clock.getTime(), 'NA', 'NA', str(iti_duration), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.just_wait(g.clock,end_time + iti_duration )

    # Add ideal trial_start accoutninf for iti duration
    g.ideal_trial_start = g.ideal_trial_start + iti_duration




def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/AT.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_END'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
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
        myDlg = gui.Dlg(title="AF")
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
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    
    StimToolLib.general_setup(g)
    g.prefix = StimToolLib.generate_prefix(g)
    volume = 1 #may need to change this if we decide to use different volumes for different subjects
    adjective_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID']+ '-' +g.session_params['session_id'] + '-__AT_params'  + '.txt')
    # Verify the subject is valid
    if '_RP_' in g.run_params['run']:
        id_number = ''

        # Counterbalance based on subject ID
        while True:
            # check if subject id number is a number, open a popup if it's not
            try:
                id_number = int(g.session_params['SID'][2:])
                break
            except:
                myDlg = gui.Dlg(title="Subject ID Correction")
                myDlg.addText('ID must be 5 characters and end in 3 numbers, apperently it does not')
                myDlg.addField('ID', initial='')
                myDlg.show()  # show dialog and wait for OK or Cancel
                thisInfo = myDlg.data
                sid = thisInfo[0]
                g.session_params['SID'] = sid

        
        # Counterbalancing
        # Rules
        # 1. Even subject see order A/B in visit 1, sees C/D in visit 2
        # 2. Odd subjects sess order C/D in visit 1, sees A/B in visit 1
        # 3. 50%s of the time, the order is flipped

        run_schedules = [
            'study-TaskDev_RA.schedule',
            'study-TaskDev_RB.schedule',
            'study-TaskDev_RC.schedule',
            'study-TaskDev_RD.schedule'
        ]

        possible_runs = []
        run_flipped = False

        # is Event subject
        if (id_number % 2) == 0:
            # is even
            print('is even subject')

            if 'V1' in g.session_params['session_id']:
                # for visit 1 use A/B
                possible_runs = [ run_schedules[0], run_schedules[1] ]
            else:
                # for visit 2 use C/D
                possible_runs = [ run_schedules[2], run_schedules[3] ]
        else:
            # is odd
            print('is odd subject')
            if 'V1' in g.session_params['session_id']:
                possible_runs = [ run_schedules[2], run_schedules[3] ]
            else:
                possible_runs = [ run_schedules[0], run_schedules[1] ]

        
        # At at this point, we should now have the right scedules
        # Flip the runs 1 more time 50%s of the time
        if random.random() < 0.5:
            possible_runs.reverse()
            run_flipped = True
            
        # Save run order to file
        print('saving run order file: %s' % adjective_param_file)
        StimToolLib.write_var_to_file(adjective_param_file, 'run_order', possible_runs)
        StimToolLib.write_var_to_file(adjective_param_file, 'run_flipped', run_flipped) # record if flipped

    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])

    # At this point, the schedules have been counterbalanced
    if '_R1_' in g.run_params['run']:
        
        run_order =  StimToolLib.get_var_from_file(adjective_param_file, 'run_order')
        print('Using run order from param file: %s' % run_order[0])
        schedule_file = os.path.join(os.path.dirname(__file__), run_order[0])
    
    if '_R2_' in g.run_params['run']:
        run_order =  StimToolLib.get_var_from_file(adjective_param_file, 'run_order')
        print('Using run order from param file: %s' % run_order[0])
        schedule_file = os.path.join(os.path.dirname(__file__), run_order[1])

    


    
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_FC_Schedule' + str(g.run_params['run']) + '.csv')
    g.trial_types,g.stim_files, g.iti_durations, g.cues = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    
    start_time = data.getDateStr()
    
    
    
    subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['param_file']) #will store Blue_Pull in subject specific parameter file
    
    
    fileName = os.path.join(g.prefix + '.csv')
    #subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['param_file'])
    #g.prefix = 'FC-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + ',Actual Schedule File:' + schedule_file+ ' , volume=' + str(volume) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    

    text_height = 80
    
    # Task Media Only used for this task
    g.fixation = visual.TextStim(g.win, text = '+', units = 'norm', pos = (0,0))
    g.cue_instruct = visual.TextStim(g.win, text = '', units = 'norm', pos = (0,.4))
    g.stim_text = visual.TextStim(g.win, text = '', units = 'norm', pos = (0,0))
    
    g.yes = visual.TextStim(g.win, text = 'YES', units = 'norm', pos = g.left_pos)
    g.no = visual.TextStim(g.win, text = 'NO', units = 'norm', pos = g.righ_pos)

    g.x_mark = visual.TextStim(g.win, text = 'X', units = 'norm', pos = (.2,-.2))
    g.choice_square = visual.Rect(g.win, width = .3, height = .2, units = 'norm', lineWidth=1, pos = (.2, -.4))

    
    # Get the String Array List to show letters    
    g.iti_durations = g.iti_durations[0]
    g.cues = g.cues[0]
    print('Trial Types')
    print(g.trial_types)
    print('Cues')
    print(g.cues)
    print('DURATIONS')
    print(g.iti_durations)


    StimToolLib.task_start(StimToolLib.ADJECTIVE_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    #timToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)


    g.trial = 0
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)

    else:
        StimToolLib.wait_start(g.win)
    g.win.flip()
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])


    g.ideal_trial_start = instruct_end_time

    # Wait 8 seconds after scanner start
    g.fixation.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.clock.getTime() + 10)
    g.ideal_trial_start = instruct_end_time + 10

    
    # Shuffle Schedule indexes
    trial_indexes = list(range(0, len(g.trial_types)))
    random.shuffle(trial_indexes)

    # Save sequency to the
    StimToolLib.write_var_to_file(adjective_param_file, 'order', trial_indexes)

    for idx in trial_indexes:
        do_one_trial(idx)
        #print('idx: %i, trial type: %s, image: %s, duration: %s' % (idx, str(ttype), g.stim_files[idx]._imName, g.iti_durations[idx]))
        g.trial = g.trial + 1
    
    # Wait 10 seconds lead out
    g.fixation.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.clock.getTime() + 10)
    g.ideal_trial_start = instruct_end_time + 10