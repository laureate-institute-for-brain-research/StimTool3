

import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.cues = None #shape cues
        self.text_cues = None #numerical cues under the shapes
        self.win = None #the window where everything is drawn
        self.resk = None #response keys
        self.clock = None #global clock used for timing
        self.target = None #target triangle stimulus
        self.x = None #X fixation stimulus
        self.o = None #O fixation stimulus
        self.wins = [0,0,0,0,0,0] #number of wins for this trial type
        self.losses = [0,0,0,0,0,0] #number of losses for this trial type
        self.calibrations = None #[begin_rt,begin_rt,begin_rt,begin_rt,begin_rt,begin_rt]#current calibrations for reaction times
        self.output = None #The output file
        self.rt_change = 0.02 #the amount the to change a calibration by
        self.this_trial_output = None #will contain the text output to print for the current trial
        self.result_msg = None
        self.total_reward = 0
        self.msg = None
        self.trial_type = None
        self.trial = None
        self.all_rts = [] #list of all rts, used to get calibration rt from practice session
        self.title = 'Money'
        self.total_wins = 0
        self.total_trials = 0
        
event_types = {'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'CUE_ONSET':3, #also codes cue_onset time and trial type
    'DELAY_ONSET':4, 
    'TARGET_ONSET':5, 
    'RESPONSE_PRESSED':6, 
    'TARGET_OFFSET':7, 
    'RESULT_ONSET':8,
    'TOTAL_REWARD':9,
    'FIXATION_ONSET':10,
    'TASK_END':StimToolLib.TASK_END}

def just_wait(end_time):
    while g.clock.getTime() < end_time:
        if event.getKeys(["escape"]):
            return -1


def update_calibration(trial_type):
    if g.wins[trial_type] + g.losses[trial_type] > 2:
        ratio = float(g.wins[trial_type])/(g.wins[trial_type] + g.losses[trial_type])
        print(ratio)
        if ratio > 0.66:
            g.calibrations[trial_type] = g.calibrations[trial_type] - g.rt_change
        else:
            g.calibrations[trial_type] = g.calibrations[trial_type] + g.rt_change
        
def fix_target(trial_type, delay):
    hit = False
    rxn_time = -1 #reaction time: will be -1 for early response
    responded = False #has the participant responded, whether before, during, or after the target
    update_calibration(trial_type) #update the target duration
    htime = -1 #response time (absolute time of button press)
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 4)
    #while g.clock.getTime() < g.ideal_trial_start + 4:
    #    if event.getKeys(["escape"]):
    #        raise StimToolLib.QuitException()
    key = event.getKeys(g.resk) #clear pressed keys so that a very early press is not counted
    while g.clock.getTime() < g.ideal_trial_start + 4 + delay:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        key = event.getKeys(g.resk) 
        if key and not responded:
            #participant responded too early: miss this trial_types
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE_PRESSED'], g.clock.getTime(), -1, 1, 0, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            responded = True
        StimToolLib.short_wait()
    g.target.draw()
    g.win.flip()
    time_target_shown = g.clock.getTime() #target shown right after g.win.flip() returns
    duration = g.calibrations[trial_type]
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TARGET_ONSET'], time_target_shown, 'NA', 'NA', duration, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #Since the target duration is pretty short, base its timing on the actual rather than ideal timing
    while g.clock.getTime() < time_target_shown + duration: #g.ideal_trial_start + 4 + delay + duration:
        if event.getKeys(["escape"]):
            return -1
        key = event.getKeys(g.resk) 
        if key and not responded:
            #if participant responded too early: miss this trial
            hit = True
            #record response time 
            htime = g.clock.getTime()
            rxn_time = htime - time_target_shown
            responded = True
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE_PRESSED'], htime, rxn_time, 1, 1, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        StimToolLib.short_wait()
    g.win.flip() #no longer display the target
    time_target_off = g.clock.getTime() #target no longer shown after g.win.flip() returns
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TARGET_OFFSET'], time_target_off, 'NA', 'NA', time_target_off - time_target_shown, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    while g.clock.getTime() < g.ideal_trial_start + 6:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
            #return -1
        key = event.getKeys(g.resk) 
        if key and not responded:
            #record response time 
            htime = g.clock.getTime()
            rxn_time = htime - time_target_shown
            responded = True
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE_PRESSED'], htime, rxn_time, 1, 0, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        StimToolLib.short_wait()
    if rxn_time > 0:
        g.all_rts.append(rxn_time) #keep track of all RTs for calibration from practice run
    print(rxn_time)
    if hit: #update win/loss counts
        g.wins[trial_type] = g.wins[trial_type] + 1
    else:
        g.losses[trial_type] = g.losses[trial_type] + 1
    return hit 
