
import StimToolLib, os, random, operator
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
        self.current_rts = []
        self.average_rt = 0.5 #initialize to something, otherwise it can crash when there are no responses during practice...
        self.average_sound_latency = 0 #correction for latency beteween calling sound.play() and the sound actually playing
        self.update_RT_during_scan = False #whether or not to update the average RT every block during the scanning run


event_types = {'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'CUE_ONSET':3, 
    'STOP_SIGNAL':4, 
    'RESPONSE':5, 
    'TRIAL_END':6,
    'INSTRUCT':7,
    'TRIGGERBOX_PRE':StimToolLib.TRIGGERBOX_PRE,
    'TRIGGERBOX_POST':StimToolLib.TRIGGERBOX_POST,
    'TASK_END':StimToolLib.TASK_END}

    
def do_one_trial(trial_type, duration):
    if trial_type < 0:
        trial_type = -trial_type #tone trials during second block of practice are coded as negative numbers
        sound_stop = False #this provides a mechanism to code responses to tone trials as being correct--since the instructions were to ignore the tone
    else:
        sound_stop = True
    delay_or_instruct = int(trial_type / 10) #tens digit: 9 codes instruct slide, 0 for go, 1..6 for tone at 0..500ms prior to average reaction time
    image = trial_type % 10 #ones digit: 0..2 codes instruct slides or 0->X, 1->O
    if delay_or_instruct == 9:
        g.instruct_images[image].draw()
        g.win.flip()
        if len(g.current_rts) > 0: #average RT for this block
            average_rt = sum(g.current_rts) / len(g.current_rts)
            g.current_rts = []
            if g.run_params['run'] == 'P' or g.update_RT_during_scan: #for the practice run, update the average RT used for tone offsets every block (also an option during scan)
                g.average_rt = average_rt
        else:
            average_rt = 'NA'
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['INSTRUCT'], g.clock.getTime(), average_rt, 'NA', image, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration - 0.2)
        g.win.flip()
    else:
        #show O/X
        print(image)
        g.stimuli[image].draw()
        g.win.flip()
        real_trial_start = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['CUE_ONSET'], real_trial_start, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        #calculate time for tone presentation
        if delay_or_instruct == 0:
            tone_time = -1
        else:
            tone_time = real_trial_start + g.average_rt - (float(delay_or_instruct) - 1) * 0.1 - g.average_sound_latency
        
        tone_played = False
        responded = False
        key = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']]) #clear pressed keys so that a very early press is not counted
        first_response_time = 'NA'
        first_response = 'NA'
        trial_result = -1
        while g.clock.getTime() < g.ideal_trial_start + duration - 0.2:
            StimToolLib.short_wait()
            #quit on escape
            if event.getKeys(["escape"]):
                raise StimToolLib.QuitException()
            #register response
            key = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']]) 
            if key:
                now = g.clock.getTime()
                if key[0] == g.session_params['select']: #record a press of the select button, but don't do anything else
                    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE'], now, now - real_trial_start, 2, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                    continue
                #record keypress and right/wrong
                if key[0] == g.session_params['left']:
                    response = 0
                    if image == 0:
                        correct = 1
                    else:
                        correct = 0
                else:
                    response = 1
                    if image == 1:
                        correct = 1
                    else:
                        correct = 0
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE'], now, now - real_trial_start, response, correct, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                if not responded: #first response, so record results for use in TRIAL_END
                    if delay_or_instruct == 0: #only use go trial RTs for average RT
                        g.current_rts.append(now - real_trial_start)
                    responded = True
                    first_response = response
                    first_response_time = now - real_trial_start
                    if correct and (tone_time == -1 or not sound_stop): #responded correctly (sound_stop codes for 'ignore tone' trials)
                        trial_result = 1
                    if correct and tone_time > 0 and sound_stop: #correct response, but should have stopped
                        trial_result = 2
                    if not correct and tone_time == -1: #incorrect response but no tone
                        trial_result = 3
                    if not correct and tone_time > 0 and sound_stop: #incorrect response and should have stopped
                        trial_result = 4
                    g.win.flip() #remove the stimulus from the window
                #record response here
            #possibly play sound
            if tone_time > 0 and g.clock.getTime() > tone_time and not tone_played:
                if not responded: #only draw red stimulus if the subject hasn't responded yet
                    g.stimuli_red[image].draw()
                    g.win.flip()
                    red_drawn = 1
                else:
                    red_drawn = 0
                g.tone.play()
                now = g.clock.getTime()
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['STOP_SIGNAL'], now, now - real_trial_start, 'NA', red_drawn, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                tone_played = True
        if trial_result == -1 and tone_time > 0: #successfully stopped on stop trial
            trial_result = 1
        if trial_result == -1 and tone_time == -1: #failed to go on go trial
            trial_result = 5
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_END'], g.clock.getTime(),first_response_time, first_response, trial_result, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        #wait 1300ms & play sound if stop signal trial
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration)
    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/SS.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status
        
