
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui, sound, prefs

#Hariri faces task

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
        self.previous_adj = None
        self.previous_adj_time = 0
        self.previous_adj_type = None

event_types = {'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'TRIAL_ONSET':3, 
    'ADJECTIVE_SELECTION':4,
    'RATING_RESPONSE':5,
    'TASK_END':StimToolLib.TASK_END}


    
            
def do_one_trial(trial_type, video, video_file, selection_time, adjective):
    
    #duration should always be 12s, but is it?
    print('duration=%.2fs' % video.duration)

    video.draw()
    g.image_to_show.draw()
    g.win.flip()

    start_time = g.clock.getTime()
    #TODO fill in appropriate stuff
    StimToolLib.mark_event(g.output, g.trial, trial_type, event_types['TRIAL_ONSET'], start_time, video.duration, 'NA', video_file, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    click_time = start_time + selection_time
    clicked = False
    
    
    while video.status != visual.FINISHED:
        video.draw()
        g.image_to_show.draw()
        g.win.flip()
        now = g.clock.getTime()
        if now > click_time and not clicked:
            #this is when the adjective selection is shown
            StimToolLib.mark_event(g.output, g.trial, trial_type, event_types['ADJECTIVE_SELECTION'], now, 'NA', 'NA', adjective, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            clicked = True
            #reset response image to non-responded to cue the participant to respond
            g.image_to_show = g.question_image
            g.previous_adj = adjective
            g.previous_adj_time = now
            g.previous_adj_type = trial_type
        #the g.run_params['select_X'] is needed to handle left/right button boxes with 4 buttons
        resp = event.getKeys([g.session_params[g.run_params['select_1']], g.session_params[g.run_params['select_2']], g.session_params[g.run_params['select_3']], g.session_params[g.run_params['select_4']]])
        if resp: #subject pressed a key
            response = resp[0]
            if response == g.session_params[g.run_params['select_1']]:
                g.image_to_show = g.response_image_1
                r = 1
            if response == g.session_params[g.run_params['select_2']]:
                g.image_to_show = g.response_image_2
                r = 2
            if response == g.session_params[g.run_params['select_3']]:
                g.image_to_show = g.response_image_3
                r = 3
            if response == g.session_params[g.run_params['select_4']]:
                g.image_to_show = g.response_image_4
                r = 4
            now = g.clock.getTime()
            #a bit confusing, but we may be (probably are) on the next trial when a participant responds to the previous trial's image
            StimToolLib.mark_event(g.output, g.trial, g.previous_adj_type, event_types['RATING_RESPONSE'], now, now - g.previous_adj_time, r, g.previous_adj, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        StimToolLib.check_for_esc()
    return
    
    
        
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/NSM.Default.params', {})
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
    
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    print(g.run_params)
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="NSM")
        myDlg.addField('Run Number', choices=schedules, initial=str(g.run_params['run']))
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1#the user hit cancel so exit 

        g.run_params['run'] = thisInfo[0]

    StimToolLib.general_setup(g)
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_FC_Schedule' + str(g.run_params['run']) + '.csv')
    trial_types,junk,selection_times,video_info = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    #pull out the relevent list parts (due to the flexibility to have multiple values in most of the input columns)
    if len(selection_times) > 0:
        selection_times = selection_times[0]
    if len(video_info) > 0:
        adjectives = video_info[0]
        video_files = video_info[1]
    else:
        #allow for there to be no videos--for interview session
        adjectives = []
        video_files = []
    videos = []
    for f in video_files:
        #video original resolution is 1280x720
        #to display on 1024x768 projector, downsample to 1024x576
        #that leaves 1024x192 for selection area at screen bottom
        videos.append(visual.MovieStim3(g.win, os.path.join('Neurosociometer', f), size=(1024, 576),
                       flipVert=False, flipHoriz=False, loop=False, units='pix', pos=[0, 76]))
                       #flipVert=False, flipHoriz=False, loop=False, units='pix', pos=[0, 96]))
    
    print('LOADED')
    
    start_time = data.getDateStr()
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    fileName = os.path.join(g.prefix + '.csv')
    g.output = open(fileName, 'w')
    
    
    #initialize question/response images
    print(g.run_params)
    g.question_image = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), g.run_params['question_image']), units = 'pix', pos = [0, -288])
    g.response_image_1 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), g.run_params['response_image_1']), units = 'pix', pos = [0, -288])
    g.response_image_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), g.run_params['response_image_2']), units = 'pix', pos = [0, -288])
    g.response_image_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), g.run_params['response_image_3']), units = 'pix', pos = [0, -288])
    g.response_image_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), g.run_params['response_image_4']), units = 'pix', pos = [0, -288])
    
    #used to keep track of the last button press, and so when to clear out the selection image
    g.last_response_time = 0
    #start out showing the non-response image
    g.image_to_show = g.question_image
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + ',Trial Types are coded as follows: (0->neutral; 1->positive; -1->negative)\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    
    
    
    StimToolLib.task_start(StimToolLib.NEUROSOCIOMETER_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #StimToolLib.show_title(g.win, g.title)
    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)


    g.trial = 0
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    

    for i in range(len(videos)):
        g.trial = i
        do_one_trial(trial_types[i], videos[i], video_files[i], selection_times[i], adjectives[i])
        
        
    
    
  
 


