
import StimToolLib, os, random, operator, math, copy
from psychopy import visual, core, event, data, gui, sound

#Change Point Detection task

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
        self.dot_locations = [(-212, 212), (-78,-290), (290, 78)]#[(-212, 212), (-78,-290), (290, 78)]
        self.dots = [] #dot patches
        self.circles_white = [] #white circles that go over dot patches when they're not being displayed
        self.circles_red = [] #red circles used to illuminate correct response (when incorrect response is given)
        self.circles_green = [] #green circles used to show correct response
        self.bar_red = None
        self.bar_green = None #red and green point bars
        self.bar_x = -900 #x location of points bar (should be left side of the screen)
        self.bar_width = 100 #width of the point bars
        self.bar_max_height = 600
        self.trial = None #trial number
        self.trial_type = None #current trial type
        self.instructions = [
'''You are about to play 20 investment games in total. You want to earn 
                                   as much as possible.''',
'''In each game, you have 16 tokens (stacked in a row at the top of the 
                 screen) and 3 lotteries (vertical white panels).''',
'''You will have to place each token in the lottery panel of your choice.''',
'''To do that, press the "1", "2" or "3" buttons that corresponds to 
               the desired lottery panel (left, middle, or right).''',
'''After each token placement, the token will turn green if you won or 
           red if you lost. You earn 1 point for each green token.''',
'''Some lotteries are more rewarding than others. Each lottery will be 
                    replaced at the beginning of a new game.''',
'''Therefore, you need to get a sense of which lotteries are better for 
                                       each new game.''',
'''Try to earn as many points as possible! Remember that you will be 
            paid based on the total number of points you earn!''']
        self.switch_cost = 25 #pts lost for switching locations
        self.time_cost = 12.5 #pts lost per second
        self.reward = 50 #pts won or lost for picking correct/incorrect location
        self.current_loc = None #current location of dots shown
        self.target_direction = 0 #directions for target and distractor patches
        self.dot_speed = 0.01 #float(3)/5*7/60 #.005 #1.98 
        self.dot_life = 3
        self.ndots = 24 #6
        self.dot_field_size = 350 #7.6 #5 #189
        self.block_points = 0 #points earned this block
        self.total_points = 0 #total points earned so far
        self.minimum_time = 0.1 #must take longer than 0.1s to decide, or 4s delay and -50 pts
        self.direction_text = None #will be right or left
        self.coins_left = None #how many coins are left for this trial--also the next coin to hide when a selection is made
        self.coins = None #list of coins to draw (g.maximum_coinsx1)
        self.bold_boxes = None #the boxes that are drawn to show which lotto was selected
        self.sound_win = None #sound to play for win trials
        self.cound_loss = None #sound to play for loss trials 
        self.wins_by_column = [0,0,0] #how many wins for each column (3x1)
        self.losses_by_column = [0,0,0] #how many losses for each column (3x1)
        self.game_points = None #number of points won in this game
        self.win_coins = None #list of green coins to draw for wins (3x16)
        self.loss_coins = None #list of red coins to draw for losses (3x16)
        self.background = None #background image--shows columns but no coins or text
        self.coins_this_block = 16
        self.game_number = 1 #the current game
        self.block_trial = None #trial within this game
        self.trial_number = None #overall trial number
        self.maximum_coins = 16 #maximum number of coins for a single game
        self.number_of_blocks = None #number of games to play
        self.trials_this_block = None #used when printing "Trial Number: X/16"
        self.title = 'Slot Machine'

event_types = {'INSTRUCT_ONSET':1, 
    'TASK_ONSET':2, 
    'BLOCK_ONSET':3,
    'TRIAL_ONSET':4, 
    'SELECTION':5,
    'BLOCK_RESULT_ONSET':6,
    'BLOCK_RESULT_OFFSET':7,
    'FINAL_RESULT_ONSET':8,
    'FINAL_RESULT_OFFSET':9,
    'TASK_END':StimToolLib.TASK_END}


