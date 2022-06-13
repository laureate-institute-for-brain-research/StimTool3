
import StimToolLib, os, random, operator, math, copy, time
from psychopy import visual, core, event, data, gui, sound
from fractions import Fraction #to make definition of probability distributions more intuitive
from psychopy.hardware import joystick

#Change Point Detection task

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawns
        self.clock = None #global clock used for timing
        self.x = None #X fixation stimulus
        self.output = None #The output file
        self.msg = None
        self.timer_msg = None #message used for countdown timer
        self.ideal_trial_start = None #ideal time the current trial started
        self.this_trial_output = '' #will contain the text output to print for the current trial
        self.instructions = []
        #self.dot_locations = [(-2.12, 2.12), (-.78,-2.90), (2.90, .78)]#[(-212, 212), (-78,-290), (290, 78)]
        #self.dots = [] #dot patches
        #self.circles_white = [] #white circles that go over dot patches when they're not being displayed
        #self.circles_red = [] #red circles used to illuminate correct response (when incorrect response is given)
        #self.circles_green = [] #green circles used to show correct response
        self.bar_red = None
        self.bar_green = None #red and green point bars
        self.bar_x = -.7 #x location of time bar (should be just left of stop line)
        self.bar_width = .08 #width of the time bar
        self.trial = None #trial number
        self.trial_type = None #current trial type
        self.break_instructions = ['''You may now take a short break.''']
        self.block_points = 0 #points earned this block
        self.total_points = 0 #total points earned so far
        self.block_correct = 0 #number of correct responses in this block
        self.direction_text = None #will be right or left
        self.car = None #car stimulus
        self.motorcycle = None #motorcycle stimulus
        self.vehicle = None #current vehicle stimulus
        self.joy = None #joystick object
        self.vehicle_start_pos = [0, -8] #starting position for the car (in cm, both trial types)
        self.target = None #white circle used in move/go trials
        self.sound_beep1 = None #beeps for countdown timers
        self.sound_beep2 = None
        self.condition = 'sensitivity' # Use for differente trial types, other option is 'velocity'

        # Dictionary for mapping schedule block types to self.B
        self.sensitivity_map  = {
                '0': 7.5, # Low Sensitivity
                '1': 15.0, # Medium Sensitivty # the default
                '2': 22.5, #  High Sensitivity
            }
        self.A = -0.35 #equilibrium point--makes it so the subject has to continue holding the stick forward just a little to remain stopped at the line
        self.B = 15.0 #maximum speed in cm/s # gets set for diffenete sensitifity changes
        self.C = 2  # 0 is very ICY, 2, is not so ICY, start at 2
        self.dy = 0.0
        self.stick_move_threshold = 0.03 #threshold used to determine when the subject has responded on move-go trials, to flag false starts, and to start speed-and-stop trials
        self.move_go_speeds = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.1, 0.15, 0.2, 0.25, 0.3] #possible speeds for the move/go task
        self.stop_y = 8 #vertical location of stop sign (in cm)
        self.stop_sign = None #sign used for speed-stop trials
        self.time_bar_max_height = 1 #maximum height of time bar, should be half the screen height (in norm)
        self.time_text = [] #10s and 0s--text next to timer bar
        self.target_pos = 3.35 #position to change colors
        self.response_period_start = None #will keep track of when the current response period began--used to compute response time in output
        self.last_t = None
        self.fast_tolerence_onset = None
        self.reached_max_runtime = False
        
        # Feedback condition texts
        self.feedback_text_dict = {
            'slow': 'try harder',
            'fast': 'Good Job!'
        }
        self.feedback_text_string = self.feedback_text_dict['fast'] # Text display after trial 

event_types = {
    'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'BEEP':3, 
    'DELAY_ONSET':4, 
    'FALSE_START':5, 
    'MOTION_ONSET':6,
    'RESPONSE_PERIOD_ONSET':7,
    'CAR_POSITION_AND_VELOCITY':8,
    'STICK_X':9,
    'STICK_Y':10,
    'MOTION_RESPONSE_END':11,
    'BREAK_ONSET':12,
    'BREAK_END':13,
    'FEEDBACK_ONSET': 14,
    'OVERTIME': 15,
    'TASK_END':StimToolLib.TASK_END
    }


def update_target_and_wait(duration):
    start_time = g.clock.getTime()
    now = g.clock.getTime()
    while now - start_time < duration:
        #print(g.joy.getY())
        #print(g.joy._device.y)
        #g.joy.getY()
        update_target_pos()
       # StimToolLib.check_for_esc()
        g.win.flip()
        now = g.clock.getTime()