def run_try():  
#def run_try(SID, raID, scan, resk, run_num='Practice'):

    #g.resk = resk
    #calibration = StimToolLib.get_var_from_file(os.path.dirname(__file__) + '/data/' + g.session_params['SID'] + 'SS.calibration', 'MRT')
    #if not calibration: #if it's not in the file...
    #    calibration = 'Average RT not read from file! OK for practice.'

    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="SST")
        myDlg.addField('Run Number', choices=schedules, initial=str(g.run_params['run']))
        #read average RT for this subject from file
        #myDlg.addField('Average RT from Practice',  calibration)
        myDlg.addField('Update RT during scanning run',  choices=['True', 'False'], initial='False')
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1#the user hit cancel so exit 
        #if thisInfo[0] == 'Practice':
        #    g.run_params['run'] = 'P'
        #else:
        g.run_params['run'] = thisInfo[0]
        #    g.average_rt = float(thisInfo[1])
        g.update_RT_during_scan = (thisInfo[1] == 'True') 
        
    
    StimToolLib.general_setup(g)
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_SS_Schedule' + str(g.run_params['run']) + '.csv')
    trial_types,junk,durations,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    durations = durations[0] #durations for images

    text_height = 80
    g.instruct_images = []
    g.instruct_images.append(visual.TextStim(g.win, text="And Here We Go!", units='pix', height=text_height, color=[1,1,1], pos=[0,0], bold=True, wrapWidth=int(1600)))
    g.instruct_images.append(visual.TextStim(g.win, text="Ignore the tone", units='pix', height=text_height, color=[1,1,1], pos=[0,0], bold=True, wrapWidth=int(1600)))
    g.instruct_images.append(visual.TextStim(g.win, text="Don't press when\nyou hear the tone", units='pix', height=text_height, color=[1,1,1], pos=[0,0], bold=True, wrapWidth=int(1600)))
    
    g.stimuli = []
    g.stimuli.append(visual.TextStim(g.win, text="X", units='pix', height=text_height, color=[1,1,1], pos=[0,0], bold=True))
    g.stimuli.append(visual.TextStim(g.win, text="O", units='pix', height=text_height, color=[1,1,1], pos=[0,0], bold=True))
    
    g.stimuli_red = []
    g.stimuli_red.append(visual.TextStim(g.win, text="X", units='pix', height=text_height, color='red', pos=[0,0], bold=True))
    g.stimuli_red.append(visual.TextStim(g.win, text="O", units='pix', height=text_height, color='red', pos=[0,0], bold=True))
    
    
    
    
    
    start_time = data.getDateStr()
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.tone = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/t1000Hz.wav'), volume=g.run_params['tone_volume'])
    g.prefix = StimToolLib.generate_prefix(g)
    fileName = os.path.join(g.prefix + '.csv')
    subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['param_file'])
    #network_subj_param_file = os.path.join(g.session_params['network_output_dir'], os.path.basename(subj_param_file))
    #subj_param_files = [subj_param_file, network_subj_param_file]
    if not g.run_params['practice']:
        g.average_rt = StimToolLib.get_var_from_file(subj_param_file, 'MRT')
        #g.average_rt = StimToolLib.get_var_from_files(subj_param_files, 'MRT')
        if not g.average_rt:
            StimToolLib.error_popup('Average RT not read from file: did you run practice first?')
    #g.prefix = 'SST-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time 
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    g.output = open(fileName, 'w')
    StimToolLib.task_start(StimToolLib.STOP_SIGNAL_CODE, g)
    #StimToolLib.show_title(g.win, g.title)
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  schedule_file + ',Event Codes:,' + str(sorted_events) + ',Trial Types are coded as follows: tens digit: 9 for instruct slide; 1..6 for tone at 0..500ms before MRT; ones digit: 0..2 for instruct slide shown or 0->X/left and 1->O/right, update_RT_during_scan=' + str(g.update_RT_during_scan) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    
    if g.session_params['signal_triggerbox']:
        StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TRIGGERBOX_PRE'], g.run_params['triggerbox_times'][0], 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TRIGGERBOX_POST'], g.run_params['triggerbox_times'][1], 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    
    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    #if g.run_params['run'] == 'P':
    #    StimToolLib.show_instructions(g.win, g.prac_instructions)
    #else:
    #    StimToolLib.show_instructions(g.win, g.scan_instructions)
    g.trial = 0
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    g.win.flip()

    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.ideal_trial_start = instruct_end_time

    for t_type, d in zip(trial_types, durations):
        g.trial_type = t_type
        #try:
        print(t_type)            
        do_one_trial(int(t_type), d) 
        #except StimToolLib.QuitException as e:
        #    g.output.close()
        #    g.win.close()
        #    return -1
        g.trial = g.trial + 1
        g.ideal_trial_start = g.ideal_trial_start + d
    if g.run_params['practice']: #store final average_rt for scanning run
        try:
            StimToolLib.write_var_to_file(subj_param_file, 'MRT', sum(g.current_rts) / len(g.current_rts))
            #StimToolLib.write_var_to_files(subj_param_files, 'MRT', sum(g.current_rts) / len(g.current_rts))
        except ZeroDivisionError:
            StimToolLib.error_popup('Division by Zero!  Did the participant forget to respond to all of the trials in the last practice block???')
            
            #calibration_output = open(os.path.dirname(__file__) + '/data/' + g.session_params['SID'] + '_SS.calibration', 'w')
        #calibration_output.write(str(sum(g.current_rts) / len(g.current_rts)))
        #calibration_output.close()

    
  
 