def process_trial_result(selection_idx, trial_win):
    #process result of one trial--handle drawing the new red/green token, play sound, and update trial wins 
    if trial_win:
        g.sound_win.play()
        g.win_coins[selection_idx][g.wins_by_column[selection_idx]].autoDraw = True
        g.wins_by_column[selection_idx] = g.wins_by_column[selection_idx] + 1
        g.block_points = g.block_points + 1
        g.total_points = g.total_points + 1
        g.text_game_points.setText('Game Points: ' + str(g.block_points))
    else:
        g.sound_loss.play()
        g.loss_coins[selection_idx][g.losses_by_column[selection_idx]].autoDraw = True
        g.losses_by_column[selection_idx] = g.losses_by_column[selection_idx] + 1
    g.text_trial_number.setText('Trial Number: ' + str(g.block_trial) + '/' + str(g.trials_this_block))
    g.win.flip()
    
    
def do_one_trial(probabilities):
    #wait for user selection
    g.win.flip()
    trial_onset = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], trial_onset, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    k = event.waitKeys(keyList = ['1', '2', '3', 'escape']) #event.waitKeys(keyList = [g.resk['left'], g.resk['right'], g.resk['down'], 'escape'])
    if k[0] == 'escape':
        raise StimToolLib.QuitException()
    g.text_game_number.setText('Game Number: ' + str(g.game_number) + '/' + str(g.number_of_blocks)) #this only changes the string the first trial in a block--adds the "/#" part of the stringnow = g.clock.getTime()
    selection_idx = int(k[0]) - 1 #minus 1 so it starts at 0--index into arrays easier
    trial_win = (random.random() < probabilities[selection_idx]) #does this selection lead to a win?
    now = g.clock.getTime()
    if trial_win: #convert True/False to 1/0 for writing out
        win_output = '1'
    else:
        win_output = '0'
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SELECTION'], now, now - trial_onset, selection_idx + 1, win_output, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #highlight selection 
    g.coins[g.coins_left - 1].autoDraw = False
    g.coins_left = g.coins_left - 1
    g.bold_boxes[selection_idx].autoDraw = True #used autodraw here because draw() would make the box the bottom layer
    g.yellow_box.autoDraw = False
    g.win.flip()
    g.bold_boxes[selection_idx].autoDraw = False
    g.yellow_box.autoDraw = True
    StimToolLib.just_wait(g.clock, g.clock.getTime() + 0.25)
    #play sound and update column images/score
    process_trial_result(selection_idx, trial_win)
    g.block_trial = g.block_trial + 1
    