def three_beeps(trials_left):
    #print(g.joy.getY())
    g.joy.getY() # clear y pos
    g.vehicle.pos = g.vehicle_start_pos#reset car position
    g.msg.setText(str(trials_left) + ' trial(s) left in this block')
    g.msg.autoDraw = True
    g.timer_msg.setText('Trial starts in 2s')
    g.timer_msg.autoDraw = True
    g.win.flip()
    g.sound_beep1.play()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BEEP'], g.clock.getTime(), 'NA', 'NA', 0, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    update_target_and_wait(1)
    #StimToolLib.just_wait(g.clock, g.clock.getTime() + 1)
    g.timer_msg.setText('Trial starts in 1s')
    g.win.flip()
    g.sound_beep1.play()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BEEP'], g.clock.getTime(), 'NA', 'NA', 0, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    update_target_and_wait(1)
    #StimToolLib.just_wait(g.clock, g.clock.getTime() + 1)
    g.timer_msg.autoDraw = False
    g.msg.autoDraw = False
    g.sound_beep2.play()
    g.third_beep_time = g.clock.getTime() #in speed-and-stop trials, used to determine reaction time
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BEEP'], g.third_beep_time, 'NA', 'NA', 1, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

def update_car(): #update position of car based on joy position
    """
    Function that udpates the car
    """
    #t1 = g.clock.getTime()
    #dt = 1.0/60 #based on a single frame--assumes 60 hz frame rate
    now = g.clock.getTime()
    g.this_t = now #g.clock.getTime()
    if not g.last_t == None:
        dt = g.this_t - g.last_t
    else:
        dt = 1.0/60 #based on a single frame--assumes 60 hz frame rate
    
  
    joy_y_pos = -g.joy.getY() #negate so that push is positive, pull is negative
    joy_x_pos = g.joy.getX() #save this value, just in case it ends up being interesting

    #print(g.joy.getY())
    #print('%f - %f - %f' % (g.vehicle.pos[1], g.stop_sign.pos[1], g.fast_tolerence))

    # Mark time when it crosses the tolerence line
    if not g.fast_tolerence_onset:
        if ( (g.vehicle.pos[1]) > ( 3 - g.fast_tolerence)) and ( (g.vehicle.pos[1]) < ( 3 + g.fast_tolerence)):
            g.fast_tolerence_onset = g.clock.getTime()
            print('Tolerence Onset %f' % g.fast_tolerence_onset)
    
    #g.grating.setPos((joy_x_pos - 1 , joy_y_pos))
    
    if g.condition == 'velocity':
        # Velocity Condition, also the default condition
        g.dy =  (g.A*(g.vehicle.pos[1] + 8.0) + g.B*joy_y_pos) * dt #change in car position: A term gives resting point (at 0.35) and B gives velocity based on joystick position
     
    else:

        # Scanner Joystick has lower angle
        # Current Designs Joystck Angle is full 30 degrees
        # Practice Joystick - Logitech Extreme 3D Pro is 40 degrees
        if g.session_params['scan']: 
            joy_y_pos = joy_y_pos * 0.75
        # ICY Condition
        g.dy = g.B * joy_y_pos * dt * dt + (1 - g.C * dt) * g.dy  # Icy C
        
    

    #dy = 5 / 60.0
    now = g.clock.getTime()
    if g.response_period_start == None: #first response, record the time and mark the event
        g.response_period_start = now
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE_PERIOD_ONSET'], now, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['CAR_POSITION_AND_VELOCITY'], now, now - g.response_period_start, g.vehicle.pos[1], g.dy * 60, False, g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['STICK_X'], now, now - g.response_period_start, joy_x_pos, 'NA', False, g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['STICK_Y'], now, now - g.response_period_start, joy_y_pos, 'NA', False, g.session_params['parallel_port_address'])

    g.vehicle.pos = [g.vehicle.pos[0], g.vehicle.pos[1] + g.dy] #update car position 
    g.last_t = now
    #g.grating.draw()
    g.win.flip()


def update_target_pos():
    g.target.pos = [g.target.pos[0], -g.joy.getY() * 5] #target position: will range from -5 to 5 cm
