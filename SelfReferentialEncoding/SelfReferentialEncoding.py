
import time
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui, sound
import numpy
import json
import timeit
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
        self.start = 0
        self.start2 = 0
        self.start3 = 0
        self.start4 = 0
        self.refresh_period_denom = 2 # try waiting half a frame before a flip to line up with the screen refresh (ex. g.win.monitorFramePeriod/refresh_period_denom)
        self.resp_dict = {}

event_types = {
    'INSTRUCT_ONSET':11,
    'TASK_ONSET':12,
    'FIXATION':13,
    'WORD_ONSET_POS':14,
    'WORD_ONSET_NEG':15,
    'BLANK_ONSET':16,
    'QUESTION_ONSET':17,
    'RESPONSE_YES':18,
    'RESPONSE_NO':19,
    'TASK_END':StimToolLib.TASK_END 
    }

def do_one_trial(word, fixation, stim_duration, blank_duration,posneg):

    # _________ FIXATION _________ 
    g.fixation.draw()
    g.win.flip() # start on screen refresh
    mark_time = g.clock.getTime()

    # mark the fixation event and then wait for fixation period
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION'], mark_time, 'NA', 'NA', fixation, g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    for x in range(int(round(fixation/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the fixation and draws the word
        g.fixation.draw()
        g.win.flip()

    # _________ WORD PRESENTATION _________ 
    # prepare and draw the letter stim so that it draws on the next flip
    word_stim = g.word_stims[word]
    word_stim.draw()
    g.win.flip() # end fixation on refresh and begin letter on same refresh
    mark_time = g.clock.getTime()

    # mark the word onset event and then wait for stim_duration period (this waiting occurs on flip intervals)
    if posneg == '1':
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['WORD_ONSET_POS'], mark_time, 'NA', 'NA', word, g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    else:
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['WORD_ONSET_NEG'], mark_time, 'NA', 'NA', word, g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    for x in range(int(round(stim_duration/g.win.monitorFramePeriod)) - 1): # stop one refresh early, so that the following refresh clears the word
        word_stim.draw()
        g.win.flip()

    # _________ BLANK SCREEN _________ 
    g.win.flip() # clear letter on screen refresh and blank screen start
    mark_time = g.clock.getTime()

    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BLANK_ONSET'], mark_time, 'NA', 'NA', blank_duration, g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    for x in range(int(round(blank_duration/g.win.monitorFramePeriod)) - 1): # stop one refresh early, so that the following refresh starts the blank
        g.win.flip()

    # _________ QUESTION PRESENTATION AND RESPONSE _________ 
    # prepare question and yes/no draw for after blank screen
    g.yes_text.draw()
    g.no_text.draw()
    g.question_text.draw()
    event.clearEvents()
    g.win.flip() # end fixation on refresh and begin question on same refresh
    done = False
    resp_marked = False
    mark_time = g.clock.getTime()
    g.mouse.clickReset()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['QUESTION_ONSET'], mark_time, 'NA', 'NA', 'Does this word describe you?', g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    while not done: # stop a bit before next refresh
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        # resp = event.getKeys([g.session_params['left'], g.session_params['right']], timeStamped=g.clock)
        resp, resptimes = g.mouse.getPressed(getTime = True) # resp = ([1=leftclick,1=midclick,1=rightclick],[resptimeleft,resptimemid,resptimeright])
        print(resp)
        if resp[0] == 1 or resp[2] == 1 and not resp_marked:
            response_time = g.clock.getTime() - mark_time
            if resp[0] == 1:
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE_YES'], g.clock.getTime(), resptimes[0], 'NA', 'YES', g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
            elif resp[2] == 1:
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE_NO'], g.clock.getTime(), resptimes[2], 'NA', 'NO', g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
            event.clearEvents()
            resp_marked = True
            done = True
        g.yes_text.draw()
        g.no_text.draw()
        g.question_text.draw()
        g.win.flip()

def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/GNG.Default.params', {})
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
        myDlg = gui.Dlg(title="SRE")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1 #the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]

    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)

    print("TESTING")
    print(param_file)

    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    StimToolLib.general_setup(g)
    g.win.flip()
    g.win.flip()

    trial_types,images,durations,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    words = trial_types
    fixations = durations[0]
    stim_durations = durations[1]
    blank_durations = durations[2]
    posneg = junk[0]

    StimToolLib.close_output()

    #set up stimuli
    g.win_ratio = g.win.size[0]/g.win.size[1]
    g.test_stim = visual.TextStim(g.win, text='TESTING SCREEN REFRESH RATE...', height=0.25, pos=[0,0], units='norm', color='white')
    g.break_stim = visual.TextStim(g.win, text='REST', height=0.25, pos=[0,0], units='norm', color='white')
    g.fixation = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/fixation.png'), pos=[0,0], size = [0.5,g.win_ratio*0.5], units='norm')
    g.word_stims = {}
    for word in set(words):
        g.word_stims[word] = visual.TextStim(g.win, text=f'{word}', height=0.25, pos=[0,0], units='norm', color='white')
    g.yes_text = visual.TextStim(g.win, text='YES', height=0.15, pos=[-0.5,-0.5], units='norm', color='white')
    g.no_text = visual.TextStim(g.win, text='NO', height=0.15, pos=[0.5,-0.5], units='norm', color='white')
    g.question_text = visual.TextStim(g.win, text='Does this word describe you?', height=0.25, pos=[0,0], units='norm', color='white')
    # g.box = visual.Rect(g.win, size=[0.52, 0.52], lineColor='white', fillColor='black', lineWidth=1, pos=[0,0], units='norm', opacity=1)

    StimToolLib.redirect_output(g.session_params)
    start_time = data.getDateStr()
    fileName = os.path.join(g.prefix + '.csv')
    
    g.output = open(fileName, 'w')

    g.mouse = event.Mouse(visible=False)

    g.resp_dict[g.session_params['left']] = 'YES'
    g.resp_dict[g.session_params['right']] = 'NO'
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.GONOGO_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])

    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)

    g.trial = 0
    if g.session_params['scan'] == 'True':
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    instruct_end_time = g.clock.getTime()
    g.win.flip()
    test_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    g.ideal_trial_start = instruct_end_time

    g.mouse = event.Mouse(visible=False)
    g.mouse.setVisible(0)

    for w,f,sd,bd,pn in zip(words,fixations,stim_durations,blank_durations,posneg):
        g.trial_type = w

        do_one_trial(w,f,sd,bd,pn)

        g.trial = g.trial + 1

    g.break_stim.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.clock.getTime() + 30)
    g.msg.setColor([-1,-1,-1])
