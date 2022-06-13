import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui, sound


#Cold Pressor Task with continuous rating 

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.clock = None #global clock used for timing
        self.output = None #The output file
        self.msg = None
        self.trial = None #trial number
        self.trial_type = None #current trial type
        self.marker_range = 998
        self.marker_start_y = -499
        self.marker_start_x = -69
        self.wheel_sensitivity = 20 #number of pixels to go up/down with each click of the mouse wheel
        self.pain_anchors = ['no pain', 'mild', 'moderate', 'severe', 'worst pain imaginable']
        self.effort_anchors = ['not at all', 'a little', 'moderately', 'a lot', 'extremely']
        self.effort_question_text = 'How hard did you TRY to keep your hand in the water for as long as you could tolerate?'
        self.anchors = None

event_types = {'INSTRUCT_START':1,
    'TASK_START':2,
    'TRIAL_START':3, 
    'MARKER_LOCATION':4, #will be seen many times, tracks trajectory of rating
    'TRIAL_COMPLETE':5,
    'VAS_RATING':6,
    'TASK_END':StimToolLib.TASK_END 
    }

def set_anchor_text(anchor_list): #should be a list of 5 anchors to draw at the appropriate places
    for a, i in zip(anchor_list, range(5)):
        g.anchors[i].setText(a)
def draw_anchors():
    for a in g.anchors:
        a.draw()
def initialize_anchors():
    g.anchors = []
    for i in range(5):
        g.anchors.append(visual.TextStim(g.win,text="",units='pix',pos=[0,g.marker_start_y + 5 + i*250],color=[1,1,1] ,height=30,wrapWidth=int(1600), alignHoriz='left'))

    
def get_vas_ratings():
    #get all ratings for a trial
    
    #get an effort rating that is on a vas that has the same length and number of anchors as the pain scale used in the cold pressor task
    start_time = g.clock.getTime()
    rating = StimToolLib.get_effort_rating(g, g.effort_question_text)
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['VAS_RATING'], now, now - start_time, rating, g.effort_question_text, True, g.session_params['parallel_port_address'])
    
    #get all other ratings
    for txt in g.vas_questions:
        rating_start_time = g.clock.getTime()
        this_rating = StimToolLib.get_one_vas_rating(g, txt.rstrip('\n'))
        now = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['VAS_RATING'], now, now - rating_start_time, str(this_rating), txt.rstrip(), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        
    
def do_one_trial(trial_length, trial_type): #trial types are 0: practice, 1: cold pressor, 2: effort rating
    g.scale_marker.pos=[g.marker_start_x,g.marker_start_y]
    
    if trial_type == 0:
        g.msg2.setText("Press ENTER when done")
    else:
        g.msg2.setText("If you remove your hand before the time limit, just wait")
    if trial_type == 0:
        g.msg2.draw()
    elif trial_type == 1:
        g.countdown.play()
        StimToolLib.just_wait(g.clock, g.clock.getTime() + g.countdown.getDuration())
    else:
        StimToolLib.error_popup("UNKNOWN TRIAL TYPE")
        #g.effort_question.draw()
    g.rating_scale.draw()
    g.scale_marker.draw()
    g.win.flip()
    start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_START'], start_time, 'NA', 'NA', 'NA', True, g.session_params['parallel_port_address'])
    position = 0
    while True: 
        if g.clock.getTime() - start_time > trial_length:
            break
        if event.getKeys(keyList = [g.session_params['up']]):
            position = min(position + 1/12, 1)
            g.scale_marker.pos = [g.scale_marker.pos[0], g.marker_range * position + g.marker_start_y]
            now = g.clock.getTime()
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['MARKER_LOCATION'], now, now - start_time, position, 'NA', False, g.session_params['parallel_port_address'])
        if event.getKeys(keyList = [g.session_params['down']]):
            position = max(position - 1/12, 0)
            g.scale_marker.pos = [g.scale_marker.pos[0], g.marker_range * position + g.marker_start_y]
            now = g.clock.getTime()
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['MARKER_LOCATION'], now, now - start_time, position, 'NA', False, g.session_params['parallel_port_address'])
        #vMeter_input = g.session_params['vMeter'].read_multiple_events()
        #if vMeter_input:
        #    position = vMeter_input[0][0][2] / float(127) #will return an int in the range [0,127]->scale to [0,1]
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        if event.getKeys(['return']) and trial_type != 1:
            break
        g.rating_scale.draw()
        g.scale_marker.draw()
        draw_anchors()
        if trial_type == 0:
            g.msg2.draw()
        elif trial_type == 1:
            g.msg2.draw()
        #else:
        #    g.effort_question.draw()
        g.win.flip()
    g.win.flip()
    if trial_type == 1:
        g.stop_sound.play()
    now = g.clock.getTime()
    #record trial info
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_COMPLETE'], now, now - start_time, 'NA', 'NA', True, g.session_params['parallel_port_address'])
    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/CP.Default.params', {})
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
        myDlg = gui.Dlg(title="Cold Pressor")
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
    schedule_file = os.path.join(os.path.dirname(__file__), str(g.run_params['run']))
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    trial_types,junk,durations,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)

    vas_question_file = open(os.path.join(os.path.dirname(__file__),  'VAS_questions.txt'), 'r')
    g.vas_questions = vas_question_file.readlines()
    
    g.countdown = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media', 'countdown.aiff'), volume=g.session_params['instruction_volume'])
    g.rating_scale = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/rating_scale.bmp'), pos=[0,0], units='pix', interpolate=True)
    g.scale_marker = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/scale_marker.bmp'), pos=[g.marker_start_x,g.marker_start_y], units='pix', mask=os.path.join(os.path.dirname(__file__),  'media/scale_marker_mask.bmp'))
    g.msg2 = visual.TextStim(g.win,text="Press ENTER when done",units='pix',pos=[0,-550],color=[1,1,1] ,height=20,wrapWidth=int(1600))
    g.effort_question = visual.TextStim(g.win,text=g.effort_question_text,units='pix',pos=[-800,0],color=[1,1,1] ,height=50,wrapWidth=int(700), alignHoriz='left')
    initialize_anchors()
    g.stop_sound = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media', 'stop.aiff'), volume=g.session_params['instruction_volume'])
    g.mouse = event.Mouse()
    start_time = data.getDateStr()
    #g.prefix = 'CP-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_1' +  '-' + start_time 
    
    
    g.prefix = StimToolLib.generate_prefix(g)
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_MID_Schedule' + str(g.run_params['run']) + '.csv')
    fileName = os.path.join(g.prefix + '.csv')
    g.output = open(fileName, 'w')
    
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])

    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Event Codes:,' + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    
    g.trial = 0
    
    StimToolLib.task_start(StimToolLib.COLD_PRESSOR_CODE, g)
    
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_START'], instruct_start_time, 'NA', 'NA', 'NA', True, g.session_params['parallel_port_address'])
    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'CP_instruct_schedule1.csv'), g)
    set_anchor_text(g.pain_anchors)
    do_one_trial(1000, 0)
    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'CP_instruct_schedule2.csv'), g)
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_START'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', True, g.session_params['parallel_port_address'])
    g.trial = 1
    do_one_trial(120, 1)
        
    get_vas_ratings()
    
    
    