def move_go_trial(speed):
    motion_per_frame = speed / 60 #speed is in cm/s, motion per frame is cm/frame--assuming 60 hz monitor
    delay_time = random.randint(1, 3) #will wait 1, 2, or 3s before the car starts to move
    #show number of trials left
    g.win.flip() #display initial screen--car on bottom, #trials remaining shown
    start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['DELAY_ONSET'], start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    while g.clock.getTime() - start_time < delay_time:
        StimToolLib.check_for_esc()
        g.win.flip() #have to flip the window to get the recent joystick position
        joy_pos = -g.joy.getY()
        g.target.pos = [g.target.pos[0], joy_pos * 5] #target position: will range from -5 to 5 cm
        if abs(joy_pos) > g.stick_move_threshold:
            g.sound_error.play()
            now = g.clock.getTime()
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FALSE_START'], now, now - start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            update_target_and_wait(3)
            #StimToolLib.just_wait(g.clock, g.clock.getTime() + 3)
            return False #will cause this trial to be repeated
    #begin car movement and wait for response
    recorded_motion_start = False
    while abs(joy_pos) < g.stick_move_threshold: 
        joy_pos = -g.joy.getY()
        StimToolLib.check_for_esc()
        g.target.pos = [g.target.pos[0], joy_pos * 5] #target position: will range from -5 to 5 cm
        g.vehicle.pos = [g.vehicle.pos[0], g.vehicle.pos[1] + motion_per_frame] #update car position 
        g.win.flip()
        if not recorded_motion_start: #record motion start here so it is *after* the first flip() with the car moved--slightly more accurate (1-16ms) than if this were before the loop
            recorded_motion_start = True
            g.motion_start_time = g.clock.getTime()

            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['MOTION_ONSET'], g.motion_start_time, 'NA', 'NA', speed, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.response_period_start = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE_PERIOD_ONSET'], g.response_period_start, g.response_period_start - g.motion_start_time , 'NA', g.vehicle.pos[1] + 8, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    done = False
    complete_press_time = None #keep track of when the joy stick made it to the end
    while not done:
        StimToolLib.check_for_esc()
        joy_pos = -g.joy.getY()
        update_car()
        update_target_pos()
        if joy_pos < 1:
            complete_press_time = g.clock.getTime()
        elif g.clock.getTime() - complete_press_time > 0.5: #wait until subject holds the joy stick at the end for 0.5s
            done = True
            g.sound_correct.play()
            now = g.clock.getTime()
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['MOTION_RESPONSE_END'], now, now-g.response_period_start, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            update_target_and_wait(2)
    g.response_period_start = None
    return True #success, move on to the next trial
    #wait for delay_time--repeat trial if move too soon
    
    #start moving the car and wait for response

def move_go_block(n_trials):
    g.vehicle = g.car
    g.vehicle.autoDraw = True
    #g.target.autoDraw = True
    random.shuffle(g.move_go_speeds)
    speed_idx = 0 #keep track of which speed is next--will be reset to 0 when all speeds have been used
    for i in range(n_trials):
        g.fast_tolerence_onset = None # Reset each trial
        if speed_idx == len(g.move_go_speeds):
            speed_idx = 0
            random.shuffle(g.move_go_speeds)
        success = False
        while not success: #keep repeating while subject has false starts
            g.target.pos = [g.target.pos[0], 0] 
            three_beeps(n_trials - i)
            success = move_go_trial(g.move_go_speeds[speed_idx])
            update_target_and_wait(1)
        g.trial = g.trial + 1
        speed_idx = speed_idx + 1
    g.vehicle.autoDraw = False
    #g.target.autoDraw = False
    
def update_timer(time_elapsed):
    #draws the timer bar: with time_elapsed=0, should be full length and with time_elapsed=10 will be gone
    #will be blue or green depending on car position (far from or close to stop sign)
    if g.target_pos - g.vehicle.pos[1] > 3 or g.target_pos < g.vehicle.pos[1]:
        pt_bar = g.bar_blue
    else:
        pt_bar = g.bar_green
    if time_elapsed < 10 - 0.04: #when there are two frames left, set height to 0 
        height = (10.0 - time_elapsed) / 10 * g.time_bar_max_height 
    else:
        height = 0 
    pt_bar.size = (g.bar_width, height ) 
    pt_bar.pos = (pt_bar.pos[0], height / 2) #adjust the position, since the position is where the midpoint of the image sits
    pt_bar.draw()
    pass
    
def drive_car(duration, draw_timer):
    #let the subject drive the car for duration seconds
    #also optionally updates the timer bar
    done = False
    while not done:
        update_car() #will set g.response_period_start the first time it's called each trial
        time_elapsed = g.clock.getTime() - g.response_period_start
        StimToolLib.check_for_esc()
        if draw_timer:
            update_timer(time_elapsed)
        if time_elapsed > duration:
            done = True
            g.sound_timeout.play()

            if g.show_feedback:
                g.feedback_text.text = get_feedback_text()
                g.feedback_text.draw()
                g.win.flip()
                now = g.clock.getTime()
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FEEDBACK_ONSET'], now, 'NA', 'NA', g.feedback_text.text, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            StimToolLib.just_wait(g.clock, g.clock.getTime() + 2)
    g.response_period_start = None #reset this for the next time--update_car will set g.response_period_start the first time it's called
            

def get_feedback_text():
    """
    Returns the feedback string condition.

    """
    # Vehicle Position gets with tolerence of stopsign in X amount of time
    if g.response_period_start and g.fast_tolerence_onset:
        if (g.fast_tolerence_onset - g.response_period_start) < g.fast_speed:
            # Means this is a 'fast' triall
            return g.feedback_text_dict['fast']

    return g.feedback_text_dict['slow']