def draw_result_text(t_type, hit):
    #draw the appropriate text for the result
    #also update the total money earned
    if hit:
        if t_type == 0 or t_type == 1 or t_type == 2: #three loss conditions
            g.result_msg.setText("$0")
        if t_type == 3:
            g.result_msg.setText("+$0")
        if t_type == 4:
            g.result_msg.setText("+$1")
            g.total_reward = g.total_reward + 1
        if t_type == 5:
            g.result_msg.setText("+$5")
            g.total_reward = g.total_reward + 5
    else:
        if t_type == 3 or t_type == 4 or t_type == 5: #three win conditions
            g.result_msg.setText("$0")
        if t_type == 0:
            g.result_msg.setText("-$0")
        if t_type == 1:
            g.result_msg.setText("-$1")
            g.total_reward = g.total_reward - 1
        if t_type == 2:
            g.result_msg.setText("-$5")
            g.total_reward = g.total_reward - 5
    g.result_msg.draw()
    #g.this_trial_output = g.this_trial_output + ',' + str(g.total_reward)
    g.win.flip()
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESULT_ONSET'], now, 'NA', 'NA', g.result_msg.text, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TOTAL_REWARD'], now, 'NA', 'NA', g.total_reward, False, g.session_params['parallel_port_address'])
    
    
def do_one_trial(t_type, delay, iti):
    #g.this_trial_output = ''
    #show cue
    g.cues[t_type].draw()
    g.text_cues[t_type].draw()
    g.win.flip()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['CUE_ONSET'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 2)
    #show fixation
    g.x.draw()
    g.win.flip()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['DELAY_ONSET'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 4)
    hit = fix_target(t_type, delay)
    #show win/loss
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 6)
    #if just_wait(g.ideal_trial_start + 6)  == -1:
    #    return -1
    draw_result_text(t_type, hit)
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 8)
    #if just_wait(g.ideal_trial_start + 8)  == -1:
    #    return -1
    #show ITI
    g.o.draw()
    g.win.flip()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION_ONSET'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 8 + iti)
    #if just_wait(g.ideal_trial_start + 8 + iti)  == -1:
    #    return -1
    #g.output.write(g.this_trial_output+ '\n') 
    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/MID.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
        
    #show result
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_END'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.output.close()
    try:
        if g.run_params['practice']:
            StimToolLib.show_instructions(g.win, ["You hit " + str(g.total_wins) + ' out of  ' + str(g.total_trials) + ' targets.'])
        else:
            #maximum reward can be set
            print(g.total_reward)
            print(g.run_params['max_reward'])
            to_show = min(g.total_reward, g.run_params['max_reward'])
            StimToolLib.show_instructions(g.win, ["You Won $" + str(to_show) + ' so far!'])
            #StimToolLib.show_instructions(g.win, ["You Won $" + str(g.total_reward) + ' so far!'])
    except StimToolLib.QuitException:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status
