
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
        self.left_pos = (-.3, -.2)
        self.righ_pos = (.3, -.2)
        self.transprob = .8 # Probability of 'correct transition

event_types = {
    'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'TRIAL_ONSET': 3,
    'FIXATION_ONSET':4, 
    'LEVEL1_ONSET': 5,
    'LEVEL1_RESPONSE':6,
    'ANIMATE':7,
    'LEVEL2_ONSET': 8,
    'LEVEL2_RESPONSE':9, 
    'OUTCOME': 10,
    'TASK_END':StimToolLib.TASK_END
    }


    
def do_one_trial(trial):
    """
    Function for 1 trial
    """
    ## First Level
    level  = 1
    
    planetpic = g.earth
    choice, stimleft, stimright = halftrial(planetpic, g.rocket['practice'][1],g.rocket['practice'][2] , level)
    print('Level 1')
    print('Choose: %s' % choice)

    if choice == 0: return

    # Determine which planet we go to 
    # Logic from Matlab COd is the xor resultant of the transition probability with chosen choice
    # state will return eith either 2 or 3.
    # Step to get this:
    # 1) Get either T or F from random probability. random number > transition probability
    # 2) Get either T or F from the sleected choice. T = chose 2, F  = chose 1
    # 3) XOR result of the (1) and (2)
    # 4) Add 2 of the resultant (3) to get either 2 or 3
    state =  2 + (bool(random.random() > g.transprob) != bool(choice  - 1))
    
    if state == 2:
        # Green Planet
        planetpic = g.planets['practice'][0]
        left_alien  = g.aliens['practice'][1]
        right_alien = g.aliens['practice'][2]
    if state == 3:
        # Yellow Planet
        planetpic = g.planets['practice'][1]
        left_alien  = g.aliens['practice'][3]
        right_alien = g.aliens['practice'][4]

    # 2nd Level
    level = 2

    print('Level 2')
    print('State %s' % state)

    if choice == 1: chosen_rocket = stimleft
    if choice == 2: chosen_rocket = stimright

    choice2, stimleft, stimright = halftrial(planetpic, left_alien, right_alien , level, chosen_rocket)

    if choice2 == 0: return
    

    # OutCome
    # Use the Proability Table
    # Porbability based on state and choice2
    money = random.random() < payoff(state - 1, choice2, trial)

    draw_outcome(money, choice2, stimleft, stimright )



def prep_propbabilit():
    """
    Prepering Probability Times
    """
    g.trials = []
    for prob in g.prob[0]:
        probability = [ 
            float(prob.split('_')[0]),
            float(prob.split('_')[1]),
            float(prob.split('_')[2]),
            float(prob.split('_')[3])
        ]
        g.trials.append(probability)
        

    print(g.trials)

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


def get_selections(response, planet):
    """
    Returns selected and non selected
    """
    if planet == 0 and response == '1': # chose left
        return 1,2
    if planet == 0 and response == '0': # chose right
        return 2,1
    if planet == 1 and response == '1': # chose left
        return 3,4
    if planet == 1 and response == '0': # chose right
        return 4,3
    

def draw_outcome(win, pos, stimleft,stimright ):
    """
    Draws eiter treasure or nothing
    """

    if pos == 1:
        g.treasure.pos = (stimleft['neutral'].pos[0],stimleft['neutral'].pos[1] + .27 )
        g.nothing.pos = (stimleft['neutral'].pos[0],stimleft['neutral'].pos[1] + .27 )
    if pos == 2:
        g.treasure.pos = (stimright['neutral'].pos[0],stimright['neutral'].pos[1] + .27 )
        g.nothing.pos = (stimright['neutral'].pos[0],stimright['neutral'].pos[1] + .27 )

    if win: outcome_image = g.treasure
    else: outcome_image = g.nothing

    outcome_image.draw()


    g.win.flip()
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output,g.trial, 'NA', event_types['OUTCOME'], now, 'NA', win ,outcome_image._imName , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.just_wait(g.clock, now + .3 )