def speed_stop_trial(trial_length = 10, threshold=True):
   # event.clearEvents()# flush
    #print(g.joy.getY())
    g.last_t = None

    # If threshold is set, and we are still within the max_set trial time
    # # then check move threshold to repeat
    # If not, then then don't check if in middle
    if threshold:
        joy_pos = abs(g.joy.getY())
        print('Onset joy Pos: %s' % joy_pos)
        if joy_pos > g.stick_move_threshold: #will be true if the subject was holding the stick off center at the end of the countdown
            g.sound_error.play()
            g.errorText.draw()
            g.win.flip()
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FALSE_START'], g.clock.getTime(), 'NA', 'NA', str(g.joy.getY()), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            false_start_onset = g.clock.getTime() + 2
            #event.clearEvents()# flush
           # g.joy.getY()
            while g.clock.getTime() < false_start_onset:
                #print('after:%s' % g.joy.getY())
                g.errorText.draw()
                g.win.flip()
           
            return False #will cause this trial to be repeated

    g.response_period_start = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RESPONSE_PERIOD_ONSET'], g.response_period_start, g.response_period_start - g.third_beep_time , 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    drive_car(trial_length, True)
    return True #success, move on to the next trial
    

def check_overtime():
    """
    Sets the reached_max_run time.
    """
    # Check the difference of how long it has been since task start
    # by the allowed set max run time minus the lead out time.
    # Lead out tiime is 10 seconds
    
    elapsed_time = g.clock.getTime() - g.task_start_time # current runtime elapsed time
    time_left = g.max_run_time - elapsed_time 

    # a valid trial takes about 12 seconds
    # 22 = lead out time + extra trial

    # So check if there's enough time left for the lead out and another trial
    if time_left <= 17:
        g.reached_max_runtime = True
        now = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['OVERTIME'], now, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

def speed_stop_block(n_trials):
    g.vehicle = g.car
    g.stop_sign.autoDraw = True
    g.vehicle.autoDraw = True
    g.time_text[0].autoDraw = True
    g.time_text[1].autoDraw = True
    trial_duration = 0 # records the duration of how long it's been
    for i in range(n_trials):
        success = False
        g.fast_tolerence_onset = None # Reset each trial
        # Don't to more trial if we reached our max_run_time
        if g.reached_max_runtime: break

         #keep repeating while if joystick is not centered 
        while not success:
            check_overtime()
            if g.reached_max_runtime: break
            three_beeps(n_trials - i)
            success = speed_stop_trial(threshold = True)
            end_onset = g.clock.getTime() + 1
            update_target_and_wait(1)
            # g.timer_msg.setText('Trial starts in 3s')
            # while g.clock.getTime() < end_onset: 
            #     g.msg.draw()
            #     g.timer_msg.draw()
            #     g.win.flip()
            #StimToolLib.just_wait(g.clock, g.clock.getTime() + 1)
        g.trial = g.trial + 1 #increment trial number
    g.vehicle.autoDraw = False
    g.stop_sign.autoDraw=False
    g.time_text[0].autoDraw = False
    g.time_text[1].autoDraw = False
    
    
def speed_stop_block_traction(n_trials):
    """
    Function to run block with traction.
    """
    g.vehicle = g.motorcycle
    g.stop_sign.autoDraw = True
    g.vehicle.autoDraw = True
    g.time_text[0].autoDraw = True
    g.time_text[1].autoDraw = True
    for i in range(n_trials):
        g.fast_tolerence_onset = None # Reset each trial
        # set trial duration
        # trial_length = random.choice([9,10,11])
        g.dy = 0
        trial_length = 10 # All trials are 10 seconds
        success = False
        
        while not success: #keep repeating while subject has false starts
            check_overtime()
            if g.reached_max_runtime: break
            three_beeps(n_trials - i)
            success = speed_stop_trial(trial_length, threshold=True)
            end_onset = g.clock.getTime() + 1
            update_target_and_wait(1)
            # g.timer_msg.setText('Trial starts in 3s')
            # while g.clock.getTime() < end_onset:
            #     g.msg.draw()
            #     g.timer_msg.draw()
            #     g.win.flip()
            #StimToolLib.just_wait(g.clock, g.clock.getTime() + 1)
        g.trial = g.trial + 1 #increment trial number
    g.vehicle.autoDraw = False
    g.stop_sign.autoDraw=False
    g.time_text[0].autoDraw = False
    g.time_text[1].autoDraw = False
    
def run_instructions(instruct_schedule_file, g):
    #instructions from schedule file along with audio
    directory = os.path.dirname(instruct_schedule_file)
    fin = open(instruct_schedule_file, 'r')
    lines = fin.readlines()
    fin.close()
    slides = []
    for i in lines:
        slides.append(i.split(','))
    i = 0
    while i < len(slides):
        i = max(0, i + do_one_slide(slides[i], directory, g)) #do_one_slide may increment or decrement i, depending on whether 'enter' or 'backspace' is pressed


def run_instructions_joystick(instruct_schedule_file, g):
    # Instruction for using joysrick
    #core.rush(True)
    directory = os.path.dirname(instruct_schedule_file)
    fin = open(instruct_schedule_file, 'r')
    lines = fin.readlines()
    fin.close()
    slides = []
    for i in lines:
        slides.append(i.split(','))
    isounds=StimToolLib.load_inst_sounds(slides,directory,g)
    i = 0
    g.triggered = False
    while i < len(slides):
        i = max(i + do_one_slide_joystick(slides[i], isounds[i], directory, g), 0) #do_one_slide may increment or decrement i, depending on whether session_params['right'] or session_params['left'] is pressed--don't let them go back on the first slide
    #core.rush(Fals


