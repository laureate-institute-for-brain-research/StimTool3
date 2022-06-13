
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
        self.rate_mark_move_distance = 96 #distance to move the selection marker left/right (in pixels)
        self.rate_mark_start = [0,-105]
        self.rating_marker = None
        self.rating_marker_selected = None


event_types = {'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'IMAGE_ONSET':3, #this will be for fixation, neutral, or drug, or stress cues
    'BOX_ONSET':4,
    'BOX_RESPONSE':5,
    'RATING_ONSET':6,
    'RATING_CHANGE':7,
    'RATING_LOCK':8,
    'FINAL_RATING':9,
    'RELAXATION_ONSET':10,
    'TASK_END':StimToolLib.TASK_END 
    }



def do_one_image_trial(trial_type, image, duration):
    #run a single image trial, which can also be a fixation
    #draw image to show
    image.draw() 
    draw_box = False #will be True for border trials, and then set to False once they hit a button
    if trial_type[0] == '8':
        #box trial--draw the box and detect a response
        draw_box = True
        g.box.draw()

    g.win.flip()
    image_start = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['IMAGE_ONSET'], image_start, 'NA', 'NA', image._imName, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    if draw_box: #record the time when the border was shown
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BOX_ONSET'], image_start, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    event.clearEvents() #clear old keypresses
    while g.clock.getTime() < g.ideal_trial_start + duration:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        resp = event.getKeys([g.session_params['left'], g.session_params['right'], g.session_params['select']])
        if resp: #subject pressed a key
            now = g.clock.getTime()
            if draw_box:
                response_result = 1
            else:
                response_result = 2
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BOX_RESPONSE'], now, now - image_start, resp[0], response_result, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            draw_box = False
        image.draw() #have to draw the image first--otherwise it will cover the box!
        if draw_box:
            g.box.draw()
        g.win.flip()
        StimToolLib.short_wait()
    if draw_box: #mark that the subject missed the response, so it's easy to find later (instead of having to look for a BOX_ONSET
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BOX_RESPONSE'], g.clock.getTime(), 'NA', 'NA', 0, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])    

            
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration)
    g.win.flip()
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration + 0.2) #200ms blank screen
    #update trial start time
    g.ideal_trial_start = g.ideal_trial_start + duration + 0.2
    if draw_box and g.run_params['practice']:
        #for practice trials where the subject didn't respond to the box, show a reminder about responding to the yellow frame and then repeat the trial until they respond
        g.frame_reminder.draw()
        g.win.flip()
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + 3)
        g.ideal_trial_start = g.ideal_trial_start + 3
        do_one_image_trial(trial_type, image, duration)

def do_one_rating_trial(trial_type, image, duration):
    current_rating = 5
    g.rating_marker.setPos(g.rate_mark_start)
    rating_type = trial_type[0]
    if rating_type == '1':
        rating_image = g.valence_response
    if rating_type == '2':
        rating_image = g.arousal_response
    if rating_type == '3':
        rating_image = g.stress_response
    if rating_type == '4':
        rating_image = g.urge_response
    
    rating_image.draw()
    g.rating_marker.draw()
    g.win.flip()
    rating_start = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_ONSET'], rating_start, 'NA', 'NA', rating_image._imName, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #down_up = [g.session_params['down'], g.session_params['up'], g.session_params['select']]
    left_right = [g.session_params['left'], g.session_params['right'], g.session_params['select']]
    responded = False #used to keep track of whether or not the subject locked in a response
    event.clearEvents() #clear old keypresses
    
    image_to_draw = g.rating_marker
    rating_lock_rt = 'NA'
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
                #in case subject un-locked response, set rating_lock_rt back to NA
                rating_lock_rt = 'NA'
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], now, now - rating_start,-1, current_rating, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            if resp[0] == left_right[1] and current_rating < 9: #pushed right and not at end
                arrow_to_draw = g.rating_marker #will draw hollow arrow
                current_rating = current_rating + 1
                g.rating_marker.setPos([g.rating_marker.pos[0] + g.rate_mark_move_distance, g.rating_marker.pos[1]])
                #in case subject un-locked response, set rating_lock_rt back to NA
                rating_lock_rt = 'NA'
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], now, now - rating_start,1, current_rating, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            if resp[0] == left_right[2]: #pushed select
                arrow_to_draw = g.rating_marker_selected #will draw filled in arrow
                g.rating_marker_selected.setPos(g.rating_marker.pos)
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_LOCK'], now, now - rating_start, current_rating, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                rating_lock_rt = now - rating_start
                #g.win.flip()
                #break
            rating_image.draw()
            arrow_to_draw.draw()
            #g.rating_marker.draw()
            g.win.flip()
        StimToolLib.short_wait()
    #mark where the selector was at the end
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_RATING'], g.clock.getTime(), rating_lock_rt, current_rating, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration)
    g.ideal_trial_start = g.ideal_trial_start + duration

