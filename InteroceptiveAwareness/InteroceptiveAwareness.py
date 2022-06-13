
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui, sound

#Emotional Reactivity module: present a series of images, sometimes accompanied by startles

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
        self.trial_type = None #trial type
        self.rate_mark_move_distance = 148 #distance to move the selection marker up/down (in pixels)
        #self.rate_mark_start = [285,-6]
        self.rate_mark_start = [0,-117]
        self.rate_length = 5
        self.rating_marker = None
        self.rating_marker_selected = None


event_types = {'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'IMAGE_ONSET':3, #this will be for fixation, heart, stomach, and target
    'TARGET_COLOR_CHANGE':4, #also codes color changed to (1-7)
    'RATING_ONSET':5, #also codes during 
    'RATING_CHANGE':6, #also codes up or down
    'FINAL_RATING':7,#also codes selection
    'TASK_END':StimToolLib.TASK_END 
    }

def get_rating(trial_type, duration):
    current_rating = 4
    g.rating_marker.setPos(g.rate_mark_start)
    if trial_type == 4:
        rating_image = g.heart_response
    if trial_type == 5:
        rating_image = g.stomach_response
    if trial_type == 6:
        rating_image = g.target_response
    if trial_type == -11:
        rating_image = g.heartbeat_response
    if trial_type == -12:
        rating_image = g.breath_response
    if trial_type == -13:
        rating_image = g.head_response
    if trial_type == -14:
        rating_image = g.lungs_response
        
    rating_image.draw()
    g.rating_marker.draw()
    g.win.flip()
    rating_start = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_ONSET'], rating_start, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #down_up = [g.session_params['down'], g.session_params['up'], g.session_params['select']]
    left_right = [g.session_params['left'], g.session_params['right'], g.session_params['select']]
    responded = False #used to keep track of whether or not the subject locked in a response
    event.clearEvents() #clear old keypresses
    
    image_to_draw = g.rating_marker
    while g.clock.getTime() < g.ideal_trial_start + duration:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys(left_right)
        if resp: #subject pressed a key
            now = g.clock.getTime()
            if resp[0] == left_right[0] and current_rating > 1: #pushed left and is not at end
                arrow_to_draw = g.rating_marker #will draw hollow arrow
                current_rating = current_rating - 1
                g.rating_marker.setPos([g.rating_marker.pos[0] - g.rate_mark_move_distance, g.rating_marker.pos[1]])
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], now, now - rating_start,-1, current_rating, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            if resp[0] == left_right[1] and current_rating < 7: #pushed right and not at end
                arrow_to_draw = g.rating_marker #will draw hollow arrow
                current_rating = current_rating + 1
                g.rating_marker.setPos([g.rating_marker.pos[0] + g.rate_mark_move_distance, g.rating_marker.pos[1]])
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], now, now - rating_start,1, current_rating, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            if resp[0] == left_right[2]: #pushed select
                arrow_to_draw = g.rating_marker_selected #will draw filled in arrow
                g.rating_marker_selected.setPos(g.rating_marker.pos)
                #rating_image.draw()
                #g.rating_marker_selected.draw()
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_RATING'], now, now - rating_start, current_rating, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                #g.win.flip()
                #break
            rating_image.draw()
            arrow_to_draw.draw()
            #g.rating_marker.draw()
            g.win.flip()
        StimToolLib.short_wait()
    if not responded: #mark where the selector was at the end
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_RATING'], g.clock.getTime(), 'NA', current_rating, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration)
    
def do_one_trial(trial_type, duration):
    if trial_type < 3 and trial_type > -10: #just show image and wait
        if trial_type == 0:
            g.fix.draw()
        if trial_type == 1:
            g.heart.draw()
        if trial_type == 2:
            g.stomach.draw()
            
        if trial_type == -1: #-11 will be rating
            g.heartbeat.draw()
        if trial_type == -2: #-12 will be rating
            g.breath.draw()
        if trial_type == -3: #-13 will be rating
            g.head.draw()
        if trial_type == -4: #-14 will be rating
            g.lungs.draw()
            
        g.win.flip()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['IMAGE_ONSET'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration)
    if (trial_type > 3 and trial_type < 7) or trial_type < -10: #rating trials
        get_rating(trial_type, duration)
        
    if trial_type > 10: #show a flashing target image
        idx = trial_type - 10 #intensity levels will be 1-7, trial_type will be 11-17
        for i in range(10):
            if i % 2 == 0: #alternate drawing dark and lighter targets
                g.targets[0].draw()
                color = 0
            else:
                g.targets[idx].draw()
                color = idx
            g.win.flip()
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TARGET_COLOR_CHANGE'], g.clock.getTime(), 'NA', 'NA', color, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            StimToolLib.just_wait(g.clock, g.ideal_trial_start + i + 1)
    #update trial start time
    g.ideal_trial_start = g.ideal_trial_start + duration
    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/IA.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status