def show_demo_video(directory):
    """
    Function that plays the demo video
    """
    demo_mov = visual.MovieStim3(g.win, os.path.join(directory, 'demo_video', 'driving_demo.mov'), 
        size=(g.win.size[0], g.win.size[1]), flipVert=False, flipHoriz=False, loop=False)

    #screen_mov = visual.MovieStim3(g.win, os.path.join(directory, 'demo_video', 'screen_demo.mp4'), 
    #    size=(g.win.size[0], g.win.size[1]), flipVert=False, flipHoriz=False, loop=False)

    #joystick_mov = visual.MovieStim3(g.win, os.path.join(directory, 'demo_video', 'joystick_demo.mp4'),
    #    pos = [300,-200], size=(g.win.size[0] / 4, g.win.size[1] / 4), flipVert=False, flipHoriz=False, loop=False)


    while demo_mov.status != visual.FINISHED:
        demo_mov.draw()
        #joystick_mov.draw()
        g.win.flip()
        if (event.getKeys(['z'])):
            break
    


def do_one_slide_joystick(slide, isound, directory, g):
    """
    Run one slide of joystick instructions
    """
    # Allow the JOystick have some time to update before 
    #StimToolLib.just_wait(g.clock, g.clock.getTime() + .2)
    time.sleep(.1)
    if slide[0] == 'DEMO_VIDEO':
        show_demo_video(directory)
        return 1

    if slide[0] == 'DEMO':
        g.vehicle = g.car #TODO make demo work with motorcycle too
        g.vehicle.pos = g.vehicle_start_pos#reset car position
        g.stop_sign.autoDraw = True
        g.vehicle.autoDraw = True
        try:
            while g.vehicle.pos[1] < 2.85:
                StimToolLib.check_for_esc()
                g.vehicle.pos = [0, min(g.vehicle.pos[1] + g.B / 120, 2.85)] #g.B is maximum speed in cm/s--go at half speed for demo
                g.win.flip()
            StimToolLib.just_wait(g.clock, g.clock.getTime() + 1)
        except StimToolLib.QuitException:
            g.stop_sign.autoDraw = False
            g.vehicle.autoDraw = False
            return -1
        g.stop_sign.autoDraw = False
        g.vehicle.autoDraw = False
        g.win.flip()
        return 1

    if slide[0] == 'PRACTICE':
        g.vehicle.pos = g.vehicle_start_pos
        g.stop_sign.autoDraw = True
        g.vehicle.autoDraw = True
        g.win.flip() #display initial screen--car on bottom
        try:
            drive_car(20, False)
        except StimToolLib.QuitException:
            g.vehicle.autoDraw = False
            g.stop_sign.autoDraw = False
            return -1
        g.vehicle.autoDraw = False
        g.stop_sign.autoDraw = False
        g.win.flip()
        return 1
    image = visual.ImageStim(g.win, image=os.path.join(directory, slide[0]), units='pix')
    try:
        image.size = [ g.session_params['screen_x'], g.session_params['screen_y'] ]
    except:
        pass
    s=isound
    advance_time = float(slide[2])

    #if it's -1, don't advance, if it's 0, advance at the end of the sound, if it's positive, advance after that amount of time
    wait_z = False
    if advance_time == -1:
        advance_time = float('inf')
    elif advance_time == 0:
        try:
            advance_time = s.getDuration()
        except AttributeError: #in case there is a None in stead of a sound, just set duration to 0.5
            advance_time = 0.5
    elif advance_time == -2: #wait for a 'z' to advance
        advance_time = float('inf')
        wait_z = True
    
    image.draw()
    g.win.flip()
    event.clearEvents()
    image.draw()
    g.win.flip()
    event.clearEvents()
    image.draw()
    g.win.flip()

    
    k = None #initialize k
    
    if s:
        s.play()
        advance_time = advance_time - s.getDuration() #since we're waiting for the duration of s, decrease advance_time by that amount--allows for e.g. advance_time of 5s with a sound of 3s->wait 2s after the sound ends
        k = event.waitKeys(keyList = ['z', 'a', 'escape'], maxWait=s.getDuration()) #force the subject to listen to all of the instructions--allow 'z' to skip them or 'a' to force back
    if not k: #if skipped instructions, don't wait to advance afterword
        if g.session_params['allow_instructions_back']: #only allow back if it's specified in the session parameters
            kl = [g.session_params['left'], g.session_params['right'], 'escape', 'z', 'a']
        else:
            kl = [g.session_params['right'], 'escape', 'z', 'a']
        if wait_z: #only advance for a 'z'
            kl = ['z', 'a']
        
        timeout=False
        now=g.clock.getTime()
      
        event.clearEvents()
        time.sleep(.5)
        g.joy.getButton(g.session_params['joy_forward'])
        g.joy.getButton(g.session_params['joy_backward'])

        print(image._imName)
        print(g.joy.getButton(g.session_params['joy_forward']))
        while 1:
            #if not g.session_params['joystick']: break # Break out of this if wer're not using a joystick
            if g.clock.getTime() > now + advance_time:
                timeout=True 
                print('timed out')
                break
            k=event.getKeys(keyList = kl)
            if k!=[]:
                print('pressed key')
                break
            if g.joy.getButton(g.session_params['joy_forward']) or g.joy.getButton(g.session_params['joy_backward']):
                print('joystick clicked')
                break
            image.draw()
            event.clearEvents()
            g.win.flip()
            #print('in loop')
            #print(image._imName)
            #print(g.joy.getButton(g.session_params['joy_forward']))
            #time.sleep(.1)


    if s: #stop the sound if it's still playing
        s.stop()
    try:
        if g.joy.getButton(g.session_params['joy_forward']) or timeout:
            retval = 1
        elif g.joy.getButton(g.session_params['joy_backward']):
            retval = -1
    except (AttributeError, UnboundLocalError, IndexError):
        joystick_not_used=True
                
    if k == None or k == []: #event timeout
        print('')
    elif k[0] == 'z':
        retval = 1
    elif k[0] == 'a':
        retval = -1
    elif k[0] == g.session_params['right']:
        print(k[0])
        retval = 1
    elif k[0] == g.session_params['left']:
        retval = -1
    elif k[0] == 'escape':
         raise StimToolLib.QuitException()
    return retval