def read_calibrations_history(parameter_file):
    g.calibrations = []
    g.wins = []
    g.losses = []
    for i in range(6):
        g.calibrations.append(StimToolLib.get_var_from_file(parameter_file, 'cal_' + str(i)))
        g.wins.append(StimToolLib.get_var_from_file(parameter_file, 'win_' + str(i)))
        g.losses.append(StimToolLib.get_var_from_file(parameter_file, 'loss_' + str(i)))
    g.total_reward = StimToolLib.get_var_from_file(parameter_file, 'total_reward')
    if g.total_reward == None: #this will be true if the calibrations file has not been created yet
        #for python 3, must initialize g.total_reward to something so that min(g.total_reward, g.run_params['max_reward']) doesn't throw an error
        g.total_reward = 0
        StimToolLib.error_popup('Cannot read calibration file.  Did you run a practice session first?')
        
def store_calibrations_history(parameter_file):
    for i in range(6):
        StimToolLib.write_var_to_file(parameter_file, 'cal_' + str(i), g.calibrations[i])
        StimToolLib.write_var_to_file(parameter_file, 'win_' + str(i), g.wins[i])
        StimToolLib.write_var_to_file(parameter_file, 'loss_' + str(i), g.losses[i])
    StimToolLib.write_var_to_file(parameter_file, 'total_reward', g.total_reward)
    