def animatebox(planetpix, stimleft, stimright, choice):
    """
    Make Blink
    """
    print('Animating..')
    print(choice)
    if choice == 1:
        selectedAlien = stimleft
        selectedAlien['alternate'][0].pos = g.left_pos
        selectedAlien['alternate'][1].pos = g.left_pos
        nonSelectedAlien = stimright

        transition_pos = [
            g.left_pos, # (-.3, -.2)
            (-.225, -.075),
            (-.15, .05),
            (-.075, .175),
            (0, .3)
        ]

    if choice == 2:
        selectedAlien = stimright
        selectedAlien['alternate'][0].pos = g.righ_pos
        selectedAlien['alternate'][1].pos = g.righ_pos
        nonSelectedAlien = stimleft

        transition_pos = [
            g.righ_pos, # (.3, -.2)
            (.225, -.075),
            (.15, .05),
            (.075, .175),
            (0, .3)
        ]

    
    if choice == 0: return

    now = g.clock.getTime()
    StimToolLib.mark_event(g.output,g.trial, 'NA', event_types['ANIMATE'], now, 'NA', 'NA' ,'NA' , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])


    x_pos_increment = .05
    y_pos_increment = .05
    for idx in range(5):
        planetpix.draw()

        # Slowy change position to the center top
        selectedAlien['alternate'][0].pos = transition_pos[idx]
        selectedAlien['alternate'][1].pos = transition_pos[idx]
        if idx % 2 == 0: selectedAlien['alternate'][0].draw()
        else: selectedAlien['alternate'][1].draw()

        nonSelectedAlien['dark'].draw()

        g.win.flip()
        now = g.clock.getTime()
        StimToolLib.just_wait(g.clock, now + .03 )