def do_one_slide(slide, directory, g):
    if slide[0] == 'DEMO':
        g.vehicle.pos = g.vehicle_start_pos#reset car position
        g.stop_sign.autoDraw = True
        g.vehicle.autoDraw = True
        try:
            while g.vehicle.pos[1] < 2.85:
                StimToolLib.check_for_esc()
                g.vehicle.pos = [0, min(g.vehicle.pos[1] + g.B / 120, 2.85)] #g.B is maximum speed in cm/s--go at half speed for demo
                g.win.flip()
            StimToolLib.just_wait(g.clock, g.clock.getTime() + 1)
        except StimToolLib.QuitException:
            g.stop_sign.autoDraw = False
            g.vehicle.autoDraw = False
            return -1
        g.stop_sign.autoDraw = False
        g.vehicle.autoDraw = False
        g.win.flip()
        return 1
    if slide[0] == 'PRACTICE':
        g.vehicle.pos = g.vehicle_start_pos
        g.stop_sign.autoDraw = True
        g.vehicle.autoDraw = True
        g.win.flip() #display initial screen--car on bottom
        try:
            drive_car(20, False)
        except StimToolLib.QuitException:
            g.vehicle.autoDraw = False
            g.stop_sign.autoDraw = False
            return -1
        g.vehicle.autoDraw = False
        g.stop_sign.autoDraw = False
        g.win.flip()
        return 1
    image = visual.ImageStim(g.win, image=os.path.join(directory, slide[0]))
    if slide[1] == 'None':
        s = None
    else:
        s = sound.Sound(value = os.path.join(directory, slide[1]), volume=g.session_params['instruction_volume'])
    advance_time = float(slide[2])
    #if it's -1, don't advance, if it's 0, advance at the end of the sound, if it's positive, advance after that amount of time
    if advance_time == -1:
        advance_time = float('inf')
    elif advance_time == 0:
        try:
            advance_time = s.getDuration()
        except AttributeError: #in case there is a None in stead of a sound, just set duration to 0.5
            advance_time = 0.5
    image.draw()
    g.win.flip()
    k = None
    if s:
        s.play()
        advance_time = advance_time - s.getDuration() #since we're waiting for the duration of s, decrease advance_time by that amount--allows for e.g. advance_time of 5s with a sound of 3s->wait 2s after the sound ends
        k = event.waitKeys(keyList = ['z', 'a', 'escape'], maxWait=s.getDuration()) #force the subject to listen to all of the instructions--allow 'z' to skip them or 'a' to force back
    if not k: #if skipped instructions, don't wait to advance afterword
        if g.session_params['allow_instructions_back']: #only allow back if it's specified in the session parameters
            kl = [g.session_params['left'], g.session_params['right'], 'escape']
        else:
            kl = [g.session_params['right'], 'escape']
        k = event.waitKeys(keyList = kl, maxWait=advance_time)
    if s:
        s.stop()
    if k == None: #event timeout
        return 1
    if k[0] == 'z':
        retval = 1
    if k[0] == 'a':
        retval = -1
    if k[0] == g.session_params['right']:
        retval = 1
    if k[0] == g.session_params['left']:
        retval = -1
    if k[0] == 'escape':
        raise StimToolLib.QuitException()
    return retval
    
    
def move_go_instruct(n_trials):
    run_instructions_joystick(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'DR_instruct_schedule_MG.csv'), g)
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)
    
def speed_stop_instruct(n_trials):
    run_instructions_joystick(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)

