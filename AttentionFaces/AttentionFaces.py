
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

event_types = {
    'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'TRIAL_ONSET': 3,
    'FIXATION_ONSET':4, 
    'STIM_ONSET':5, 
    'RESPONSE':6, 
    'OUTCOME': 7,
    'TASK_END':StimToolLib.TASK_END}


    
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
    g.ideal_trial_start = g.ideal_trial_start + g.face_duration + iti_duration # netx ideal trial start
    
    # Set sizes
    g.stim_files[idx].units = 'norm'
    g.stim_files[idx].size = (.6,1)
    g.stim_text.setHeight(.1)

     # Set the text to the string
    
    g.stim_text.setText(text =  g.stim_letters[idx])
    g.stim_text.bold = True
    print(g.stim_text)

    stim_start_time = g.clock.getTime()
    
    event.clearEvents() #clear old keypresses
    responded = False
    response_result = 0
    result = 0
    response_time = 'NA'

    stim_marked = False
    fixation_marked = False
    while g.clock.getTime() <= g.ideal_trial_start:

        # Draw the Face and String if time under .2
        if g.clock.getTime() <= stim_start_time + g.face_duration:
            g.stim_files[idx].draw()
            g.stim_text.draw()
            g.win.flip()
            if not stim_marked:
                now = g.clock.getTime()
                StimToolLib.mark_event(g.output,g.trial, g.trial_type, event_types['STIM_ONSET'], stim_start_time, 'NA',g.stim_files[idx]._imName , g.stim_letters[idx], g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                stim_marked = True
        else:
            # ELse draw the fixation
            g.fixation.draw()
            g.win.flip()
            if not fixation_marked:
                fixation_start_time = g.clock.getTime()
                StimToolLib.mark_event(g.output,g.trial, g.trial_type, event_types['FIXATION_ONSET'], fixation_start_time, 'NA', 'NA', str(iti_duration), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                fixation_marked = True
        resp = event.getKeys([g.session_params['left'], g.session_params['right'], 'escape'])
        if resp: #subject pressed a key
            if resp[0] == "escape":
                raise StimToolLib.QuitException()
            
            # Get Respose anytime a button is pressed
            now = g.clock.getTime()
            if resp[0] == g.session_params['left']:
                response_result = 1
                key_response = 0 # left is always 0
            else:
                response_result = 2
                key_response = 1 # right is always 1
            response_time  = now - stim_start_time
            if correct_response == response_result: result = 1 # 1 if correct, 0 if incorrect
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE'], now, response_time, key_response, result, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            responded = True
            
    
    end_time = g.clock.getTime()
    # Last Ooutcome
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['OUTCOME'], end_time, response_time,response_result,result, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])



def get_string_letters():
    """
    Returns array of letter stimulus to dispay over the face

    Return
    ------
    string_letters : Array
        The string letters that will be displayed
    """
    string_letters = []

    for idx in range(len(g.trial_types)):
        trial_type = g.trial_types[idx]
        load_condition = trial_type[0]
        response = trial_type[2]
        face_condition = trial_type[4]

        # Intialize Variables
        target_letter = ''
        letters = []
        if response == '1': target_letter = 'N'
        if response == '2': target_letter = 'X'

        # Load condition of 1 means to shuffle
        if load_condition == '1':
            letters = ["H","K","M","W","Z"]
            letters.append(target_letter) # Add either N or X
            random.shuffle(letters)
        else:
            # Means all characters are the same
            letters = [ target_letter for x in range(6)]

        string_letters.append(' '.join(letters))

    return string_letters

def add_second_intervals():
    """
    Add 2 seconds to the iti durations

    Return
    ------
    None
    """

    for idx in range(1, len(g.iti_durations) + 1 ):
        if (idx % 4 == 0) and (idx != 0):
            g.iti_durations[idx - 1] = g.iti_durations[idx - 1] + 2000.0

        


def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/AF.Default.params', {})
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
    StimToolLib.general_setup(g)
    volume = 1 #may need to change this if we decide to use different volumes for different subjects
    
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_FC_Schedule' + str(g.run_params['run']) + '.csv')
    g.trial_types,g.stim_files,g.iti_durations, junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    
    start_time = data.getDateStr()
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    
    g.prefix = StimToolLib.generate_prefix(g)
    subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['param_file']) #will store Blue_Pull in subject specific parameter file
    
    
    fileName = os.path.join(g.prefix + '.csv')
    #subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['param_file'])
    #g.prefix = 'FC-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + ',Trial Types are coded as follows: 0->left arrow; 1->right arrow; 2->CS-; 3->CS+; 4->CS+&US, volume=' + str(volume) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    

    text_height = 80
    
    # Task Media Only used for this task
    g.fixation = visual.TextStim(g.win, text = '.', units = 'norm', pos = (0,0))
    g.stim_text = visual.TextStim(g.win, text = '', units = 'norm', pos = (0,.1), color = 'black', height = .064, bold = True)
    #print(os.path.join(os.path.dirname(__file__), 'media', 'Bevan.ttf'))
    #g.stim_text.fontFiles = ['C:\stimtool3_james_develop\AttentionFaces\media\Bevan.ttf']
    #g.stim_text.font = 'Bevan'
    g.stim_text.bold = True
    
    # Set the positon of the stim text if its' in practice 
    if g.run_params['practice']:
        g.stim_text.pos = (0,0)
    
    # Get the String Array List to show letters
    #print g.trial_types
    g.iti_durations = g.iti_durations[0]
    g.stim_files = g.stim_files[0]
    #print 'durations before:'
    #print g.iti_durations

    g.stim_letters = get_string_letters()

    # Functiont to add 2s second intervals every 4 trials
    add_second_intervals()
    #print 'durations after:'
    #print g.iti_durations



    StimToolLib.task_start(StimToolLib.ATTENTION_FACES_CODE, g)
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
    StimToolLib.just_wait(g.clock, g.clock.getTime() + 8)
    g.ideal_trial_start = instruct_end_time + 8

    for idx,ttype in enumerate(g.trial_types):
        do_one_trial(idx)
        #print('idx: %i, trial type: %s, image: %s, duration: %s' % (idx, str(ttype), g.stim_files[idx]._imName, g.iti_durations[idx]))
        g.trial = g.trial + 1
    
    g.win.flip()
    print("WATING..")
    now = g.clock.getTime()
    #StimToolLib.just_wait(g.clock, now + 1) #wait 1 second so the total task length is an even number of seconds and ends on a TR

    # if '-R3-' in g.run_params['run_id']:
    #     g.last_slide = visual.ImageStim(g.win, image = os.path.join(os.path.dirname(__file__), 'media', 'swap_slide.png'), units = 'pix', pos = (0,0), size = (g.session_params['screen_x'], g.session_params['screen_y']))
    #     g.last_slide.draw()
    #     g.win.flip()
    #     print("WATING ON LAST SLIDE")
    #     StimToolLib.just_wait(g.clock, now + 10) # show for 10 seconds
    g.win.flip()
    print("END OF THE LINE")