def halftrial(planetpic, stimleft, stimright, level, chosen_rocket = '' ):
    """
    Half State
    """
    event.clearEvents()
    
    choice = 0

    planetpic.draw()

    stimleft['neutral'].pos = g.left_pos
    stimleft['neutral'].draw()

    stimright['neutral'].pos = g.righ_pos
    stimright['neutral'].draw()

    if chosen_rocket:
        chosen_rocket['neutral'].pos = (0,.3)
        chosen_rocket['neutral'].draw()

    level_onset = g.clock.getTime()
    if level == 1:
        StimToolLib.mark_event(g.output,g.trial, g.trial_type, event_types['LEVEL1_ONSET'], level_onset, 'NA',planetpic._imName ,stimleft['neutral']._imName + ' ' + stimright['neutral']._imName , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    if level == 2:
        StimToolLib.mark_event(g.output,g.trial, g.trial_type, event_types['LEVEL2_ONSET'], level_onset, 'NA',planetpic._imName ,stimleft['neutral']._imName + ' ' + stimright['neutral']._imName , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # Wait until key press
    g.win.flip()
    
    resp = event.waitKeys( keyList = ['1', '0', 'escape', 'z'])
    if resp[0] == "escape": raise StimToolLib.QuitException()
    if resp[0] == '1': choice = 1
    if resp[0] == '0': choice = 2
    if resp[0] == 'z': return 0,stimleft,stimright

    now = g.clock.getTime()

    if level == 1:
        StimToolLib.mark_event(g.output,g.trial, g.trial_type, event_types['LEVEL1_RESPONSE'], now, level_onset - now ,resp[0] ,choice , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    if level == 2:
        StimToolLib.mark_event(g.output,g.trial, g.trial_type, event_types['LEVEL2_RESPONSE'], now, level_onset - now ,resp[0] ,choice , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    

    animatebox(planetpic, stimleft, stimright, choice)

    planetpic.draw()
    if choice == 1:
        stimleft['neutral'].pos = (0 , .3)
        stimleft['neutral'].draw()
        stimright['dark'].draw()
    if choice == 2:
        stimright['neutral'].pos = (0 , .3)
        stimright['neutral'].draw()
        stimleft['dark'].draw()
   


    return choice, stimleft,stimright


def payoff(state, choice2, trial):
    """
    Returns the probability frmo the probability table

    Parameters
    ----------
    state : int, rquired
        The state integer, will be either 1 or 2

    choice2: int, required
        The choice selection from the halftrial, will be either 1 or 2

    trial: array, required
        List of probability, input schedule. Determined by the state and choice

    Returns:
    probability: float
    """
    probability = 0.0 # default probabilty
    if state == 1 and choice2 == 1: probability = trial[0]
    if state == 1 and choice2 == 2: probability = trial[1]
    if state == 2 and choice2 == 1: probability = trial[2]
    if state == 2 and choice2 == 2: probability = trial[3]
    return probability

def run_tutorial():
    """
    Runs Tutorial
    """
    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
    
    # Practice Selecting 
    for trial in range(3):
        event.clearEvents()

        g.planets['practice'][0].draw()

        g.aliens['practice'][1]['neutral'].draw()
        g.aliens['practice'][2]['neutral'].draw()

        if trial > 0:
            text = visual.TextStim(g.win, text = 'Now try another one', units = 'norm', pos = (0,.3), color = 'white')
            text.draw()

        g.win.flip()
        resp = event.waitKeys( keyList = ['1', '0', 'escape', 'z'])
        if resp[0] == "escape": raise StimToolLib.QuitException()
        if resp[0] == 'z': break
        selected, no_selected = get_selections(resp[0], 0)

        for idx in range(5):
            g.planets['practice'][0].draw()

            if idx % 2 == 0: g.aliens['practice'][selected]['alternate'][0].draw()
            else: g.aliens['practice'][selected]['alternate'][1].draw()

            g.aliens['practice'][no_selected]['dark'].draw()

            g.win.flip()
            now = g.clock.getTime()
            StimToolLib.just_wait(g.clock, now + .1 )

    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'TTT_instruct_scheduleP_2.csv'), g)

    # Share from 1 Alien
    # Set Positions

    g.aliens['practice'][3]['neutral'].pos = (0,0)
    g.aliens['practice'][3]['alternate'][0].pos = (0,0)
    g.aliens['practice'][3]['alternate'][1].pos = (0,0)
    g.treasure.pos = ( g.aliens['practice'][3]['neutral'].pos[0], g.aliens['practice'][3]['neutral'].pos[1] + .3)
    g.nothing.pos = ( g.aliens['practice'][3]['neutral'].pos[0], g.aliens['practice'][3]['neutral'].pos[1] + .3)

    for reward in [1,0,1,1,1,0,1,0,1,1]:
        event.clearEvents()
        
        g.planets['practice'][1].draw()
        g.aliens['practice'][3]['neutral'].draw()

        g.win.flip()
        resp = event.waitKeys( keyList = ['1', '0', 'escape', 'z'])
        if resp[0] == "escape": raise StimToolLib.QuitException()
        if resp[0] == '1': choice = 1
        if resp[0] == '0': choice = 2
        if resp[0] == 'z': break
        selected = 3 # It's always the 3rd alient

        for idx in range(5):
            g.planets['practice'][1].draw()

            if idx % 2 == 0: g.aliens['practice'][selected]['alternate'][0].draw()
            else: g.aliens['practice'][selected]['alternate'][1].draw()


            g.win.flip()
            now = g.clock.getTime()
            StimToolLib.just_wait(g.clock, now + .1 )
        
        # Draw planet
        g.planets['practice'][1].draw()

        # Draw Alient
        g.aliens['practice'][3]['neutral'].draw()

        # Draw outcome
        
        draw_outcome(reward, choice,g.aliens['practice'][selected], g.aliens['practice'][selected] )

    g.win.flip()

    # Change Back to original pos
    g.aliens['practice'][3]['neutral'].pos = g.left_pos
    g.aliens['practice'][3]['alternate'][0].pos = g.left_pos
    g.aliens['practice'][3]['alternate'][1].pos = g.left_pos
    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'TTT_instruct_scheduleP_3.csv'), g)

    # Right side Higher probability

    for trial in range(20):
        level = 0
        choice, stimleft, stimright = halftrial(g.planets['practice'][0], g.aliens['practice'][1],g.aliens['practice'][2], level)

        if choice == 0: break # User Skipped ths section

        if choice == 1: win = random.random() < .3
        if choice == 2: win = random.random() < .8

        draw_outcome(win, choice, stimleft, stimright )

    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'TTT_instruct_scheduleP_4.csv'), g)


    # Full Practice

    for trial in g.trials:
        ## First Level
        level  = 1
        
        planetpic = g.earth
        choice, stimleft, stimright = halftrial(planetpic, g.rocket['practice'][1],g.rocket['practice'][2] , level)
        print('Level 1')
        print('Choose: %s' % choice)

        if choice == 0: break

        # Determine which planet we go to 
        # Logic from Matlab COd is the xor resultant of the transition probability with chosen choice
        # state will return eith either 2 or 3.
        # Step to get this:
        # 1) Get either T or F from random probability. random number > transition probability
        # 2) Get either T or F from the sleected choice. T = chose 2, F  = chose 1
        # 3) XOR result of the (1) and (2)
        # 4) Add 2 of the resultant (3) to get either 2 or 3
        state =  2 + (bool(random.random() > g.transprob) != bool(choice  - 1))
        
        if state == 2:
            # Green Planet
            planetpic = g.planets['practice'][0]
            left_alien  = g.aliens['practice'][1]
            right_alien = g.aliens['practice'][2]
        if state == 3:
            # Yellow Planet
            planetpic = g.planets['practice'][1]
            left_alien  = g.aliens['practice'][3]
            right_alien = g.aliens['practice'][4]

        # 2nd Level
        level = 2

        print('Level 2')
        print('State %s' % state)

        if choice == 1: chosen_rocket = stimleft
        if choice == 2: chosen_rocket = stimright

        choice2, stimleft, stimright = halftrial(planetpic, left_alien, right_alien , level, chosen_rocket)

        if choice2 == 0: break
        

        # OutCome
        # Use the Proability Table
        # Porbability based on state and choice2
        money = random.random() < payoff(state - 1, choice2, trial)

        draw_outcome(money, choice2, stimleft, stimright )


    g.win.flip()
    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'TTT_instruct_scheduleP_5.csv'), g)