def do_one_block(block_type, block_length):
    g.trial_type = block_type #set trial type to be written to output file
    if block_type == '0': #move_go_instructions
        start_time = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['INSTRUCT_ONSET'], start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        move_go_instruct(block_length)
        now = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TASK_ONSET'], now, now - start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    if block_type == '1': #move_go_block
        g.trial_type = 1 #set trial type for output for this block
        move_go_block(block_length)
    if block_type == '2': #speed_stop_instructions
        start_time = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['INSTRUCT_ONSET'], start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        speed_stop_instruct(block_length)
        now = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TASK_ONSET'], now, now - start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    if block_type == '3': #speed_stop_block
        g.trial_type = 3 #set trial type for output for this block
        speed_stop_block(block_length)

    # Speed Stop with differente traction
 
    # 1st digit means the condition, either 3 or 4
    # 2nd digit means it's the traction control value (g.C)
    if (len(block_type) == 2):
        g.trial_type = block_type

        if block_type[0] == '3':
            # Use the sensitivity Condition
            # The LSB is the sensitivity values.
            # High / Mid /Low 
            # 40: High, 41: Mid , 42: Low
            g.condition = 'velocity' # b
            g.B = g.sensitivity_map[block_type[1]]
            speed_stop_block(block_length)
        
        if block_type[0] == '4':
            # Use ICY Condition
            # Ths LSB is the traction g.C value. 30 = 0, 31 = 1, 32 = 2
            g.condition = 'acceleration'
            g.C = float(block_type[1])
            speed_stop_block_traction(block_length)



    if block_type == '4': #break
        start_time = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BREAK_ONSET'], start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        StimToolLib.show_instructions(g.win, ['Now please take a 5 second break'])
        end_time = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BREAK_END'], end_time, end_time - start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.win.flip()
    
    if block_type == '5': #break with fixation , specified duration
        start_time = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BREAK_ONSET'], start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.win.flip()
        g.fix.draw()
        g.win.flip()
        StimToolLib.just_wait(g.clock,start_time + float(block_length) )
        end_time = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BREAK_END'], end_time, end_time - start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.win.flip()

    if (len(block_type) == 3):
        # Break Fixation with text on top
        # the 2 index determines what traction to say
        start_time = g.clock.getTime()
        g.win.flip()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BREAK_ONSET'], start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        if (block_type[0] == '3'):
            text_dict = {
                '0': "sensitivity: extralow", # g.C of 0, does mean its more slick/slippery
                '1': "sensitivity: low",
                '2': "sensitivity: high"
            } 
        if block_type[0] == '4':
            text_dict = {
                '0': "slickness: high", # g.C of 0, does mean its more slick/slippery
                '1': "slickness: medium",
                '2': "slickness: low"
            }
        g.toptext.text = text_dict[block_type[2]]
        g.toptext.draw()
        g.fix.draw()
        g.win.flip()
        StimToolLib.just_wait(g.clock,start_time + float(block_length) )
        end_time = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BREAK_END'], end_time, end_time - start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.win.flip()


    StimToolLib.just_wait(g.clock, g.clock.getTime() + 1) #one second pause at the end of each block so the next one doesn't start immediately


def counterBalance(block_types):
    """
    Reverse orders the block based on subject id
    Also, don't reverse if it'a practic run
    """

    if not g.session_params['scan']:
        print('not a scan, do not reverse')
        return block_types

    # If subject id is even, return as is, if not, reverse it.
    id_number = ''
    while True:
        try:
            id_number = int(g.session_params['SID'][2:]) # returns only the numeric nubmers. BM123 -> 123
            break
        except Exception as e:
            myDlg = gui.Dlg(title = 'Subject ID Correction')
            myDlg.addText('ID must be 5 characters and end in 3 numbers, apparently it does not')
            myDlg.addField('ID', initial='')
            myDlg.show()
            thisInfo = myDlg.data
            sid = thisInfo[0]
            g.session_params['SID'] = sid
            print(e)
    
    if id_number %2 == 0: return block_types # Event

    # If it gets past here it must mean it's an odd number

    # Make list of tuples for non '2' trial
    order_trials = []
    for idx, block in enumerate(block_types):
        if block == '2': continue
        if block[0] == '5': order_trials.append([block, block_types[idx + 1 ]])

    
    order_trials.reverse() # reverse the order

    # Now put it back into a list
    new_order = []

    # If there is an instruction block in the schedule added it
    if block_types[0] == '2': new_order.append('2')

    for block in order_trials:
        new_order.append(block[0])
        new_order.append(block[1])
    
    print('new order:')
    print(new_order)
    return new_order


def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/DR.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    
    ### IMPORTANT LINE! ###
    # Correctly close device after each run
    # This is so that the next run when using joystick doesn't have errors polling x/y postions.
    g.joy._device.close()
    #######################
    StimToolLib.task_end(g)
    return g.status
        