def generate_order_pick_run():
    temp_dictionary = {}
    subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['param_file'])
    temp_dictionary = StimToolLib.get_var_dict_from_file(subj_param_file, temp_dictionary)
    if temp_dictionary == {}: #first random run--create subject specific random order
        possible_schedules = g.run_params['possible_schedules']
        #possible_schedules = ['T1000_IA_T0_R1.schedule', 'T1000_IA_T0_R2.schedule', 'T1000_IA_T0_R3.schedule'] #this is *NOT* the best way to do this...should be specified in a parameter file in stead of hard coded
        random.shuffle(possible_schedules)
        StimToolLib.write_var_to_file(subj_param_file, 'schedule_1', possible_schedules[0])
        StimToolLib.write_var_to_file(subj_param_file, 'schedule_2', possible_schedules[1])
        temp_dictionary = StimToolLib.get_var_dict_from_file(subj_param_file, temp_dictionary)
    g.run_params['run'] = temp_dictionary['schedule_' + str(g.run_params['random_run_number'])]
    param_file = g.run_params['run'][0:-9] + '.params'
    #StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    
def run_try():  
#def run_try(SID, raID, scan, resk, run_num='Practice'):
    
    #if not os.path.isfile(os.path.dirname(__file__) + '/data/' + g.session_params['SID'] + '_IA.order'): #this file will contain two space separated integers 1..3, indicating run 1 and run 2 for this subject, randomly selected from 6 possible orders
    #    order_out = open(os.path.dirname(__file__) + '/data/' + g.session_params['SID'] + '_IA.order', 'w')
    #    order = range(1,4)
    #    random.shuffle(order)
    #    order_out.write(str(order[0]) + ' ' + str(order[1]))
    #    order_out.close()
    #if g.run_params['run'] != 'P': #run_num will be 1 or 2
    #    order_in = open(os.path.dirname(__file__) + '/data/' + g.session_params['SID'] + '_IA.order', 'r')
    #    order = order_in.next().split()
    #    g.run_params['run'] = order[int(g.run_params['run']) - 1]
    #g.resk = resk
        
    
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="IA")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
     #will contain run order for subject when a random order is selected

    if g.run_params['random_run']:
        generate_order_pick_run()
        g.prefix = StimToolLib.generate_prefix(g)
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    StimToolLib.general_setup(g)
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_IA_Schedule' + g.run_params['run'] + '.csv')
    trial_types,images,durations,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    durations = durations[0] #durations of the itis
    for i in range(len(trial_types)): #convert to int for easier decoding
        trial_types[i] = int(trial_types[i])
    
    
    #set up stimuli
    g.targets = []
    for i in range(8):
        g.targets.append(visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/Target' + str(i) + '.png'), pos=[0,0], units='pix'))
    g.fix = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/fixation.png'), pos=[0,0], units='pix')
    g.heart = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/heart.png'), pos=[0,0], units='pix')
    g.stomach = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/stomach.png'), pos=[0,0], units='pix')
    g.lungs = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/lungs.png'), pos=[0,0], units='pix')
    
    
    g.heartbeat = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/heartbeat.png'), pos=[0,0], units='pix')
    g.breath = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/breath.png'), pos=[0,0], units='pix')
    g.head = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/head.png'), pos=[0,0], units='pix')
    
    g.heart_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/h_resp_3.bmp'), pos=[0,0], units='pix')
    g.stomach_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/s_resp_3.bmp'), pos=[0,0], units='pix')
    g.lungs_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/lungs_resp.png'), pos=[0,0], units='pix')
    g.target_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/td_resp_3.bmp'), pos=[0,0], units='pix')
    
    g.heartbeat_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/hb_resp_3.png'), pos=[0,0], units='pix')
    g.breath_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/breath_resp_3.png'), pos=[0,0], units='pix')
    g.head_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/head_resp_3.bmp'), pos=[0,0], units='pix')


    g.rating_marker = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/rating_mark_down.png'), pos=[285,-450], units='pix')
    g.rating_marker_selected = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/rating_mark_down_selected.png'), pos=[285,-450], units='pix')
    
    
    
    start_time = data.getDateStr()
    fileName = os.path.join(g.prefix + '.csv')
    
    
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.INTEROCEPTIVE_AWARENESS_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)

    

    g.trial = 0
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.ideal_trial_start = instruct_end_time

    
    for t, d in zip(trial_types, durations):
        g.trial_type = t
        do_one_trial(t, d)
        g.trial = g.trial + 1
    g.msg.setColor([-1,-1,-1])

  
 