def run_try():  
#def run_try(SID, raID, scan, resk, run_num = 'Practice'):    
    
    #parameter_file = os.path.join(os.path.dirname(__file__), 'data', g.session_params['SID'] + '_MID.calibration')
    
    g.resk = [g.session_params['left'], g.session_params['right'], g.session_params['select']]#  resk.values() #since we don't care which response key is pressed, convert the dictionary to a list   
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="MID")
        myDlg.addField('Run Number', choices=schedules, initial=str(g.run_params['run']))
        myDlg.show()  # show dialog and wait for OK or Cancel
        thisInfo = myDlg.data
        if myDlg.OK:  # then the user pressed OK
            pass
        else:
            print('QUIT!')
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0] 
    StimToolLib.general_setup(g)
    
    
        
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['param_file'])
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_MID_Schedule' + str(g.run_params['run']) + '.csv')
    fileName = os.path.join(g.prefix + '.csv')
    g.output = open(fileName, 'w')
    print(subj_param_file)
    if g.run_params['practice']: #for the first run, use the RT from the dialogue and all wins/losses will start out at 0
        practice_calibration = 0.3
        g.calibrations = [practice_calibration, practice_calibration, practice_calibration, practice_calibration, practice_calibration, practice_calibration] #set practice calibration time to 300ms
    else: #otherwise, pick up where left off--this will generalize to more than 2 runs
        #read 6 calibrations, 6 win counts, 6 loss counts, total won so far
        read_calibrations_history(subj_param_file)
    
    
    trial_types,junk,durations,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    
    delays = durations[0]
    itis = durations[1]
    start_time = data.getDateStr()
    #g.prefix = 'MID-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' +  g.prefix + '.csv')
    
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  schedule_file + ',Event Codes:,' + str(sorted_events) + 'Trial Types:,0:-0,1:-1,2:-5,3:+0,4:+1,5:+5\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    
    #g.output.write('Trial_Type:0:-0_1:-1_2:-5_3:+0_4:+1_5:+5,Trial_Onset,Hit,Target_Duration,Target_Onset_Time,Target_Offset_Time,Target_Actual_Duration,Button_Press_Time,Reaction_Time:-1=no_response_-[float]:too_early,Total_Reward\n')
    trial_types = map(int, trial_types) #convert strings to ints to make indexing arrays easier
        
    #prepare the stimulus shapes
    #they will be in the right order so that trial type 0 -> cues[0], type 1 -> cues[1], etc.
    g.cues = []
    g.text_cues = []
    vpos = -250
    h=130
    g.cues.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'square_low.bmp')))
    g.text_cues.append(visual.TextStim(g.win, text="-$0.00", units='pix', pos=[0,vpos], color=[1,1,1], height=h))
    g.cues.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'square_med.bmp')))
    g.text_cues.append(visual.TextStim(g.win, text="-$1.00", units='pix', pos=[0,vpos], color=[1,1,1], height=h))
    g.cues.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'square_high.bmp')))
    g.text_cues.append(visual.TextStim(g.win, text="-$5.00", units='pix', pos=[0,vpos], color=[1,1,1], height=h))
    g.cues.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'circle_low.bmp')))
    g.text_cues.append(visual.TextStim(g.win, text="+$0.00", units='pix', pos=[0,vpos], color=[1,1,1], height=h))
    g.cues.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'circle_med.bmp')))
    g.text_cues.append(visual.TextStim(g.win, text="+$1.00", units='pix', pos=[0,vpos], color=[1,1,1], height=h))
    g.cues.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'circle_high.bmp')))
    g.text_cues.append(visual.TextStim(g.win, text="+$5.00", units='pix', pos=[0,vpos], color=[1,1,1], height=h))

    g.target = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'triangle.bmp'))
    
    g.result_msg = visual.TextStim(g.win, text="", units='pix', pos=[0,0], color=[1,1,1], height=h)
    
    
    g.x = visual.TextStim(g.win, text="X", units='pix', height=50, color=[1,1,1], pos=[0,0], bold=True)
    g.o = visual.TextStim(g.win, text="O", units='pix', height=50, color=[1,1,1], pos=[0,0], bold=True)

    StimToolLib.task_start(StimToolLib.MONETARY_INCENTIVE_DELAY_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    #if g.run_params['practice']:
    #    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'MID_instruct_scheduleP.csv'), g)
    #else:
    #    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'MID_instruct_scheduleS.csv'), g)
    #StimToolLib.show_title(g.win, g.title)
    #StimToolLib.show_instructions(g.win, g.instructions)
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.ideal_trial_start = instruct_end_time #ideal current time: incremented each trial by adding 8 + ITI
    #g.clock.reset()#start time at 0
    
    #lead in time
    g.o.draw()
    g.win.flip()
    #try:
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 12)
    g.win.flip()
    g.ideal_trial_start = g.ideal_trial_start + 12
    g.trial = 0
    for t,d,i in zip(trial_types, delays, itis):
        #main loop, will run through all trials
        g.trial_type = t
        do_one_trial(t, d, i)
        g.ideal_trial_start = g.ideal_trial_start + 8 + i #each trial is 8s long, plus the variable ITI
        g.trial = g.trial + 1
    #lead out time
    g.o.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + 8)

    g.win.flip()
    
    if g.run_params['practice']:
        #if this is a practice run, store 2/3 correct calibration for use in the scanner--also store all 0's for wins/losses to be ready for the first real run
        #mean_rt = sum(g.all_rts) / len(g.all_rts)
        g.all_rts.sort()
        g.total_trials = sum(g.wins) + sum(g.losses)
        if len(g.all_rts) < 0.5 * g.total_trials: #if they responded to less than half of the practice trials, repeat the practice
            StimToolLib.error_popup('Responses made to less than 1/2 of practice trials.  REPEAT THE PRACTICE')
        idx = int(0.66 * len(g.all_rts))
        calibration_time = g.all_rts[idx]
        g.calibrations = [calibration_time, calibration_time, calibration_time, calibration_time, calibration_time, calibration_time]
        g.total_wins = sum(g.wins)
        g.wins = [0, 0, 0, 0, 0, 0]
        g.losses = [0, 0, 0, 0, 0, 0]
        g.total_reward = 0
        StimToolLib.write_var_to_file(subj_param_file, 'initial_RT_for_scan', calibration_time)
        #StimToolLib.write_var_to_file(parameter_file, 'calibration', int(g.all_rts[idx] * 1000))
        #calibration_output = open(os.path.dirname(__file__) + '/data/' + g.session_params['SID'] + '_MID.calibration', 'w')
        #calibration_output.write(str(int(g.all_rts[idx] * 1000)))
        #calibration_output.close()
    store_calibrations_history(subj_param_file)
    