def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/AT.Default.params', {})
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
    g.trial_types,g.stim_files,junk, g.prob,  = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    
    
    prep_propbabilit()

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
    g.fixation = visual.TextStim(g.win, text = '+', units = 'norm', pos = (0,0))
    g.stim_text = visual.TextStim(g.win, text = '', units = 'norm', pos = (0,.1), color = 'black', height = .064, bold = True)

    ### Practice Images

   
    g.earth = visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media', 'earth.jpg' ))
    g.nothing = visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media', 'nothing.png' ), units = 'norm')
    g.treasure = visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media', 'treasure.png' ), units = 'norm')

    g.planets = {
        'practice' : [
            visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutgreenplanet.jpg' )),
            visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutyellowplanet.jpg' )),
        ],
        'main' : [
            visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'purpleplanet.jpg' )),
            visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'redplanet1.jpg' )),
        ]
    }

    g.aliens = {
        'practice': {
            1 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien1_n.png' ), units = 'norm', pos = g.left_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien1_d.png' ), units = 'norm', pos = g.left_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien1_s.png' ), units = 'norm', pos = g.left_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien1_a1.png' ), units = 'norm', pos = g.left_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien1_a2.png' ), units = 'norm', pos = g.left_pos)
                ]
            },
            2 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien2_n.png' ), units = 'norm', pos = g.righ_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien2_d.png' ), units = 'norm', pos = g.righ_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien2_s.png' ), units = 'norm', pos = g.righ_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien2_a1.png' ), units = 'norm', pos = g.righ_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien2_a2.png' ), units = 'norm', pos = g.righ_pos)
                ]
            },
            3 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien3_n.png' ), units = 'norm', pos = g.left_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien3_d.png' ), units = 'norm', pos = g.left_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien3_s.png' ), units = 'norm', pos = g.left_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien3_a1.png' ), units = 'norm', pos = g.left_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien3_a2.png' ), units = 'norm', pos = g.left_pos)
                ]
            },
            4 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien4_n.png' ), units = 'norm', pos = g.righ_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien4_d.png' ), units = 'norm', pos = g.righ_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien4_s.png' ), units = 'norm', pos = g.righ_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien4_a1.png' ), units = 'norm', pos = g.righ_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutalien4_a2.png' ), units = 'norm', pos = g.righ_pos)
                ]
            },
        },
        'main': {
            1 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien1_norm.png' ), units = 'norm', pos = g.left_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien1_deact.png' ), units = 'norm', pos = g.left_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien1_sp.png' ), units = 'norm', pos = g.left_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien1_a1.png' ), units = 'norm', pos = g.left_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien1_a2.png' ), units = 'norm', pos = g.left_pos)
                ]
            },
            2 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien2_norm.png' ), units = 'norm', pos = g.righ_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien2_deact.png' ), units = 'norm', pos = g.righ_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien2_sp.png' ), units = 'norm', pos = g.righ_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien2_a1.png' ), units = 'norm', pos = g.righ_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien2_a2.png' ), units = 'norm', pos = g.righ_pos)
                ]
            },
            3 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien3_norm.png' ), units = 'norm', pos = g.left_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien3_deact.png' ), units = 'norm', pos = g.left_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien3_sp.png' ), units = 'norm', pos = g.left_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien3_a1.png' ), units = 'norm', pos = g.left_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien3_a2.png' ), units = 'norm', pos = g.left_pos)
                ]
            },
            4 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien4_norm.png' ), units = 'norm', pos = g.righ_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien4_deact.png' ), units = 'norm', pos = g.righ_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien4_sp.png' ), units = 'norm', pos = g.righ_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien4_a1.png' ), units = 'norm', pos = g.righ_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'alien4_a2.png' ), units = 'norm', pos = g.righ_pos)
                ]
            },
        }
    }

    g.rocket = {
        'practice': {
            1 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutrocket1_n.png' ), units = 'norm', pos = g.left_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutrocket1_d.png' ), units = 'norm', pos = g.left_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutrocket1_s.png' ), units = 'norm', pos = g.left_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutrocket1_a1.png' ), units = 'norm', pos = g.left_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutrocket1_a2.png' ), units = 'norm', pos = g.left_pos)
                ]
            },
            2 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutrocket2_n.png' ), units = 'norm', pos = g.righ_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutrocket2_d.png' ), units = 'norm', pos = g.righ_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutrocket2_s.png' ), units = 'norm', pos = g.righ_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutrocket2_a1.png' ), units = 'norm', pos = g.righ_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','practice', 'tutrocket2_a2.png' ), units = 'norm', pos = g.righ_pos)
                ]
            }
        },
        'main': {
            1 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'rocket1_norm.png' ), units = 'norm', pos = g.left_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'rocket1_deact.png' ), units = 'norm', pos = g.left_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'rocket1_sp.png' ), units = 'norm', pos = g.left_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'rocket1_a1.png' ), units = 'norm', pos = g.left_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'rocket1_a2.png' ), units = 'norm', pos = g.left_pos)
                ]
            },
            2 : {
                'neutral' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'rocket2_norm.png' ), units = 'norm', pos = g.righ_pos),
                'dark' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'rocket2_deact.png' ), units = 'norm', pos = g.righ_pos),
                'slow' : visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'rocket2_sp.png' ), units = 'norm', pos = g.righ_pos),
                'alternate' : [
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'rocket2_a1.png' ), units = 'norm', pos = g.righ_pos),
                    visual.ImageStim(g.win, image = os.path.join( os.path.dirname(__file__), 'media','main', 'rocket2_a2.png' ), units = 'norm', pos = g.righ_pos)
                ]
            }
        }
    }
    

    StimToolLib.task_start(StimToolLib.ALIENS_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    if g.run_params['practice']:
        run_tutorial()
        g.transprob = .8
    else:
        g.transprob = .7
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

    g.trial_type = 'NA'

    for trial in g.trials:
        do_one_trial(trial)
        g.trial = g.trial + 1
