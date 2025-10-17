
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

event_types = {
    'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'TRIAL_ONSET':3,
    'FIXATION':4,
    'GO_LETTER_ONSET':5,
    'NOGO_LETTER_ONSET':6,
    'RESPONSE_GO':7,
    'RESPONSE_NOGO':8,
    'BLANK_ONSET':9,
    'GNG_START': 22,
    'GNG_END': 23,
    'TASK_END':StimToolLib.TASK_END 
    }

def do_one_trial(letter, fixation, stim_duration, blank_duration, gonogo_flag):

    # FIXATION
    g.fixation.draw()
    g.win.flip() # start on screen refresh
    mark_time = trial_start = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION'], mark_time, 'NA', 'NA', fixation, g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    for x in range(int(round(fixation/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the fixation and draws the letter
        g.fixation.draw()
        g.win.flip()

    # LETTER PRESENTATION AND RESPONSE
    # prepare and draw the letter stim so that it draws on the next flip
    letter_stim = g.letter_stims[letter]
    letter_stim.draw()
    event.clearEvents()
    g.win.flip() # end fixation on refresh and begin letter on same refresh
    resp_marked = False
    mark_time = g.clock.getTime()
    g.mouse.clickReset()
    if gonogo_flag == 'G':
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['GO_LETTER_ONSET'], mark_time, 'NA', 'NA', letter, g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    else:
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['NOGO_LETTER_ONSET'], mark_time, 'NA', 'NA', letter, g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    #___________ BETTER DISPLAY TIMING
    for x in range(int(round(stim_duration/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh clears the letter
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        # resp = event.getKeys([g.session_params['select'], g.session_params['left'], g.session_params['right'], g.session_params['up'], g.session_params['down']], timeStamped=g.clock)
        resp, resptimes = g.mouse.getPressed(getTime = True)
        print(resp)
        if 1 in resp and not resp_marked:
            if gonogo_flag == 'G':
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE_GO'], g.clock.getTime(), max(resptimes), 'NA', gonogo_flag, g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
            else:
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE_NOGO'], g.clock.getTime(), max(resptimes), 'NA', gonogo_flag, g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
            event.clearEvents()
            resp_marked = True
        letter_stim.draw()
        g.win.flip()
    g.win.flip() # clear letter on refresh
    mark_time = g.clock.getTime()

    # BLANK SCREEN
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BLANK_ONSET'], mark_time, 'NA', 'NA', blank_duration, g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    for x in range(int(round(blank_duration/g.win.monitorFramePeriod)) - 1): # stop one refresh early so that the following refresh shows the next fixation
        # g.fixation.draw()
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
        myDlg = gui.Dlg(title="GNG")
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
    letters = trial_types
    fixations = durations[0]
    stim_durations = durations[1]
    blank_durations = durations[2]
    gonogo_flags = junk[0]

    StimToolLib.close_output()

    #set up stimuli
    g.win_ratio = g.win.size[0]/g.win.size[1]
    g.test_stim = visual.TextStim(g.win, text='TESTING SCREEN REFRESH RATE...', height=0.25, pos=[0,0], units='norm', color='white')
    g.break_stim = visual.TextStim(g.win, text='REST', height=0.25, pos=[0,0], units='norm', color='white')
    g.end_stim = visual.TextStim(g.win, text='Thank you for participating. Please wait.\n(ENTER to end)', height=0.15, pos=[0,0], units='norm', color='white')
    g.fixation = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/fixation.png'), pos=[0,0], size = [0.5,g.win_ratio*0.5], units='norm')
    g.letter_stims = {}
    for letr in set(letters):
        g.letter_stims[letr] = visual.TextStim(g.win, text=f'{letr}', height=0.5, pos=[0,0], units='norm', color='white')
    # g.box = visual.Rect(g.win, size=[0.52, 0.52], lineColor='white', fillColor='black', lineWidth=1, pos=[0,0], units='norm', opacity=1)

    StimToolLib.redirect_output(g.session_params)
    start_time = data.getDateStr()
    fileName = os.path.join(g.prefix + '.csv')
    
    g.output = open(fileName, 'w')

    g.mouse = event.Mouse(visible=False)
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.GONOGO_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])

    StimToolLib.run_instructions_mouse(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)

    g.trial = 0
    if g.session_params['scan'] == 'True':
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    instruct_end_time = g.clock.getTime()
    g.win.flip()
    test_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    if '_P' not in g.run_params['run']:
        StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['GNG_START'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])
    g.ideal_trial_start = instruct_end_time

    g.mouse = event.Mouse(visible=False)
    g.mouse.setVisible(0)

    for l,f,sd,bd,gng in zip(letters,fixations,stim_durations,blank_durations,gonogo_flags):
        g.trial_type = l

        g.start2 = timeit.default_timer()
        do_one_trial(l,f,sd,bd,gng)

        g.trial = g.trial + 1

    if 'R2' in g.run_params['run_id']:
        done = False
        while not done:
            g.end_stim.draw()
            g.win.flip()
            resp = event.getKeys(['return'])
            if resp:
                done = True
            StimToolLib.short_wait()

    StimToolLib.just_wait(g.clock, g.clock.getTime() + 4)
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['GNG_END'], instruct_end_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'], g.session_params['signal_serial'], g.session_params['serial_port_address'], g.session_params['baud_rate'])

    if not g.run_params['practice'] and 'R2' not in g.run_params['run_id']:
        g.break_stim.draw()
        g.win.flip()
        StimToolLib.just_wait(g.clock, g.clock.getTime() + 30)

    g.win.flip()
    g.msg.setColor([-1,-1,-1])