def do_one_relaxation_trial(trial_type, image, duration):
    #play the relaxation audio, then rest for the remainder of duration
    #image will be a fixation cross
    image.draw() 
    g.win.flip()
    image_start = g.clock.getTime()
    g.audio_relaxation.play()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RELAXATION_ONSET'], image_start, 'NA', 'NA', os.path.join(os.getcwd(), 'media', 'DSRRelaxationScript.aiff'), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration)
    g.ideal_trial_start = g.ideal_trial_start + duration




def do_one_trial(trial_type, image, duration):
    if trial_type == '999':
        do_one_relaxation_trial(trial_type, image, duration)
        return
    if trial_type[0] == '0' or trial_type[0] == '8':
        #0 for no box, 9 for box
        do_one_image_trial(trial_type, image, duration)
    else:
        do_one_rating_trial(trial_type, image, duration)
    
    
    
    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/DSR.Default.params', {})
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
        myDlg = gui.Dlg(title="DSR")
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

    #select schedule file based on subject ID and visit
    
    #lists of schedules for each image category, for PASO these each have 4 items, one for each visit
    #g.run_params['neutral_schedules']
    #g.run_params['stress_schedules']
    #g.run_params['opioid_schedules']
    #subject ID--we will get the last 3 characters to use for run selection
    #g.session_params['SID'] 
    #session_id, e.g. T0/T1/T2/T3, which we will use to select which image set is selected (in random order, based on subject ID) 
    #g.session_params['session_id']
    #run number, used along with subject ID to select condition (neutral/stress/opioid)
    #g.run_params['run_number']

    
        

    while True:
        #check to be sure id_number is a number, open a popup if it is not
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

    
    print('id_number is: ' + str(id_number))

    
            
    set_order_dict = {
        0  : '1234',
        1  : '1243',
        2  : '1324',
        3  : '1342',
        4  : '1423',
        5  : '1432',
        6  : '2134',
        7  : '2143',
        8  : '2314',
        9  : '2341',
        10 : '2413',
        11 : '2431',
        12 : '3124',
        13 : '3142',
        14 : '3214',
        15 : '3241',
        16 : '3412',
        17 : '3421',
        18 : '4123',
        19 : '4132',
        20 : '4213',
        21 : '4231',
        22 : '4312',
        23 : '4321'}
    order_idx = id_number % 24
    print('order_idx is: ' + str(order_idx))
    #subject ID mod 24 -> image set order
    this_set_order = set_order_dict[order_idx]
    print('this_set_order is: ' + this_set_order)
    session_idx_dict = {
        'V1':0,
        'V2':1,
        'V3':2,
        'V4':3
    }
    if g.run_params['practice']:
        #for practice, always use the same schedule
        this_set = 'P'
    else:
        this_set = this_set_order[session_idx_dict[g.session_params['session_id']]]
    print('session ID is: ' + g.session_params['session_id'])
    print('set selected based on session ID and set order is: ' + this_set)
    #this_set is now a character, '1', '2', '3', or '4'
    #subject ID mod 6 -> run order
    condition_order_dict = {0 : ['neutral', 'opioid', 'stress'],
        1  : ['neutral', 'stress', 'opioid'],
        2  : ['opioid', 'neutral', 'stress'],
        3  : ['opioid', 'stress', 'neutral'],
        4  : ['stress', 'neutral', 'opioid'],
        5  : ['stress', 'opioid', 'neutral']}
    condition_order_idx = id_number % 6
    print('condition_order_idx is:' + str(condition_order_idx))
    this_condition_order = condition_order_dict[condition_order_idx]
    print('conditoin order, based on condition_order_idx and condition_order_dict is: ' + str(this_condition_order))
    #this_condition_order is now an order of conditions, will select from them based on run_number (- 1, since run is 1..3 and need to grab item 0..2 )
    if g.run_params['practice']:
        #for practice, always use the same schedule
        this_condition = 'neutral'
    else:
        this_condition = this_condition_order[g.run_params['run_number'] - 1]
    print('this_condition is: ' + this_condition)
    #schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    selected_schedule = 'study-PASO_task-DSR_condition-' + this_condition + '_set-' + this_set + '.schedule'
    print('selected_schedule is: ' + selected_schedule)
    schedule_file = os.path.join(os.path.dirname(__file__), selected_schedule)

    #write order
    run_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '-' + g.session_params['session_id'] + '-_DSR-R' + str(g.run_params['run_number']) + '-PARA.txt')
    StimToolLib.write_var_to_file(run_param_file, 'id', g.session_params['SID'])
    StimToolLib.write_var_to_file(run_param_file, 'id_mod_24', order_idx)
    StimToolLib.write_var_to_file(run_param_file, 'set_order', this_set_order)
    StimToolLib.write_var_to_file(run_param_file, 'id_mod_6', condition_order_idx)
    StimToolLib.write_var_to_file(run_param_file, 'condition_order', this_condition_order)
    StimToolLib.write_var_to_file(run_param_file, 'visit', g.session_params['session_id'])
    StimToolLib.write_var_to_file(run_param_file, 'run', g.run_params['run_number'])
    StimToolLib.write_var_to_file(run_param_file, 'schedule_file', selected_schedule)




    StimToolLib.general_setup(g)
    trial_types,images,durations,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    durations = durations[0] #durations of the images/itis
    images = images[0]
    for i in images:
        #i.size = (g.session_params['screen_x'], g.session_params['screen_y']) #set stimulus images to be fullscreen
        i.size = (g.run_params['image_x'], g.run_params['image_y']) #set stimulus image size--probably always 1024x768

    

    #yellow frame for box trials
    g.box = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media','YellowFrame.gif'), units='pix', mask=os.path.join(os.path.dirname(__file__),  'media/frame_mask.gif'))
    g.box.size = (g.session_params['screen_x'], g.session_params['screen_y']) #set stimulus images to be fullscreen

    #initialize question/response images
    g.rating_marker = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/rating_mark_up.png'), pos=[285,-450], units='pix')
    g.rating_marker_selected = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/rating_mark_up_selected.png'), pos=[285,-450], units='pix')

    
    
    g.valence_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/valence.png'), pos=[0,0], units='pix')
    g.arousal_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/arousal.png'), pos=[0,0], units='pix')
    g.stress_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/stress.png'), pos=[0,0], units='pix')
    g.urge_response = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/urge.png'), pos=[0,0], units='pix')
    g.frame_reminder = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media', 'frame_reminder.PNG'))

    g.audio_relaxation = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/DSRRelaxationScript.aiff'))

    start_time = data.getDateStr()
    fileName = os.path.join(g.prefix + '.csv')
    
    
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.CUE_REACTIVITY_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)

    g.trial = 0
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.ideal_trial_start = instruct_end_time
    g.win.flip()
    
    
    for t, i, d in zip(trial_types, images, durations):
        g.trial_type = t
        do_one_trial(t, i, d)
        g.trial = g.trial + 1
    
  
 