def setup_stimuli():
    #load stimuli into appropriate locations for drawing later
    coin_size = 22
    first_coin_pos = [-250, 208]
    g.background = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/background.bmp'), units='pix')
    g.coins = []
    for i in range(g.maximum_coins):
        g.coins.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/Coin.png'), units='pix', size=[coin_size, coin_size], pos = [first_coin_pos[0] + i * coin_size, first_coin_pos[1]]))
    first_green_coin_pos = [-216, -186]
    coin_column_sep = 193
    g.win_coins = [[],[],[]]
    g.loss_coins = [[],[],[]]
    for i in range(g.maximum_coins):
        g.win_coins[0].append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/circle_green_small.bmp'), units='pix', size=[coin_size, coin_size], pos = [first_green_coin_pos[0], first_green_coin_pos[1] + i * coin_size]))
        g.loss_coins[0].append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/circle_red_small.bmp'), units='pix', size=[coin_size, coin_size], pos = [first_green_coin_pos[0] + 44, first_green_coin_pos[1] + i * coin_size]))
        g.win_coins[1].append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/circle_green_small.bmp'), units='pix', size=[coin_size, coin_size], pos = [first_green_coin_pos[0] + coin_column_sep, first_green_coin_pos[1] + i * coin_size]))
        g.loss_coins[1].append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/circle_red_small.bmp'), units='pix', size=[coin_size, coin_size], pos = [first_green_coin_pos[0] + 44 + coin_column_sep, first_green_coin_pos[1] + i * coin_size]))
        g.win_coins[2].append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/circle_green_small.bmp'), units='pix', size=[coin_size, coin_size], pos = [first_green_coin_pos[0] + coin_column_sep * 2, first_green_coin_pos[1] + i * coin_size]))
        g.loss_coins[2].append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/circle_red_small.bmp'), units='pix', size=[coin_size, coin_size], pos = [first_green_coin_pos[0] + 44 + coin_column_sep * 2, first_green_coin_pos[1] + i * coin_size]))
    g.text_game_number = visual.TextStim(g.win, text="Game Number: ", units='pix', height=25, color=[-1,-1,-1], pos=[first_coin_pos[0] - 25, first_coin_pos[1] + 75], bold=True, alignHoriz='left')
    g.text_trial_number = visual.TextStim(g.win, text="Trial Number: ", units='pix', height=25, color=[-1,-1,-1], pos=[first_coin_pos[0] - 25, first_coin_pos[1] + 35], bold=True, alignHoriz='left')
    g.text_game_points = visual.TextStim(g.win, text="Game Points: ", units='pix', height=25, color='green', pos=[first_coin_pos[0] + 250, first_coin_pos[1] + 75], bold=True, alignHoriz='left')
    g.bold_boxes = []
    g.bold_boxes.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/select_highlight.bmp'), units='pix', pos = [-193,-55], mask=os.path.join(os.path.dirname(__file__),'media/select_highlight_mask.bmp')))
    g.bold_boxes.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/select_highlight.bmp'), units='pix', pos = [0,-55], mask=os.path.join(os.path.dirname(__file__),'media/select_highlight_mask.bmp')))
    g.bold_boxes.append(visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/select_highlight.bmp'), units='pix', pos = [194,-55], mask=os.path.join(os.path.dirname(__file__),'media/select_highlight_mask.bmp')))
    g.yellow_box = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/yellow_box.bmp'), units='pix', pos = first_coin_pos, mask=os.path.join(os.path.dirname(__file__),'media/yellow_box_mask.bmp'))
    g.intro_image = visual.ImageStim(g.win, os.path.join(os.path.dirname(__file__),'media/intro_image.bmp'), units='pix', pos = [0,300], size=[480,480])
    g.block_end_text = []
    g.block_end_text.append(visual.TextStim(g.win, text="Game Points: ", units='pix', height=35, color='green', pos=[0, 290], bold=True, alignHoriz='center', wrapWidth=1600))
    g.block_end_text.append(visual.TextStim(g.win,text="Press ENTER to Start the Next Game",units='pix',pos=[0,-450],color=[1, 1, 1] ,height=20,wrapWidth=int(1600)))
    g.sound_win = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/correctsound.aiff'), volume=0.08)
    g.sound_loss = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/errorsound.aiff'), volume=0.08)

def clear_result_coins():
    for i in range(3):
        for j in range(g.maximum_coins):
            g.win_coins[i][j].autoDraw = False
            g.loss_coins[i][j].autoDraw = False 
        g.wins_by_column[i] = 0
        g.losses_by_column[i] = 0
def block_setup():
    #draw all coins, erase all win/loss coins, draw text for game/trial number, reset wins/losses per column
    g.yellow_box.autoDraw = False
    g.background.autoDraw = True
    clear_result_coins()
    for i in range(g.coins_this_block):    
        g.coins[i].autoDraw = True
    g.block_points = 0
    g.block_trial = 1
    g.coins_left = g.coins_this_block
    g.text_game_number.setText('Game Number: ' + str(g.game_number))
    g.text_game_number.autoDraw = True
    g.text_trial_number.setText('Trial Number: 1')
    g.text_trial_number.autoDraw = True
    g.text_game_points.setText('Game Points: 0')
    g.text_game_points.autoDraw = True
    g.yellow_box.autoDraw = True
    g.win.flip()    

    
def block_completion_screen():
    g.block_end_text[0].setText('Game Over, you Earned ' + str(g.block_points) + ' Points!')
    g.block_end_text[0].autoDraw = True
    g.block_end_text[1].autoDraw = True
    g.yellow_box.autoDraw = False
    g.text_game_number.setText('')
    g.text_trial_number.setText('')
    g.text_game_points.setText('')
    g.win.flip()
    k = event.waitKeys(keyList = ['return', 'escape'])
    if k[0] == 'escape':
        raise StimToolLib.QuitException()
    g.block_end_text[0].autoDraw = False
    g.block_end_text[1].autoDraw = False
def do_one_block(n_trials, probabilities):
    g.trials_this_block = n_trials #used for printing the "Trial Number: X/16"
    block_setup()
    g.trial_type = str(probabilities[0]) + '-' + str(probabilities[1]) + '-' + str(probabilities[2]) #every trial within a block has the same type
    block_onset = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BLOCK_ONSET'], block_onset, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    for i in range(n_trials):
        do_one_trial(probabilities)
        g.trial = g.trial + 1
    g.game_number = g.game_number + 1
    #show end of block text
    block_end = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BLOCK_RESULT_ONSET'], block_end, block_end - block_onset, 'NA', g.block_points, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    block_completion_screen()
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['BLOCK_RESULT_OFFSET'], now, now - block_end, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    
def show_instructions():
    
    instruct_onset = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_onset, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.show_title(g.win, g.title)
    g.intro_image.autoDraw = True
    StimToolLib.show_instructions(g.win, g.instructions)
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], now, now - instruct_onset, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.intro_image.autoDraw = False
def run(session_params, run_params):
    global g
    g = GlobalVars()

    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/B.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status
        