def run_try():  
#def run_try(SID, raID, scan, resk, run_num='1'):
    
    #setup the joystick
    
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="DR")
        myDlg.addField('Run Number', choices=schedules, initial=str(g.run_params['run']))
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    StimToolLib.general_setup(g)
    joystick.backend= g.win.winType
    nJoysticks=joystick.getNumJoysticks()
    if nJoysticks>0:
        g.joy = joystick.Joystick(0)
        #print('joystick attr device')
        #print(dir(g.joy._device))
    else:
        g.win.close()
        #try:
        StimToolLib.error_popup("You don't have a joystick connected?")
        #except StimToolLib.QuitException:
        #    return -1
            
    
    #g.resk = resk

    g.timer_msg = visual.TextStim(g.win,text="",units='pix',pos=[0,-50],color=[1,1,1],height=30,wrapWidth=int(1600))
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_DR_Schedule' + str(g.run_params['run']) + '.csv')
    block_types,junk,block_lengths,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    block_lengths = block_lengths[0] 

    # Counterbalancing Schedule
    print('counterbalancing')
    print('Before')
    print(block_types)
    #don't worry about counterbalancing for now
    #block_types = counterBalance(block_types)
    print('After')
    print(block_types)
    


    start_time = data.getDateStr()
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    fileName = os.path.join(g.prefix + '.csv')

    # Set Params if any
    try:
        g.stick_move_threshold = g.run_params['stick_move_threshold']
    except:
        pass
    try:
        g.max_run_time = float(g.run_params['max_run_time'])
    except:
        pass
    try:
        g.A = float(g.run_params['A'])
    except Exception as e:
        print(e)
        pass
    try:
        g.fast_tolerence = float(g.run_params['fast_tolerence']) # the distance away from stop
    except Exception as e:
        pass
    try:
        g.fast_speed = float(g.run_params['fast_speed']) # the max time in seconds to be consider a 'fast' condition
    except Exception as e:
        pass
    try:
        g.show_feedback = g.run_params['show_feedback']
    except:
        print('no show_feedback params found, assuming False')
        g.show_feedback = False

    
    #g.prefix = 'DR-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time 
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  schedule_file + ',Event Codes:,' + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')

    g.motorcycle = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/motorcycle_new.png'), units='cm', interpolate=True)
    g.car = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/car2.bmp'), units='cm', interpolate=True, mask=os.path.join(os.path.dirname(__file__),'media/car_mask.bmp'))
    g.bar_green = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_green.png'), pos=(g.bar_x, 0), units='norm')
    g.bar_blue = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/bar_blue.png'), pos=(g.bar_x, 0), units='norm')
    g.stop_sign = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/stop.png'), pos=(0, g.stop_y), units='cm', interpolate=True)
    g.target = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/circle_white.png'), pos=[6, 0], units='cm')
    g.sound_correct = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/correctsound.aiff'), volume=0.08)
    g.sound_error = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/errorsound.aiff'), volume=0.08)
    g.sound_double_error = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/doubleerrorsound.aiff'), volume=0.08)
    g.sound_beep1 = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/beep1.aiff'), volume=0.08)
    g.sound_beep2 = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/beep2.aiff'), volume=0.08)
    g.sound_timeout = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/timeoutsound.aiff'), volume=0.08)
    
    g.time_text.append(visual.TextStim(g.win, text="10s", units='norm', height=.07, color=[1,1,1], pos=[g.bar_x - .1,g.time_bar_max_height - .07]))
    g.time_text.append(visual.TextStim(g.win, text="0s", units='norm', height=.07, color=[1,1,1], pos=[g.bar_x - .1,0]))
    
    g.fix = visual.TextStim(g.win, text="+", units='pix', height=50, color=[1,1,1], pos=[0,0], bold=True)
    g.toptext = visual.TextStim(g.win, text="", units='pix', height=50, color=[1,1,1], pos=[0,200], bold=True)

    g.feedback_text = visual.TextStim(g.win, text=g.feedback_text_string, units='pix', height=50, color=[1,1,1], pos=[300,0], bold=True)
    g.errorText = visual.TextStim(g.win, text="ERROR:\nCenter the joystick.", units='pix', height=40, color=[1,-1,-1], pos=[0,0], bold=True)

    g.grating = visual.GratingStim(g.win, pos=(0.5, 0),tex="sin", mask="gauss",color=[1.0, 0.5, -1.0],size=(0.2, .2), sf=(2, 0))
    
    StimToolLib.task_start(StimToolLib.DRIVE_CODE, g)
    g.win.flip()


    try:
        run_instructions_joystick(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    except:
        pass


    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win)
    else:
        StimToolLib.wait_start(g.win)

    g.task_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TASK_ONSET'], g.task_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    # Lead in 10s Fixation Time
    now = g.clock.getTime()
    g.win.flip()
    g.fix.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, now + 10 ) # 10 second fixation lead in time

    g.trial = 0 #initialize trial number
    #StimToolLib.show_title(g.win, g.title)
    for i in range(len(block_types)):
        if g.reached_max_runtime: break
        do_one_block(block_types[i], int(block_lengths[i]))

    # Lead out 10s Fixation Time
    now = g.clock.getTime()
    g.win.flip()
    g.fix.draw()
    g.win.flip()
    StimToolLib.just_wait(g.clock, now + 10 ) # 10 second fixation lead in time