def run_try():  
#def run_try(SID, raID, scan, resk, run_num='1'):
    
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="B")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1#the user hit cancel so exit 
        if thisInfo[0] == 'Practice':
            g.run_params['run'] = 'P'
        else:
            g.run_params['run'] = thisInfo[0]
    
    #initialize the window, main text stim, and clock
    StimToolLib.general_setup(g)
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_B_Schedule' + str(g.run_params['run']) + '.csv')
    block_lengths,junk,probabilities,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)

    
    setup_stimuli()
    g.number_of_blocks = len(block_lengths)
    
    g.clock = core.Clock()
    start_time = data.getDateStr()
    #g.prefix = 'B-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time 
    fileName = os.path.join(g.prefix + '.csv')
    #fileName = os.path.join(os.path.dirname(__file__), 'data/' + g.prefix +  '.csv')
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  schedule_file + ',Event Codes:,' + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.BANDIT_CODE, g)
    
    instruct_onset_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_onset_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'B_instruct_schedule.csv'), g)
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], now, now - instruct_onset_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #return
    #show_instructions()
    g.win.flip()
    
    g.trial = 0 #initialize trial number
    indices = list(range(len(block_lengths)))
    random.shuffle(indices) #randomize order of blocks
    for i in indices: 
        do_one_block(int(block_lengths[i]), [probabilities[0][i], probabilities[1][i], probabilities[2][i]])
    if g.total_points >= 0.6 * g.trial:
        reward = '10'
        adj = 'fantastic'
    else:
        reward = '5'
        adj = 'great'
    
    final_result_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['FINAL_RESULT_ONSET'], final_result_time, 'NA', 'NA', reward, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.background.autoDraw = False
    clear_result_coins()
    StimToolLib.show_instructions(g.win, [
'''You are done with this task!
Thank you for participating
You did ''' + adj + '''! You earned $''' + reward + ''' in this task!'''])
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['FINAL_RESULT_OFFSET'], now, now - final_result_time, 'NA', g.total_points, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    
  
 


