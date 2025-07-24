
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui, sound
import numpy
import json
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
        self.not_done = True
        self.num_of_speed_tests = 10 #10
        self.taps_count = []
        self.taps_avg = 0 # now taps_max ...
        self.solo_stim_duration = 3.0
        self.rating_duration = 4.0
        self.actual_rating_duration = 0.0
        self.tap_soon_duration = 2.0
        self.actual_tap_soon_duration = 0.0
        self.tap_now_duration = 4.0
        self.actual_tap_now_duration = 0.0
        self.actual_post_rating_pause = 0.0
        self.shock_duration = 1.0
        self.anxious_color = 'red'
        self.risk_color = 'blue'
        self.debug_no_shock = False
        self.end_after_taps = False
        self.taps_minimum_max = 12
        self.shock_counter_l = 0
        self.shock_counter_m = 0
        self.shock_counter_h = 0
        self.loop_iteration_time = 0
        self.max_shield = 0.8
        self.lane_length = 2.0
        self.total_points = 0
        self.dac1 = 'DAC1'
        self.dac0 = 'DAC0'
        self.tap_routine_schedule = [[0.13,0,5],[0.13,0,5],[0.13,-1,5],[0.13,0,5],[0.13,1,5], #[5%=20%, 50%=50%, 95%=80%]
                                     [0.39,0,50],[0.39,0,50],[0.39,-1,50],[0.39,1,50],[0.39,0,50],
                                     [0.65,-1,95],[0.65,0,95],[0.65,0,95],[0.65,1,95],[0.65,0,95]] #[[% Max, Plus/Minus, 5=5%;50=50%;95=95%], ...]

event_types = {
    'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'PRACTICE_ONSET':3,
    'MAIN_ONSET':4, 
    'BLOCK_ONSET':5, 
    'TRIAL_ONSET':6, 
    'STIM_ONSET':7, 
    'RATING_ONSET':8, 
    'RATING_CHANGE':9, 
    'FINAL_RATING':10, 
    'PAUSE_ONSET':11,
    'SHOCK_ONSET':12, 
    'OUTLINE_ONSET':13,
    'TAP_SOON':14,
    'TAP_ONSET':15,
    'TAPS':16,
    'FIXATION_ONSET':17, 
    'ERROR_TAPS':18,
    'CHAR_POS':19,
    'SHIELD_SIZE':20,
    'SCORE_CHANGE':21,
    'TASK_END':StimToolLib.TASK_END 
    }

def do_slider_practice():
    g.slider_practice_shock1.draw()
    for part in g.risk_hscale_parts:
        part.draw()
    g.win.flip()
    done_with_loop = False
    event.clearEvents()
    while not done_with_loop:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        if event.getKeys([g.run_params['right']]):
            done_with_loop = True
        StimToolLib.short_wait()
    event.clearEvents()
    g.risk_hscale_selector.setPos([0.0, g.risk_hscale_selector.pos[1]])
    g.risk_hscale_selector.setFillColor(g.risk_color)
    g.blank.draw()
    g.slider_practice_shock2.draw()
    for part in g.risk_hscale_parts:
        part.draw()
    g.win.flip()
    selected = False
    while not selected:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        
        k = event.getKeys([g.run_params['left'], g.run_params['right'], g.run_params['select']])
        if k != None and k != []:
            if k[0] == g.run_params['left'] and g.risk_hscale_selector.pos[0] > g.risk_hscale_bottom_line.pos[0] and not selected: # move up, but not above top tick
                g.risk_hscale_selector.setPos([g.risk_hscale_selector.pos[0] - 0.2, g.risk_hscale_selector.pos[1]])
            if k[0] == g.run_params['right'] and g.risk_hscale_selector.pos[0] < g.risk_hscale_top_line.pos[0] and not selected: # move down, but not below bottom tick
                g.risk_hscale_selector.setPos([g.risk_hscale_selector.pos[0] + 0.2, g.risk_hscale_selector.pos[1]])
            if k[0] == g.run_params['select'] and not selected:
                selected = True
                g.risk_hscale_selector.setFillColor('yellow')
        # update scale
        g.blank.draw()
        g.slider_practice_shock2.draw()
        for part in g.risk_hscale_parts:
            part.draw()
        g.win.flip()
        StimToolLib.short_wait()

    g.slider_practice_anx1.draw()
    for part in g.anx_hscale_parts:
        part.draw()
    g.win.flip()
    done_with_loop = False
    event.clearEvents()
    while not done_with_loop:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        if event.getKeys([g.run_params['right']]):
            done_with_loop = True
        StimToolLib.short_wait()
    
    event.clearEvents()
    g.anx_hscale_selector.setPos([0.0, g.anx_hscale_selector.pos[1]])
    g.anx_hscale_selector.setFillColor(g.anxious_color)
    g.blank.draw()
    g.slider_practice_anx2.draw()
    for part in g.anx_hscale_parts:
        part.draw()
    g.win.flip()
    selected = False
    while not selected:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        
        k = event.getKeys([g.run_params['left'], g.run_params['right'], g.run_params['select']])
        if k != None and k != []:
            if k[0] == g.run_params['left'] and g.anx_hscale_selector.pos[0] > g.anx_hscale_bottom_line.pos[0] and not selected: # move up, but not above top tick
                g.anx_hscale_selector.setPos([g.anx_hscale_selector.pos[0] - 0.2, g.anx_hscale_selector.pos[1]])
            if k[0] == g.run_params['right'] and g.anx_hscale_selector.pos[0] < g.anx_hscale_top_line.pos[0] and not selected: # move down, but not below bottom tick
                g.anx_hscale_selector.setPos([g.anx_hscale_selector.pos[0] + 0.2, g.anx_hscale_selector.pos[1]])
            if k[0] == g.run_params['select'] and not selected:
                selected = True
                g.anx_hscale_selector.setFillColor('yellow')
        # update scale
        g.blank.draw()
        g.slider_practice_anx2.draw()
        for part in g.anx_hscale_parts:
            part.draw()
        g.win.flip()
        StimToolLib.short_wait()

    g.slider_practice_startA.draw()
    g.win.flip()
    done_with_loop = False
    event.clearEvents()
    while not done_with_loop:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        if event.getKeys([g.run_params['right']]):
            done_with_loop = True
        StimToolLib.short_wait()

def initiate_shock():
    if g.debug_no_shock:
        return

    """
    Shock Subject by writing to DAC1 Register on labjack
    """
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SHOCK_ONSET'], g.clock.getTime(), 'NA', '100ms', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # Write to Register pin name
    # Pulse Rise every 2ms, since DIGITMER has a limit duration of 2ms
    # So Rise up and Rise down 20 times to make it 100ms, since 1 full period is 5ms
    
    shock_onset_time = g.clock.getTime()
    if "run-1a" in g.run_params['run']: #physio room
        for stim in range(20):
            ljm.eWriteName(g.ljhandle, g.dac1, 5) # rise up 
            StimToolLib.just_wait(g.clock, g.clock.getTime() + .002)# Waite 2ms
            ljm.eWriteName(g.ljhandle, g.dac1, 1) # rise down
            StimToolLib.just_wait(g.clock, g.clock.getTime() + .003)# wait 3ms
    else: #scanner
        for stim in range(20):
            ljm.eWriteName(g.ljhandle, g.dac0, 5) # rise up 
            StimToolLib.just_wait(g.clock, g.clock.getTime() + .002)# Waite 2ms
            ljm.eWriteName(g.ljhandle, g.dac0, 1) # rise down
            StimToolLib.just_wait(g.clock, g.clock.getTime() + .003)# wait 3ms
    shock_end_time = g.clock.getTime()
    g.ideal_trial_start = g.ideal_trial_start + (shock_end_time - shock_onset_time)

def initiate_shock_for_feedback():
    if g.debug_no_shock:
        return
    """
    Shock Subject by writing to DAC1 Register on labjack
    """
    # Write to Register pin name
    # Pulse Rise every 2ms, since DIGITMER has a limit duration of 2ms
    # So Rise up and Rise down 20 times to make it 100ms, since 1 full period is 5ms
    
    shock_onset_time = g.clock.getTime()
    if "run-1a" in g.run_params['run']:
        for stim in range(20):
            ljm.eWriteName(g.ljhandle, g.dac1, 5) # rise up 
            StimToolLib.just_wait(g.clock, g.clock.getTime() + .002)# Waite 2ms
            ljm.eWriteName(g.ljhandle, g.dac1, 1) # rise down
            StimToolLib.just_wait(g.clock, g.clock.getTime() + .003)# wait 3ms
    else:
        for stim in range(20):
            ljm.eWriteName(g.ljhandle, 'DAC0', 5) # rise up 
            StimToolLib.just_wait(g.clock, g.clock.getTime() + .002)# Waite 2ms
            ljm.eWriteName(g.ljhandle, 'DAC0', 1) # rise down
            StimToolLib.just_wait(g.clock, g.clock.getTime() + .003)# wait 3ms

def show_fixation(trial, duration, just_iti):
    g.fixation.draw()
    g.win.flip()

    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FIXATION_ONSET'], now, 'NA', 'NA', just_iti, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    StimToolLib.just_wait(g.clock, g.ideal_trial_start + duration)

def do_countdown():
    g.blank.draw()
    g.count_3.draw()
    g.win.flip()
    wait_time = g.clock.getTime()
    StimToolLib.just_wait(g.clock, wait_time + 1.0)
    g.blank.draw()
    g.count_2.draw()
    g.win.flip()
    wait_time = g.clock.getTime()
    StimToolLib.just_wait(g.clock, wait_time + 1.0)
    g.blank.draw()
    g.count_1.draw()
    g.win.flip()
    wait_time = g.clock.getTime()
    StimToolLib.just_wait(g.clock, wait_time + 1.0)

def do_all_speed_tests():
    g.taps_count = []
    for x in range(g.num_of_speed_tests):
        do_countdown()
        do_one_speed_test()
    # g.taps_avg = round(g.taps_count / g.num_of_speed_tests)
    g.taps_avg = max(g.taps_count)
    if g.taps_avg < g.taps_minimum_max:
        g.not_enough_message.draw()
        g.win.flip()
        progress_key = []
        while len(progress_key) < 1:
            one_progress_key = event.getKeys(['return'])
            if one_progress_key:
                progress_key.append(one_progress_key[0])
            g.not_enough_message.draw()
            g.win.flip()
            StimToolLib.short_wait()
        g.taps_count = 0
        do_all_speed_tests()
    else:
        # success
        pass


def do_one_speed_test():
    event.clearEvents()
    speed_test_keys = []
    start_test = g.clock.getTime()
    while g.clock.getTime() - start_test <= g.tap_now_duration:
        one_speed_test_key = event.getKeys([g.run_params['tap']])
        if one_speed_test_key:
            speed_test_keys.append(one_speed_test_key[0])
        g.blank.draw()
        g.speed_test_tap.draw()
        g.purple_border.draw()
        g.purple_border2.draw()
        g.purple_border3.draw()
        g.win.flip()
        StimToolLib.short_wait()
    g.win.flip()
    g.blank.draw()
    g.times_up.draw()
    g.win.flip()
    wait_time = g.clock.getTime()
    StimToolLib.just_wait(g.clock, wait_time + 1.0)
    g.taps_count.append(len(speed_test_keys))

def do_tap_feedback():
    one_count = 0
    two_count = 0
    three_count = 0
    four_count = 0
    while one_count <= 3 or two_count <= 3 or three_count <= 3 or four_count <= 3:
        # doing countdown
        do_countdown()
        
        event.clearEvents()
        speed_test_keys = []
        start_test = g.clock.getTime()
        while g.clock.getTime() - start_test <= g.tap_now_duration:
            one_speed_test_key = event.getKeys([g.run_params['tap']])
            if one_speed_test_key:
                speed_test_keys.append(one_speed_test_key[0])
            g.blank.draw()
            g.feedback_tap.draw()
            g.yellow_border.draw()
            g.yellow_border2.draw()
            g.yellow_border3.draw()
            g.win.flip()
            StimToolLib.short_wait()
        g.win.flip()

        if len(speed_test_keys) >= (0.8 * g.taps_avg):
            g.feedback_message.setText("That would reduce your risk of shock by about 95%.")
            one_count += 1
        elif len(speed_test_keys) >= (0.6 * g.taps_avg):
            g.feedback_message.setText("That would reduce your risk of shock by about 75%.")
            two_count += 1
        elif len(speed_test_keys) >= (0.4 * g.taps_avg):
            g.feedback_message.setText("That would reduce your risk of shock by about half.")
            three_count += 1
        else:
            g.feedback_message.setText("That would reduce your risk of shock by less than half.")
            four_count += 1
        
        if one_count <= 3 or two_count <= 3 or three_count <= 3 or four_count <= 3:
            g.feedback_message.setText(g.feedback_message.text + ' Keep trying different amounts.')
        else:
            g.feedback_message.setText(g.feedback_message.text + ' Thank you!')
        g.blank.draw()
        g.feedback_message.draw()
        g.win.flip()
        wait_time = g.clock.getTime()
        StimToolLib.just_wait(g.clock, wait_time + 1.0)
    
def do_tap_feedback_bar():
    print("IN BAR ROUTINE")
    # setup bars
    bar_height = g.tap_bar_height / g.taps_avg
    print(bar_height)
    for x in range(g.taps_avg):
        print(bar_height*(x+1))
        print((-1*g.tap_bar_height/2) + (bar_height/2)*(x+1))
        g.bars_list.append(visual.Rect(g.win, pos=[-0.4,((-1*g.tap_bar_height/2) + (bar_height/2 + (x*bar_height))) + 0.12], size=[g.tap_bar.size[0],bar_height], lineColor='white', fillColor='white', depth=1, units='norm'))
        print(x)
        print(g.bars_list[x].pos)

    # run trials
    ix = 0
    failed_trials = 0
    failed_trials_cons = 0
    last_per = 0
    for trial_vars in g.tap_routine_schedule:
        if trial_vars[2] != last_per:
            if trial_vars[2] == 5:
                practice_keys = []
                while len(practice_keys) < 1:
                    one_practice_key = event.getKeys(['return', 'z'])
                    if one_practice_key:
                        practice_keys.append(one_practice_key[0])
                    g.blank.draw()
                    g.lil_prac.draw()
                    g.win.flip()
                    StimToolLib.short_wait()
                start_countdown = g.clock.getTime()
                while g.clock.getTime() - start_countdown <= 3:
                    pre_flip_time = g.clock.getTime()
                    g.blank.draw()
                    if g.clock.getTime() - start_countdown <= 1:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:03...')
                    elif g.clock.getTime() - start_countdown <= 2:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:02...')
                    elif g.clock.getTime() - start_countdown <= 2.9:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:01...')
                    else:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:00...')
                    g.tap_countdown.draw()
                    g.win.flip()
                    StimToolLib.short_wait()
            if trial_vars[2] == 50:
                practice_keys = []
                while len(practice_keys) < 1:
                    one_practice_key = event.getKeys(['return', 'z'])
                    if one_practice_key:
                        practice_keys.append(one_practice_key[0])
                    g.blank.draw()
                    g.som_prac.draw()
                    g.win.flip()
                    StimToolLib.short_wait()
                start_countdown = g.clock.getTime()
                while g.clock.getTime() - start_countdown <= 3:
                    pre_flip_time = g.clock.getTime()
                    g.blank.draw()
                    if g.clock.getTime() - start_countdown <= 1:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:03...')
                    elif g.clock.getTime() - start_countdown <= 2:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:02...')
                    elif g.clock.getTime() - start_countdown <= 2.9:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:01...')
                    else:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:00...')
                    g.tap_countdown.draw()
                    g.win.flip()
                    StimToolLib.short_wait()
            if trial_vars[2] == 95:
                practice_keys = []
                while len(practice_keys) < 1:
                    one_practice_key = event.getKeys(['return', 'z'])
                    if one_practice_key:
                        practice_keys.append(one_practice_key[0])
                    g.blank.draw()
                    g.lot_prac.draw()
                    g.win.flip()
                    StimToolLib.short_wait()
                start_countdown = g.clock.getTime()
                while g.clock.getTime() - start_countdown <= 3:
                    pre_flip_time = g.clock.getTime()
                    g.blank.draw()
                    if g.clock.getTime() - start_countdown <= 1:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:03...')
                    elif g.clock.getTime() - start_countdown <= 2:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:02...')
                    elif g.clock.getTime() - start_countdown <= 2.9:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:01...')
                    else:
                        g.tap_countdown.setText('Practice Round Begins in\n 0:00...')
                    g.tap_countdown.draw()
                    g.win.flip()
                    StimToolLib.short_wait()
        last_per = trial_vars[2]
        g.tap_stop.setText('Tap')
        g.tap_stop.setColor('Green')
        bars_to_use = g.bars_list[0:(round(g.taps_avg*trial_vars[0]) + trial_vars[1])]
        print(len(bars_to_use))
        tap_goal_num = len(bars_to_use)
        g.tap_bar.size = [g.tap_bar.size[0], bar_height * len(bars_to_use)] # sum of bars to use heights
        g.tap_bar.pos = [g.tap_bar.pos[0], ((-1*g.tap_bar_height/2) + g.tap_bar.size[1]/2) + 0.12] # adjust position so that bottom of full bar rests in same spot
        num_of_taps = 0
        event.clearEvents()
        bar_test_keys = []
        start_bar = g.clock.getTime()
        default_overkill_tuple = (255,150,150)
        g.char.setPos([-1, -0.8])
        g.shield.setPos(g.char.pos)
        g.shield.opacity = 0.0
        last_img_set = g.clock.getTime()
        iix = 0
        event.clearEvents()
        tapped = False
        star_count = -1
        star_count2 = -1
        consecutive_taps = 0
        first_tap_flag = False # for consecutive taps
        first_tap = g.clock.getTime()
        # g.tap_outcome.setText('You got 0 stars')
        while g.clock.getTime() - start_bar <= g.tap_now_duration:
            pre_flip_time = g.clock.getTime()
            g.blank.draw()
            g.tap_routine_prompt.draw()
            # g.tap_to_fill.draw()
            # g.tap_bar.draw()
            if g.clock.getTime() - start_bar <= 1:
                g.tap_countdown.setText('Time:\n 0:04')
            elif g.clock.getTime() - start_bar <= 2:
                g.tap_countdown.setText('Time:\n 0:03')
            elif g.clock.getTime() - start_bar <= 3:
                g.tap_countdown.setText('Time:\n 0:02')
            elif g.clock.getTime() - start_bar <= 3.9:
                g.tap_countdown.setText('Time:\n 0:01')
            else:
                g.tap_countdown.setText('Time:\n 0:00')
            g.tap_countdown.draw()
            one_speed_test_key = event.getKeys([g.run_params['tap']])
            if one_speed_test_key:
                tapped = True
                if not first_tap_flag:
                    first_tap_flag = True
                    first_tap = g.clock.getTime()
                consecutive_taps += 1
                if g.shield.opacity < g.max_shield:
                    g.shield.opacity = g.shield.opacity + (g.max_shield / g.taps_avg)
                bar_test_keys.append(one_speed_test_key[0])
            if g.clock.getTime() > last_img_set + 0.033: # iterate through the sprite states
                iix += 1
                if iix > 3:
                    iix = 0
                if not tapped:
                    g.char.setImage(g.char_img_list[iix])
                else:
                    g.char.setImage(os.path.dirname(__file__) + '/media/person_brace.png')
                last_img_set = g.clock.getTime()
            for star in g.starray2:
                if g.char.pos[0] < star.pos[0]:
                    star.draw()
                else:
                    if g.starray2.index(star) > star_count2:
                        star_count2 = g.starray2.index(star)
            for star in g.starray:
                if g.char.pos[0] < star.pos[0]:
                    star.draw()
                else:
                    if g.starray.index(star) > star_count:
                        star_count = g.starray.index(star)
                        # g.tap_outcome.setText('You got ' + str(star_count + 1) + ' stars')
                        # g.total_points += 100
                        # StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SCORE_CHANGE'], g.clock.getTime(), 'NA', '100', str(g.total_points), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.char.draw()
            g.shield.draw()
            if tapped:
                g.wall.setPos([g.char.pos[0] + 0.12, g.char.pos[1]])
                if g.clock.getTime() > first_tap + (consecutive_taps*(g.tap_now_duration / g.taps_avg)):
                    tapped = False
                    consecutive_taps = 0
                    first_tap_flag = False
            num_of_taps = len(bar_test_keys)
            g.tap_stop.setPos([g.char.pos[0], g.char.pos[1] + 0.23])
            g.tap_stop_box.setPos([g.char.pos[0], g.char.pos[1] + 0.23])
            if num_of_taps == 0:
                g.tap_stop.setText('Tap')
                g.tap_stop.setColor('Green')
                g.tap_stop.draw()
            elif num_of_taps < tap_goal_num - 1:
                g.tap_stop.setText('Tap More')
                g.tap_stop.setColor('Green')
                g.tap_stop.draw()
            elif num_of_taps == tap_goal_num -1:
                g.tap_stop.setText('Last Tap')
                g.tap_stop.setColor('Yellow')
                g.tap_stop.draw()
            elif num_of_taps == tap_goal_num or num_of_taps == tap_goal_num+1:
                g.tap_stop_box.draw()
                g.tap_stop.setText('Done!')
                g.tap_stop.setColor('Red')
                g.tap_stop.draw()
            elif num_of_taps > tap_goal_num+1:
                g.tap_stop.setText('TAPPED TOO MUCH')
                g.tap_stop.setColor('Orange')
                g.tap_stop.draw()
                
            g.win.flip()
            StimToolLib.short_wait()
            post_flip_time = g.clock.getTime()
            g.loop_iteration_time = post_flip_time - pre_flip_time
            if not tapped:
                g.char.setPos([g.char.pos[0] + ((g.lane_length / g.tap_now_duration) * (g.loop_iteration_time)), g.char.pos[1]])
            g.shield.setPos(g.char.pos)
        g.char.setPos([0.53, 0])
        g.char.setImage(g.char_img_list[2])
        g.shield.setPos(g.char.pos)
        
        g.blank.draw()
        if num_of_taps == round(g.taps_avg*trial_vars[0]) + trial_vars[1]:
            g.tap_outcome.draw()
        # g.tap_bar.draw()
        g.win.flip()
        StimToolLib.just_wait(g.clock, g.clock.getTime() + 1.0)

        if num_of_taps == round(g.taps_avg*trial_vars[0]) + trial_vars[1] or num_of_taps == round(g.taps_avg*trial_vars[0]) + trial_vars[1] + 1:
            failed_trials_cons = 0
            g.blank.draw()
            g.tap_outcome.draw()
            draw_char('1', star_count, star_count2, draw_stars=False)
            draw_mini_stars(star_count)
            # g.tap_bar.draw()
            g.tap_outcome_points.draw()
            g.points_arrow.draw()
            g.shield_arrow.draw()
            if trial_vars[2] == 5:
                # g.five_graph.draw()
                g.tap_outcome_shield.setText('Low protection from shock')
                g.tap_outcome_shield.draw()
                # g.shock_text_pair.draw()
                # g.shock_sound.play()
            elif trial_vars[2] == 50:
                # g.fifty_graph.draw()
                g.tap_outcome_shield.setText('Some protection from shock')
                g.tap_outcome_shield.draw()
            elif trial_vars[2] == 95:
                # g.ninetyfive_graph.draw()
                g.tap_outcome_shield.setText('High protection from shock')
                g.tap_outcome_shield.draw()
            # else:
            #     g.noshock_text.draw()
            g.win.flip()
            start_star_fade = g.clock.getTime()
            while g.clock.getTime() < start_star_fade + 3.0:
                for star in g.starray2:
                    if star.opacity > 0:
                        # star.opacity = star.opacity - 0.07
                        star.opacity = 0
                for star in g.starray:
                    if star.opacity > 0:
                        # star.opacity = star.opacity - 0.07
                        star.opacity = 0
                g.blank.draw()
                g.tap_outcome.draw()
                draw_char('1', star_count, star_count2, draw_stars=False)
                draw_mini_stars(star_count)
                g.tap_outcome_points.draw()
                g.points_arrow.draw()
                g.shield_arrow.draw()
                g.tap_outcome_shield.draw()
                g.win.flip()
                StimToolLib.just_wait(g.clock, g.clock.getTime() + 0.1)
            for star in g.starray2:
                star.opacity = 1
            for star in g.starray:
                star.opacity = 1
            # StimToolLib.just_wait(g.clock, g.clock.getTime() + 3.0)
        elif num_of_taps > round(g.taps_avg*trial_vars[0]) + trial_vars[1] + 1:
            failed_trials += 1
            failed_trials_cons += 1
            g.blank.draw()
            # g.tap_bar.draw()
            g.try_again_text.setText("Try Again.\nTap LESS this time.\nTap until instructed to not tap.")
            g.try_again_text.draw()
            g.win.flip()
            StimToolLib.just_wait(g.clock, g.clock.getTime() + 5.0)
            g.tap_routine_schedule.insert(ix, trial_vars) # insert the same trial as the next entry, so that the failed trial repeats
        else:
            failed_trials += 1
            failed_trials_cons += 1
            g.blank.draw()
            # g.tap_bar.draw()
            g.try_again_text.setText("Try Again.\nTap MORE this time.\nTap until instructed to not tap.")
            g.try_again_text.draw()
            g.win.flip()
            StimToolLib.just_wait(g.clock, g.clock.getTime() + 5.0)
            g.tap_routine_schedule.insert(ix, trial_vars) # insert the same trial as the next entry, so that the failed trial repeats
        if failed_trials == 6 or failed_trials_cons == 3:
            failed_trials = 0
            failed_trials_cons = 0
            event.clearEvents()
            while True:
                if event.getKeys(["escape"]):
                    raise StimToolLib.QuitException()
                if event.getKeys(['return','z']):
                    break
                g.blank.draw()
                g.try_again_text.setText("Please Wait.")
                g.try_again_text.draw()
                g.win.flip()
                StimToolLib.short_wait()


        bars_to_use[len(bars_to_use) - 1].fillColor='white'
        g.blank.draw()
        g.fixation.draw()
        g.win.flip()
        StimToolLib.just_wait(g.clock, g.clock.getTime() + 2.0)
        ix += 1
    pass

def do_tap_routine():
    # doing practice
    event.clearEvents()
    g.blank.draw()
    g.practice_tap.draw()
    g.purple_border.draw()
    g.purple_border2.draw()
    g.purple_border3.draw()
    g.win.flip()
    practice_keys = []
    while len(practice_keys) < 3:
        one_practice_key = event.getKeys([g.run_params['tap']])
        if one_practice_key:
            practice_keys.append(one_practice_key[0])
        g.blank.draw()
        g.practice_tap.draw()
        g.purple_border.draw()
        g.purple_border2.draw()
        g.purple_border3.draw()
        g.win.flip()
        StimToolLib.short_wait()
    g.win.flip()

    if g.run_params['task_name'] == 'DEMOTTS':
        g.num_of_speed_tests = 3
        g.tap_routine_schedule = [[0.13,0,5],[0.13,0,5],[0.39,0,50],[0.39,0,50],[0.65,-1,95],[0.65,0,95]]

    # doing speed test 
    do_all_speed_tests()
    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'tts_instruct_schedule_PT2.csv'), g)
    StimToolLib.wait_enter_start(g.win)
    # doing feedback
    do_tap_feedback_bar()

    practice_keys = []
    g.blank.draw()
    g.training_end.draw()
    g.win.flip()
    while len(practice_keys) < 1:
        one_practice_key = event.getKeys([g.run_params['right'],'return', 'z'])
        if one_practice_key:
            practice_keys.append(one_practice_key[0])
        g.blank.draw()
        g.training_end.draw()
        g.win.flip()
        StimToolLib.short_wait()

def get_horizontal_rating(flag, base_image):
    selected = False
    event.clearEvents()
    if flag == '2':
        # reset selector position
        g.anx_hscale_selector.setPos([0.0, g.anx_hscale_selector.pos[1]])
        rating_to_mark = 3
        g.anx_hscale_selector.setFillColor(g.anxious_color)

        g.blank.draw()
        base_image.draw()
        for part in g.anx_hscale_parts:
            part.draw()
        g.win.flip()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_ONSET'], g.clock.getTime(), 'NA', 'ANX', rating_to_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

        while g.clock.getTime() < g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration:
            if event.getKeys(["escape"]):
                raise StimToolLib.QuitException()
            
            k = event.getKeys([g.run_params['left'], g.run_params['right'], g.run_params['select']])
            if k != None and k != []:
                if k[0] == g.run_params['left'] and g.anx_hscale_selector.pos[0] > g.anx_hscale_bottom_line.pos[0] and not selected: # move up, but not above top tick
                    rating_to_mark -= 1
                    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], g.clock.getTime(), 'NA', 'left', rating_to_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                    g.anx_hscale_selector.setPos([g.anx_hscale_selector.pos[0] - 0.2, g.anx_hscale_selector.pos[1]])
                if k[0] == g.run_params['right'] and g.anx_hscale_selector.pos[0] < g.anx_hscale_top_line.pos[0] and not selected: # move down, but not below bottom tick
                    rating_to_mark += 1
                    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], g.clock.getTime(), 'NA', 'right', rating_to_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                    g.anx_hscale_selector.setPos([g.anx_hscale_selector.pos[0] + 0.2, g.anx_hscale_selector.pos[1]])
                if k[0] == g.run_params['select'] and not selected:
                    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_RATING'], g.clock.getTime(), 'NA', 'select', rating_to_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                    selected = True
                    g.anx_hscale_selector.setFillColor('yellow')
            # update scale
            g.blank.draw()
            base_image.draw()
            for part in g.anx_hscale_parts:
                part.draw()
            g.win.flip()
            StimToolLib.short_wait()
        if not selected:
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_RATING'], g.clock.getTime(), 'NA', 'NA', rating_to_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    elif flag == '1':
        # reset selector position
        g.risk_hscale_selector.setPos([0.0, g.risk_hscale_selector.pos[1]])
        rating_to_mark = 3
        g.risk_hscale_selector.setFillColor(g.risk_color)

        g.blank.draw()
        base_image.draw()
        for part in g.risk_hscale_parts:
            part.draw()
        g.win.flip()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_ONSET'], g.clock.getTime(), 'NA', 'RISK', rating_to_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

        while g.clock.getTime() < g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration:
            if event.getKeys(["escape"]):
                raise StimToolLib.QuitException()
            
            k = event.getKeys([g.run_params['left'], g.run_params['right'], g.run_params['select']])
            if k != None and k != []:
                if k[0] == g.run_params['left'] and g.risk_hscale_selector.pos[0] > g.risk_hscale_bottom_line.pos[0] and not selected: # move up, but not above top tick
                    rating_to_mark -= 1
                    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], g.clock.getTime(), 'NA', 'left', rating_to_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                    g.risk_hscale_selector.setPos([g.risk_hscale_selector.pos[0] - 0.2, g.risk_hscale_selector.pos[1]])
                if k[0] == g.run_params['right'] and g.risk_hscale_selector.pos[0] < g.risk_hscale_top_line.pos[0] and not selected: # move down, but not below bottom tick
                    rating_to_mark += 1
                    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['RATING_CHANGE'], g.clock.getTime(), 'NA', 'right', rating_to_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                    g.risk_hscale_selector.setPos([g.risk_hscale_selector.pos[0] + 0.2, g.risk_hscale_selector.pos[1]])
                if k[0] == g.run_params['select'] and not selected:
                    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_RATING'], g.clock.getTime(), 'NA', 'select', rating_to_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                    selected = True
                    g.risk_hscale_selector.setFillColor('yellow')
            # update scale
            g.blank.draw()
            base_image.draw()
            for part in g.risk_hscale_parts:
                part.draw()
            g.win.flip()
            StimToolLib.short_wait()
        if not selected:
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['FINAL_RATING'], g.clock.getTime(), 'NA', 'NA', rating_to_mark, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

def get_vertical_rating(flag, base_image): ### !!!! MARK EVENTS NOT IMPLEMENTED HERE !!!!
    selected = False
    event.clearEvents()
    if flag == '2':
        # reset selector position
        g.anx_scale_selector.setPos([g.anx_scale_selector.pos[0], 0.0])
        g.anx_scale_selector.setFillColor(g.anxious_color)

        g.blank.draw()
        base_image.draw()
        for part in g.anx_scale_parts:
            part.draw()
        g.win.flip()

        while g.clock.getTime() < g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration:
            if event.getKeys(["escape"]):
                raise StimToolLib.QuitException()
            
            k = event.getKeys([g.run_params['left'], g.run_params['right'], g.run_params['select']])
            if k != None and k != []:
                if k[0] == g.run_params['left'] and g.anx_scale_selector.pos[1] < g.anx_scale_top_line.pos[1] and not selected: # move up, but not above top tick
                    g.anx_scale_selector.setPos([g.anx_scale_selector.pos[0], g.anx_scale_selector.pos[1] + 0.2])
                if k[0] == g.run_params['right'] and g.anx_scale_selector.pos[1] > g.anx_scale_bottom_line.pos[1] and not selected: # move down, but not below bottom tick
                    g.anx_scale_selector.setPos([g.anx_scale_selector.pos[0], g.anx_scale_selector.pos[1] - 0.2])
                if k[0] == g.run_params['select'] and not selected:
                    selected = True
                    g.anx_scale_selector.setFillColor('yellow')
            # update scale
            g.blank.draw()
            base_image.draw()
            for part in g.anx_scale_parts:
                part.draw()
            g.win.flip()
            StimToolLib.short_wait()
    elif flag == '1':
        # reset selector position
        g.risk_scale_selector.setPos([g.risk_scale_selector.pos[0], 0.0])
        g.risk_scale_selector.setFillColor(g.risk_color)

        g.blank.draw()
        base_image.draw()
        for part in g.risk_scale_parts:
            part.draw()
        g.win.flip()

        while g.clock.getTime() < g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration:
            if event.getKeys(["escape"]):
                raise StimToolLib.QuitException()
            
            k = event.getKeys([g.run_params['left'], g.run_params['right'], g.run_params['select']])
            if k != None and k != []:
                if k[0] == g.run_params['left'] and g.risk_scale_selector.pos[1] < g.risk_scale_top_line.pos[1] and not selected: # move up, but not above top tick
                    g.risk_scale_selector.setPos([g.risk_scale_selector.pos[0], g.risk_scale_selector.pos[1] + 0.2])
                if k[0] == g.run_params['right'] and g.risk_scale_selector.pos[1] > g.risk_scale_bottom_line.pos[1] and not selected: # move down, but not below bottom tick
                    g.risk_scale_selector.setPos([g.risk_scale_selector.pos[0], g.risk_scale_selector.pos[1] - 0.2])
                if k[0] == g.run_params['select'] and not selected:
                    selected = True
                    g.risk_scale_selector.setFillColor('yellow')
            # update scale
            g.blank.draw()
            base_image.draw()
            for part in g.risk_scale_parts:
                part.draw()
            g.win.flip()
            StimToolLib.short_wait()

def draw_char(neut_flag, star_count, star_count2, draw_stars=True):
    if neut_flag != '0':
        if draw_stars:
            for x in range(star_count2 + 1, len(g.starray2)):
                if star_count2 != 26:
                    g.starray2[x].draw()
            for x in range(star_count + 1, len(g.starray)):
                if star_count != 8:
                    g.starray[x].draw()
        g.char.draw()
        g.shield.draw()

def do_nothing():
    pass

def shock_test():
    g.shock_yourself_text = visual.TextStim(g.win, text="Press Any Button to Deliver the Shock", units='pix', color='white', pos=[0,150], height=50)
    g.shock_yourself_text.draw()
    g.win.flip()
    while g.not_done:
        k = event.getKeys(keyList = [g.session_params['left'], g.session_params['right'], g.session_params['up'], g.session_params['down'], 'escape']) # BAIL OUT at esc press, SHOCK with anything else
        if k != None and k != []: 
            if (k[0] == g.session_params['left'] or k[0] == g.session_params['right'] or k[0] == g.session_params['up'] or k[0] == g.session_params['down']):
                # SHOCKED
                print("shocked")
                initiate_shock_for_feedback()
                g.not_done = False
            if 'escape' in k:
                g.not_done = False
        StimToolLib.short_wait()
        g.shock_yourself_text.draw()
        g.win.flip()

def capture_error_taps(time, stim_array_to_draw, draw_char_or_not_func):
    check_keys = []
    while g.clock.getTime() <= time:
        tap_check_key = event.getKeys([g.run_params['tap']])
        if tap_check_key:
            check_keys.append(tap_check_key[0])
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['ERROR_TAPS'], g.clock.getTime(), 'NA', 'NA', str(len(check_keys)), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        for stim in stim_array_to_draw:
            stim.draw()
        draw_char_or_not_func()
        g.win.flip()
        StimToolLib.short_wait()

def draw_border(color):
    if color == 'yellow':
        g.yellow_border.draw()
        g.yellow_border2.draw()
        g.yellow_border3.draw()
    elif color == 'red':
        g.red_border.draw()
        g.red_border2.draw()
        g.red_border3.draw()

def draw_mini_stars(star_count):
    for x in range(0,star_count+1):
        g.mini_starray[x].setPos([g.char.pos[0] + 0.08, 0.05 + x*0.031])
        g.mini_starray[x].draw()

def shock_handler(neut_keys, trial_type, shock_flag):
    shocked = False
    if len(neut_keys) >= round(0.53 * g.taps_avg) and trial_type != 'pavCS':
        if g.run_params['shock_schedule_h'][g.shock_counter_h] == 1:
            initiate_shock()
            shocked = True
            g.shock_counter_h += 1
    elif len(neut_keys) >= round(0.27 * g.taps_avg) and len(neut_keys) < round(0.53 * g.taps_avg) and trial_type != 'pavCS':
        if g.run_params['shock_schedule_m'][g.shock_counter_m] == 1:
            initiate_shock()
            shocked = True
            g.shock_counter_m += 1
    elif len(neut_keys) < round(0.27 * g.taps_avg) and len(neut_keys) >= 1:
        if shock_flag == '2':
            pass
        else:
            # g.shock_sound.play()
            if g.run_params['shock_schedule_l'][g.shock_counter_l] == 1:
                initiate_shock()
                shocked = True
                g.shock_counter_l += 1
    else:
        shocked = True
        initiate_shock()
    
    return shocked
    
    
def do_one_trial(trial_type, base_image, post_rating_pause, iti, stim_duration, flags):
    rating_flag = flags.split("_")[0]
    shock_flag = flags.split("_")[1]
    neut_flag = flags.split("_")[2]
    g.solo_stim_duration = stim_duration
    star_count = -1
    star_count2 = -1
    
    if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()

    g.blank.draw()
    base_image.draw()
    g.win.flip()
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TRIAL_ONSET'], g.clock.getTime(), 'NA', 'NA', flags, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['STIM_ONSET'], g.clock.getTime(), 'NA', 'NA', base_image.image, g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    event.clearEvents()
    capture_error_taps(g.ideal_trial_start + g.solo_stim_duration, [g.blank, base_image], lambda: do_nothing())
    StimToolLib.just_wait(g.clock, g.ideal_trial_start + g.solo_stim_duration)

    if rating_flag != '0':
        g.actual_rating_duration += g.rating_duration
        get_horizontal_rating(rating_flag, base_image)

    neut_keys = []
    if neut_flag != '0':
        # tap soon section
        g.blank.draw()
        base_image.draw()
        g.tap_soon_text.draw()
        g.win.flip()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TAP_SOON'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        event.clearEvents()
        capture_error_taps(g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.tap_soon_duration, [g.blank, base_image, g.tap_soon_text], lambda: do_nothing())
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.tap_soon_duration)
        g.actual_tap_soon_duration += g.tap_soon_duration
        # tap now section
        g.char.setPos([-1, -0.8])
        g.shield.setPos(g.char.pos)
        g.shield.opacity = 0.0
        last_img_set = g.clock.getTime()
        iix = 0
        event.clearEvents()
        tapped = False
        star_count = -1
        star_count2 = -1
        consecutive_taps = 0
        first_tap_flag = False # for consecutive taps
        first_tap = g.clock.getTime()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TAP_ONSET'], g.clock.getTime(), 'NA', g.taps_avg, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SHIELD_SIZE'], g.clock.getTime(), 'NA', 'NA', '0', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        while g.clock.getTime() <= g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.tap_now_duration:
            pre_flip_time = g.clock.getTime()
            one_neut_key = event.getKeys([g.run_params['tap']])
            if one_neut_key:
                tapped = True
                if not first_tap_flag:
                    first_tap_flag = True
                    first_tap = g.clock.getTime()
                consecutive_taps += 1
                if g.shield.opacity < g.max_shield:
                    g.shield.opacity = g.shield.opacity + (g.max_shield / g.taps_avg)
                neut_keys.append(one_neut_key[0])
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['TAPS'], g.clock.getTime(), 'NA', 'NA', str(len(neut_keys)), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SHIELD_SIZE'], g.clock.getTime(), 'NA', 'NA', str(int((g.shield.opacity/g.max_shield)*100)) + "%", g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.blank.draw()
            g.speed_test_tap.draw()
            base_image.draw()
            draw_border('yellow')
            g.tap_now_text.draw()
            if g.clock.getTime() > last_img_set + 0.033: # iterate through the sprite states
                iix += 1
                if iix > 3:
                    iix = 0
                if not tapped:
                    g.char.setImage(g.char_img_list[iix])
                else:
                    g.char.setImage(os.path.dirname(__file__) + '/media/person_brace.png')
                last_img_set = g.clock.getTime()
            for star in g.starray2:
                if g.char.pos[0] < star.pos[0]:
                    star.draw()
                else:
                    if g.starray2.index(star) > star_count2:
                        star_count2 = g.starray2.index(star)
            for star in g.starray:
                if g.char.pos[0] < star.pos[0]:
                    star.draw()
                else:
                    if g.starray.index(star) > star_count:
                        star_count = g.starray.index(star)
                        g.total_points += 100
                        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['SCORE_CHANGE'], g.clock.getTime(), 'NA', '100', str(g.total_points), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            g.char.draw()
            g.shield.draw()
            if tapped:
                g.wall.setPos([g.char.pos[0] + 0.12, g.char.pos[1]])
                if g.clock.getTime() > first_tap + (consecutive_taps*(g.tap_now_duration / g.taps_avg)):
                    tapped = False
                    consecutive_taps = 0
                    first_tap_flag = False
            g.win.flip()
            StimToolLib.short_wait() # short wait is 0.001
            post_flip_time = g.clock.getTime()
            g.loop_iteration_time = post_flip_time - pre_flip_time
            if not tapped:
                g.char.setPos([g.char.pos[0] + ((g.lane_length / g.tap_now_duration) * (g.loop_iteration_time)), g.char.pos[1]])
            g.shield.setPos(g.char.pos)
            StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['CHAR_POS'], g.clock.getTime(), 'NA', 'NA', str(g.char.pos[0]), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.char.setPos([0.6, 0])
        g.char.setImage(g.char_img_list[2])
        g.shield.setPos(g.char.pos)
        g.actual_tap_now_duration += g.tap_now_duration

    if trial_type != 'pavCS' and rating_flag != '0' and neut_flag != '0':
        g.actual_rating_duration += g.rating_duration
        get_horizontal_rating(rating_flag, base_image)
        g.actual_post_rating_pause += post_rating_pause
        g.blank.draw()
        base_image.draw()
        draw_char(neut_flag, star_count, star_count2, draw_stars=False)
        g.win.flip()
        event.clearEvents()
        capture_error_taps(g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration + post_rating_pause, [g.blank, base_image], lambda: draw_char(neut_flag, star_count, star_count2, draw_stars=False))
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration + post_rating_pause)
    elif trial_type == 'pavCS':
        g.actual_post_rating_pause += post_rating_pause
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['PAUSE_ONSET'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        event.clearEvents()
        capture_error_taps(g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration + post_rating_pause, [g.blank, base_image], lambda: draw_char(neut_flag, star_count, star_count2, draw_stars=False))
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration + post_rating_pause)
    
    if shock_flag != '0':
        g.blank.draw()
        base_image.draw()
        draw_border('red')
        draw_char(neut_flag, star_count, star_count2, draw_stars=False)
        g.win.flip()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['OUTLINE_ONSET'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        shocked = shock_handler(neut_keys, trial_type, shock_flag)
        
        last_img_set = g.clock.getTime()
        iix = 0
        while g.clock.getTime() < g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration + g.actual_post_rating_pause + g.shock_duration:
            g.blank.draw()
            base_image.draw()
            draw_border('red')
            for star in g.starray2:
                if star.opacity > 0:
                    # star.opacity = star.opacity - 0.04
                    star.opacity = 0
            for star in g.starray:
                if star.opacity > 0:
                    # star.opacity = star.opacity - 0.04
                    star.opacity = 0
            draw_char(neut_flag, star_count, star_count2, draw_stars=False)
            if g.clock.getTime() > last_img_set + 0.033: # iterate through the sprite states
                iix += 1
                if iix > 3:
                    iix = 0
                if shocked:
                    g.shield.opacity = 0.0
                    g.blast.setPos(g.char.pos)
                    g.blast.setImage(g.blast_img_list[iix])
                    g.lil_shock.setPos([g.char.pos[0] - 0.07, g.char.pos[1] + 0.07])
                last_img_set = g.clock.getTime()
            if shocked and (neut_flag != '0'):
                g.blast.draw()
                g.lil_shock.draw()
            draw_mini_stars(star_count)
            g.win.flip()
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration + g.actual_post_rating_pause + g.shock_duration)
    else:
        g.blank.draw()
        base_image.draw()
        draw_border('red')
        draw_char(neut_flag, star_count, star_count2, draw_stars=False)
        g.win.flip()
        StimToolLib.mark_event(g.output, g.trial, g.trial_type, event_types['OUTLINE_ONSET'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        last_img_set = g.clock.getTime()
        iix = 0
        while g.clock.getTime() < g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration + g.actual_post_rating_pause + g.shock_duration:
            g.blank.draw()
            base_image.draw()
            draw_border('red')
            for star in g.starray2:
                if star.opacity > 0:
                    # star.opacity = star.opacity - 0.04
                    star.opacity = 0
            for star in g.starray:
                if star.opacity > 0:
                    # star.opacity = star.opacity - 0.04
                    star.opacity = 0
            draw_char(neut_flag, star_count, star_count2, draw_stars=False)
            draw_mini_stars(star_count)
            g.win.flip()
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration + g.actual_post_rating_pause + g.shock_duration)

    for star in g.starray2:
        star.opacity = 1
    for star in g.starray:
        star.opacity = 1
    show_fixation(g.trial, g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration + g.actual_post_rating_pause + g.shock_duration + iti, iti)
    g.ideal_trial_start = g.ideal_trial_start + g.solo_stim_duration + g.actual_rating_duration + g.actual_tap_soon_duration + g.actual_tap_now_duration + g.actual_post_rating_pause + g.shock_duration + iti
    g.actual_rating_duration = 0
    g.actual_tap_soon_duration = 0
    g.actual_tap_now_duration = 0
    g.actual_post_rating_pause = 0

def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/TTS.Default.params', {})
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
        myDlg = gui.Dlg(title="TTS")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1 #the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]

    # Check if Labjack in plugged in
    # Open first found LabJack
    try:
        g.ljhandle = ljm.openS("ANY", "ANY", "ANY")
        # set DAC pins to 0
        ljm.eWriteName(g.ljhandle, 'DAC0', 1)
    except:
        myDlg = gui.Dlg(title="LabJack Error")
        myDlg.addText("It doesn't look like you have labjack plugged in?\nPlease plug in the labjack to run this task.")
        myDlg.show()  # show dialog and wait for OK or Cancel
        if not g.debug_no_shock:
            raise StimToolLib.QuitException()

    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)

    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    if 'full-behv' in schedule_file:
        g.dac1 = 'DAC0'
    StimToolLib.general_setup(g)
    g.win.color = [0,0,0]
    g.win.flip()
    g.win.flip()

    if "shock_test" in g.run_params['run']:
        start_time = data.getDateStr()
        fileName = os.path.join(g.prefix + '.csv')
        g.output = open(fileName, 'w')
        sorted_events = sorted(event_types.items(), key=lambda item: item[1])
        g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + '\n')
        g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
        StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)
        g.ideal_trial_start = g.clock.getTime()
        shock_test()
        return

    trial_types,images,durations,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    base_images = images[0]
    post_rating_durations = durations[1]
    iti_durations = durations[2]
    stim_durations = durations[0]
    flags = junk[0]

    #set up stimuli
    ## Blank
    g.blank = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/blank.jpg'), pos=[0,0], size = 2, units='norm')
    g.fixation = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/fixation_diamond.PNG'), pos=[0,0], size = 2, units='norm')
    ## Borders
    g.purple_border = visual.Rect(g.win, pos=[0,0], size=[2,2], lineColor='#7030a0', lineWidth=800, fillColor=None, depth=1, units='norm')
    g.yellow_border = visual.Rect(g.win, pos=[0,0], size=[2,2], lineColor='#ffff01', lineWidth=800, fillColor=None, depth=1, units='norm')
    g.red_border = visual.Rect(g.win, pos=[0,0], size=[2,2], lineColor='red', lineWidth=800, fillColor=None, depth=1, units='norm')
    g.purple_border2 = visual.Rect(g.win, pos=[0,0], size=[1.97,1.97], lineColor='#7030a0', lineWidth=800, fillColor=None, depth=1, units='norm')
    g.yellow_border2 = visual.Rect(g.win, pos=[0,0], size=[1.97,1.97], lineColor='#ffff01', lineWidth=800, fillColor=None, depth=1, units='norm')
    g.red_border2 = visual.Rect(g.win, pos=[0,0], size=[1.97,1.97], lineColor='red', lineWidth=800, fillColor=None, depth=1, units='norm')
    g.purple_border3 = visual.Rect(g.win, pos=[0,0], size=[1.985,1.985], lineColor='#7030a0', lineWidth=800, fillColor=None, depth=1, units='norm')
    g.yellow_border3 = visual.Rect(g.win, pos=[0,0], size=[1.985,1.985], lineColor='#ffff01', lineWidth=800, fillColor=None, depth=1, units='norm')
    g.red_border3 = visual.Rect(g.win, pos=[0,0], size=[1.985,1.985], lineColor='red', lineWidth=800, fillColor=None, depth=1, units='norm')
    ## Tap Routine
    g.not_enough_message = visual.TextStim(g.win, text='Your tap average is not high enough. Please let the task administrator know if you are not able to tap faster. Thank you.\n\nPress ENTER to Continue', height=0.1, pos=[0,0], units='norm')
    g.practice_tap = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide16.PNG'), pos=[0,0], units='norm')
    g.speed_test_tap = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide20.PNG'), pos=[0,0], units='norm')
    g.feedback_tap = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide36.PNG'), pos=[0,0], units='norm')
    g.times_up = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide21.PNG'), pos=[0,0], units='norm')
    g.count_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide17.PNG'), pos=[0,0], units='norm')
    g.count_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide18.PNG'), pos=[0,0], units='norm')
    g.count_1 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide19.PNG'), pos=[0,0], units='norm')
    g.lil_prac = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide35.PNG'), pos=[0,0], units='norm')
    g.som_prac = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide35b.PNG'), pos=[0,0], units='norm')
    g.lot_prac = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide35c.PNG'), pos=[0,0], units='norm')
    g.feedback_message = visual.TextStim(g.win, text='', height=0.1, pos=[0,0], units='norm', color='black')
    # g.pre_feedback_routine = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide22.PNG'), pos=[0,0], units='norm')
    ## Trial Tapping
    g.tap_soon_text = visual.TextStim(g.win, text='You will soon have the option to button-tap...', height=0.1, pos=[0,0.8], units='norm', color='black')
    g.tap_now_text = visual.TextStim(g.win, text='You may now tap the button!', height=0.1, pos=[0,0.8], units='norm', color='black')
    ## Virtual Shock
    g.v_shock = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/vshock.png'), pos=[0.7,0.7], size = [0.35,0.45], units='norm')
    ## Horizontal Anxiety Scale
    g.anx_hscale_text = visual.TextStim(g.win, text='Current Anxiety?', height=0.08, pos=[0.0,-0.72], color='black', units='norm')
    g.anx_hscale_line = visual.Rect(g.win, pos=[0,-0.8], size=[0.8,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_hscale_top_line = visual.Rect(g.win, pos=[0.4,-0.8], size=[0.005,0.05], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_hscale_top_text = visual.TextStim(g.win, text='None', height=0.072, pos=[-0.4,-0.86], color='black', units='norm')
    g.anx_hscale_top_midline = visual.Rect(g.win, pos=[0.2,-0.8], size=[0.005,0.05], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_hscale_top_midtext = visual.TextStim(g.win, text='', height=0.072, pos=[-0.2,-0.86], color='black', units='norm')
    g.anx_hscale_midline = visual.Rect(g.win, pos=[0,-0.8], size=[0.005,0.05], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_hscale_midtext = visual.TextStim(g.win, text='Some', height=0.072, pos=[0.0,-0.86], color='black', units='norm')
    g.anx_hscale_bottom_midline = visual.Rect(g.win, pos=[-0.2,-0.8], size=[0.005,0.05], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_hscale_bottom_midtext = visual.TextStim(g.win, text='', height=0.072, pos=[0.2,-0.86], color='black', units='norm')
    g.anx_hscale_bottom_line = visual.Rect(g.win, pos=[-0.4,-0.8], size=[0.005,0.05], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_hscale_bottom_text = visual.TextStim(g.win, text='A Lot', height=0.072, pos=[0.4,-0.86], color='black', units='norm')
    if "run-1a" in g.run_params['run'] or "run-pa" in g.run_params['run']:
        g.anx_hscale_selector = visual.Circle(g.win, pos=[0,-0.8], radius=0.02, size=[1,1.6], lineColor=g.anxious_color, fillColor=g.anxious_color, depth=1, units='norm')
    else:
        g.anx_hscale_selector = visual.Circle(g.win, pos=[0,-0.8], radius=0.02, size=[1,1.2], lineColor=g.anxious_color, fillColor=g.anxious_color, depth=1, units='norm')
    g.anx_hscale_parts = [g.anx_hscale_line, g.anx_hscale_top_line, g.anx_hscale_top_midline, g.anx_hscale_midline, g.anx_hscale_bottom_midline, g.anx_hscale_bottom_line,
                          g.anx_hscale_text, g.anx_hscale_top_text, g.anx_hscale_top_midtext, g.anx_hscale_midtext, g.anx_hscale_bottom_midtext, g.anx_hscale_bottom_text, g.anx_hscale_selector]
    ## Horizontal Risk Scale
    g.risk_hscale_text = visual.TextStim(g.win, text='Risk of Shock?', height=0.08, pos=[0,0.885], color='black', units='norm')
    g.risk_hscale_line = visual.Rect(g.win, pos=[0,0.8], size=[0.8,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_hscale_top_line = visual.Rect(g.win, pos=[0.4,0.8], size=[0.005,0.05], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_hscale_top_text = visual.TextStim(g.win, text='None', height=0.072, pos=[-0.4,0.725], color='black', units='norm')
    g.risk_hscale_top_midline = visual.Rect(g.win, pos=[0.2,0.8], size=[0.005,0.05], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_hscale_top_midtext = visual.TextStim(g.win, text='', height=0.072, pos=[-0.2,0.725], color='black', units='norm')
    g.risk_hscale_midline = visual.Rect(g.win, pos=[0,0.8], size=[0.005,0.05], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_hscale_midtext = visual.TextStim(g.win, text='Some', height=0.072, pos=[0.0,0.725], color='black', units='norm')
    g.risk_hscale_bottom_midline = visual.Rect(g.win, pos=[-0.2,0.8], size=[0.005,0.05], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_hscale_bottom_midtext = visual.TextStim(g.win, text='', height=0.072, pos=[0.2,0.725], color='black', units='norm')
    g.risk_hscale_bottom_line = visual.Rect(g.win, pos=[-0.4,0.8], size=[0.005,0.05], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_hscale_bottom_text = visual.TextStim(g.win, text='A Lot', height=0.072, pos=[0.4,0.725], color='black', units='norm')
    # g.risk_hscale_selector = visual.Circle(g.win, pos=[0,0.8], radius=0.02, size=[1,1.2], lineColor=g.risk_color, fillColor=g.risk_color, depth=1, units='norm')
    if "run-1a" in g.run_params['run'] or "run-pa" in g.run_params['run']:
        g.risk_hscale_selector = visual.Circle(g.win, pos=[0,0.8], radius=0.02, size=[1,1.6], lineColor=g.risk_color, fillColor=g.risk_color, depth=1, units='norm')
    else:
        g.risk_hscale_selector = visual.Circle(g.win, pos=[0,0.8], radius=0.02, size=[1,1.2], lineColor=g.risk_color, fillColor=g.risk_color, depth=1, units='norm')
    g.risk_hscale_parts = [g.risk_hscale_line, g.risk_hscale_top_line, g.risk_hscale_top_midline, g.risk_hscale_midline, g.risk_hscale_bottom_midline, g.risk_hscale_bottom_line,
                           g.risk_hscale_text, g.risk_hscale_top_text, g.risk_hscale_top_midtext, g.risk_hscale_midtext, g.risk_hscale_bottom_midtext, g.risk_hscale_bottom_text, g.risk_hscale_selector]
    ## Vertical Anxiety Scale
    g.anx_scale_text = visual.TextStim(g.win, text='Current Anxiety?', height=0.05, pos=[-0.77,0.48], color='black', units='norm')
    g.anx_scale_line = visual.Rect(g.win, pos=[-0.8,0], size=[0.005,0.8], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_scale_top_line = visual.Rect(g.win, pos=[-0.8,0.4], size=[0.05,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_scale_top_text = visual.TextStim(g.win, text='Extreme', height=0.042, pos=[-0.72,0.4], color='black', units='norm', alignHoriz='left')
    g.anx_scale_top_midline = visual.Rect(g.win, pos=[-0.8,0.2], size=[0.05,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_scale_top_midtext = visual.TextStim(g.win, text='A lot', height=0.042, pos=[-0.72,0.2], color='black', units='norm', alignHoriz='left')
    g.anx_scale_midline = visual.Rect(g.win, pos=[-0.8,0], size=[0.05,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_scale_midtext = visual.TextStim(g.win, text='Moderate', height=0.042, pos=[-0.72,0.0], color='black', units='norm', alignHoriz='left')
    g.anx_scale_bottom_midline = visual.Rect(g.win, pos=[-0.8,-0.2], size=[0.05,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_scale_bottom_midtext = visual.TextStim(g.win, text='A little', height=0.042, pos=[-0.72,-0.2], color='black', units='norm', alignHoriz='left')
    g.anx_scale_bottom_line = visual.Rect(g.win, pos=[-0.8,-0.4], size=[0.05,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.anx_scale_bottom_text = visual.TextStim(g.win, text='None', height=0.042, pos=[-0.72,-0.4], color='black', units='norm', alignHoriz='left')
    g.anx_scale_selector = visual.Circle(g.win, pos=[-0.8,0], radius=0.02, size=[1,1.2], lineColor=g.anxious_color, fillColor=g.anxious_color, depth=1, units='norm')
    g.anx_scale_parts = [g.anx_scale_line, g.anx_scale_top_line, g.anx_scale_top_midline, g.anx_scale_midline, g.anx_scale_bottom_midline, g.anx_scale_bottom_line,
                          g.anx_scale_text, g.anx_scale_top_text, g.anx_scale_top_midtext, g.anx_scale_midtext, g.anx_scale_bottom_midtext, g.anx_scale_bottom_text, g.anx_scale_selector]
    ## Vertical Risk Scale
    g.risk_scale_text = visual.TextStim(g.win, text='Will a shock occur?', height=0.05, pos=[0.77,0.51], color='black', units='norm')
    g.risk_scale_line = visual.Rect(g.win, pos=[0.8,0], size=[0.005,0.8], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_scale_top_line = visual.Rect(g.win, pos=[0.8,0.4], size=[0.05,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_scale_top_text = visual.TextStim(g.win, text='Definitely', height=0.042, pos=[0.73,0.4], color='black', units='norm', alignHoriz='right')
    g.risk_scale_top_midline = visual.Rect(g.win, pos=[0.8,0.2], size=[0.05,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_scale_top_midtext = visual.TextStim(g.win, text='Probably', height=0.042, pos=[0.73,0.2], color='black', units='norm', alignHoriz='right')
    g.risk_scale_midline = visual.Rect(g.win, pos=[0.8,0], size=[0.05,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_scale_midtext = visual.TextStim(g.win, text='Maybe', height=0.042, pos=[0.73,0.0], color='black', units='norm', alignHoriz='right')
    g.risk_scale_bottom_midline = visual.Rect(g.win, pos=[0.8,-0.2], size=[0.05,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_scale_bottom_midtext = visual.TextStim(g.win, text='Probably Not', height=0.042, pos=[0.73,-0.2], color='black', units='norm', alignHoriz='right')
    g.risk_scale_bottom_line = visual.Rect(g.win, pos=[0.8,-0.4], size=[0.05,0.005], lineColor='black', fillColor='black', depth=1, units='norm')
    g.risk_scale_bottom_text = visual.TextStim(g.win, text='Definitely Not', height=0.042, pos=[0.73,-0.4], color='black', units='norm', alignHoriz='right')
    g.risk_scale_selector = visual.Circle(g.win, pos=[0.8,0], radius=0.02, size=[1,1.2], lineColor=g.risk_color, fillColor=g.risk_color, depth=1, units='norm')
    g.risk_scale_parts = [g.risk_scale_line, g.risk_scale_top_line, g.risk_scale_top_midline, g.risk_scale_midline, g.risk_scale_bottom_midline, g.risk_scale_bottom_line,
                          g.risk_scale_text, g.risk_scale_top_text, g.risk_scale_top_midtext, g.risk_scale_midtext, g.risk_scale_bottom_midtext, g.risk_scale_bottom_text, g.risk_scale_selector]
    ## slider practice
    g.slider_practice_shock1 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide7.PNG'), pos=[0,0], units='norm')
    g.slider_practice_shock2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide8.PNG'), pos=[0,0], units='norm')
    g.slider_practice_anx1 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide9.PNG'), pos=[0,0], units='norm')
    g.slider_practice_anx2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide10.PNG'), pos=[0,0], units='norm')
    g.slider_practice_questions = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide11.PNG'), pos=[0,0], units='norm')
    g.slider_practice_startA = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide66.PNG'), pos=[0,0], units='norm')

    ## tap bar feedback routine
    g.tap_bar_height = 1.6
    g.bars_list = []
    g.tap_bar = visual.Rect(g.win, pos=[-0.4,0], size=[0.4,1.6], lineColor='white', fillColor='black', depth=1, units='norm')
    g.try_again_text = visual.TextStim(g.win, text='Try Again.\nTap until instructed to not tap.', height=0.1, pos=[0,0], units='norm', color='black')
    g.tap_countdown = visual.TextStim(g.win, text='Time:\n 0:03', height=0.12, pos=[0,0], units='norm', color='black')
    g.tap_to_fill = visual.TextStim(g.win, text='Tap to fill the bar!', height=0.1, pos=[-0.4,0.8], units='norm', color='black')
    g.tap_outcome = visual.TextStim(g.win, text='Outcome:', height=0.1, pos=[0.4,0.7], units='norm', color='black')
    g.tap_outcome_shield = visual.TextStim(g.win, text='Shield Level: LOW', height=0.1, pos=[0.15,0.44], units='norm', color='black')
    g.tap_outcome_points = visual.TextStim(g.win, text='Points', height=0.1, pos=[0.84,0.44], units='norm', color='black')
    g.shock_text_pair = visual.TextStim(g.win, text='Shock', height=0.1, pos=[0.4,-0.5], units='norm', color='black')
    g.noshock_text = visual.TextStim(g.win, text='No Shock', height=0.1, pos=[0.4,0], units='norm', color='black')
    g.v_shock_big = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/vshock.png'), pos=[0.4,0.0], size = [0.55,0.65], units='norm')
    g.five_graph = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/vshock_5.png'), pos=[0.4,0.0], size = [0.87,0.9], units='norm')
    g.fifty_graph = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/vshock_50.png'), pos=[0.4,0.0], size = [0.87,0.9], units='norm')
    g.ninetyfive_graph = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/vshock_95.png'), pos=[0.4,0.0], size = [0.87,0.9], units='norm')
    g.training_end = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/instructions/Slide37.PNG'), pos=[0,0], units='norm')
    g.shock_sound = sound.Sound(value = os.path.join(os.path.dirname(__file__),  'media/shock.aiff'), volume=1)
    g.tap_stop = visual.TextStim(g.win, text='Tap', height=0.1, pos=[0,0], units='norm', color='green')
    g.points_arrow = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/points_arrow2.png'), size = [0.28, 0.245], pos=[0.75,0.22], units='norm')
    g.shield_arrow = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),  'media/shield_arrow.png'), size = [0.35, 0.28], pos=[0.31,0.22], units='norm')
    g.tap_routine_prompt = visual.TextStim(g.win, text='Tap until you see \"Don\'t Tap.\"', height=0.1, pos=[0,0.75], units='norm', color='black')
    g.tap_stop_box = visual.Rect(g.win, pos=[0,0], size=[0.32,0.12], lineColor='white', fillColor=None, depth=1, units='norm')

    # points animation
    g.score = visual.TextStim(g.win, text='SCORE: 0', height=0.2, pos=[0,0], units='norm', color='black')
    g.score_star = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.51,-0.335], size = [0.14,0.14], units='norm')
    g.points = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/100points.png'), pos=[-0.8,-0.8], size = [0.06,0.04], units='norm')
    g.star1 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.8,-0.8], size = [0.1,0.1], units='norm')
    g.star2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.6,-0.8], size = [0.1,0.1], units='norm')
    g.star3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.4,-0.8], size = [0.1,0.1], units='norm')
    g.star4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.2,-0.8], size = [0.1,0.1], units='norm')
    g.star5 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.0,-0.8], size = [0.1,0.1], units='norm')
    g.star6 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.2,-0.8], size = [0.1,0.1], units='norm')
    g.star7 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.4,-0.8], size = [0.1,0.1], units='norm')
    g.star8 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.6,-0.8], size = [0.1,0.1], units='norm')
    g.star9 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.8,-0.8], size = [0.1,0.1], units='norm')
    g.starray = [g.star1, g.star2, g.star3, g.star4, g.star5, g.star6, g.star7, g.star8, g.star9]
    g.star1_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.83,-0.81], size = [0.1,0.1], units='norm')
    g.star2_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.56,-0.79], size = [0.1,0.1], units='norm')
    g.star3_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.45,-0.78], size = [0.1,0.1], units='norm')
    g.star4_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.23,-0.82], size = [0.1,0.1], units='norm')
    g.star5_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.05,-0.81], size = [0.1,0.1], units='norm')
    g.star6_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.27,-0.79], size = [0.1,0.1], units='norm')
    g.star7_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.38,-0.82], size = [0.1,0.1], units='norm')
    g.star8_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.56,-0.78], size = [0.1,0.1], units='norm')
    g.star9_2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.75,-0.81], size = [0.1,0.1], units='norm')
    g.star1_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.76,-0.78], size = [0.1,0.1], units='norm')
    g.star2_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.63,-0.82], size = [0.1,0.1], units='norm')
    g.star3_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.34,-0.8], size = [0.1,0.1], units='norm')
    g.star4_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.13,-0.79], size = [0.1,0.1], units='norm')
    g.star5_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.05,-0.78], size = [0.1,0.1], units='norm')
    g.star6_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.14,-0.81], size = [0.1,0.1], units='norm')
    g.star7_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.48,-0.8], size = [0.1,0.1], units='norm')
    g.star8_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.62,-0.79], size = [0.1,0.1], units='norm')
    g.star9_3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.73,-0.78], size = [0.1,0.1], units='norm')
    g.star1_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.7,-0.78], size = [0.1,0.1], units='norm')
    g.star2_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.65,-0.82], size = [0.1,0.1], units='norm')
    g.star3_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.34,-0.78], size = [0.1,0.1], units='norm')
    g.star4_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.13,-0.82], size = [0.1,0.1], units='norm')
    g.star5_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.05,-0.81], size = [0.1,0.1], units='norm')
    g.star6_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.14,-0.8], size = [0.1,0.1], units='norm')
    g.star7_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.48,-0.78], size = [0.1,0.1], units='norm')
    g.star8_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.62,-0.81], size = [0.1,0.1], units='norm')
    g.star9_4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.73,-0.8], size = [0.1,0.1], units='norm')
    g.starray2 = [g.star1_2, g.star2_2, g.star3_2, g.star4_2, g.star5_2, g.star6_2, g.star7_2, g.star8_2, g.star9_2,
                  g.star1_3, g.star2_3, g.star3_3, g.star4_3, g.star5_3, g.star6_3, g.star7_3, g.star8_3, g.star9_3,
                  g.star1_4, g.star2_4, g.star3_4, g.star4_4, g.star5_4, g.star6_4, g.star7_4, g.star8_4, g.star9_4]
    g.mini_star1 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.8,-0.8], size = [0.03,0.03], units='norm')
    g.mini_star2 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.6,-0.8], size = [0.03,0.03], units='norm')
    g.mini_star3 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.4,-0.8], size = [0.03,0.03], units='norm')
    g.mini_star4 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[-0.2,-0.8], size = [0.03,0.03], units='norm')
    g.mini_star5 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.0,-0.8], size = [0.03,0.03], units='norm')
    g.mini_star6 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.2,-0.8], size = [0.03,0.03], units='norm')
    g.mini_star7 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.4,-0.8], size = [0.03,0.03], units='norm')
    g.mini_star8 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.6,-0.8], size = [0.03,0.03], units='norm')
    g.mini_star9 = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/star.png'), pos=[0.8,-0.8], size = [0.03,0.03], units='norm')
    g.mini_starray = [g.mini_star1, g.mini_star2, g.mini_star3, g.mini_star4, g.mini_star5, g.mini_star6, g.mini_star7, g.mini_star8, g.mini_star9]
    g.wall = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/wall.png'), pos=[-1,-0.8], size = [0.2,0.2], units='norm')
    g.lil_shock = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/vshock.png'), pos=[-1,-0.8], size = [0.1,0.1], units='norm')
    g.shield = visual.Rect(g.win, size = [0.22,0.22], fillColor = 'blue', opacity = 0.0, units = 'norm')
    g.char = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/run_purple_person2.png'), pos=[-1,-0.8], size = [0.2,0.2], units='norm')
    g.char_img_list = [os.path.dirname(__file__) + '/media/run_purple_person1.png',
                       os.path.dirname(__file__) + '/media/run_purple_person2.png',
                       os.path.dirname(__file__) + '/media/run_purple_person3.png',
                       os.path.dirname(__file__) + '/media/run_purple_person4.png']
    g.blast = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/blast1.png'), pos=[-1,-0.8], size = [0.2,0.2], units='norm')
    g.blast_img_list = [os.path.dirname(__file__) + '/media/blast1.png',
                       os.path.dirname(__file__) + '/media/blast2.png',
                       os.path.dirname(__file__) + '/media/blast3.png',
                       os.path.dirname(__file__) + '/media/blast2.png']
    g.dance = visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'media/dance_person1.png'), pos=[-1,-0.8], size = [0.2,0.2], units='norm')
    g.dance_img_list = [os.path.dirname(__file__) + '/media/dance_person1.png',
                       os.path.dirname(__file__) + '/media/dance_person2.png',
                       os.path.dirname(__file__) + '/media/dance_person1.png',
                       os.path.dirname(__file__) + '/media/dance_person3.png']

    g.debug = visual.TextStim(g.win, text='', height=0.1, pos=[-0.7,0.7], units='norm')
    g.debug_avg = visual.TextStim(g.win, text='', height=0.1, pos=[-0.7,0.6], units='norm')
    
    start_time = data.getDateStr()
    fileName = os.path.join(g.prefix + '.csv')
    
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.FLIGHT_INIT_DIST_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)

    tap_avg_json = os.path.join(g.session_params['output_dir'], g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['task_name'] + "_tap_avg.json")
    if "run-tp" in g.run_params['run']:
        # Do some practice and get average tap capability
        do_tap_routine()
        #save that number for other runs
        if not os.path.exists(tap_avg_json): # write new file if none exists
            with open(tap_avg_json, 'w') as f:
                f.write("{ \"tap_avg\": " + str(g.taps_avg) + " }")
                pass
        else: # if one does exist, then go through routine to rename old one and make new one (persist all old tap average files)
            file_count_idx = 0
            file_routine_done = False
            while not file_routine_done:
                old_fname = tap_avg_json
                tap_avg_json_rename = os.path.join(g.session_params['output_dir'], g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + g.run_params['task_name'] + "_tap_avg_" + str(file_count_idx) + ".json") # new name with incrementing index
                if not os.path.exists(tap_avg_json_rename):
                    os.rename(old_fname, tap_avg_json_rename) # if it doesn't exist, then rename it
                    file_routine_done = True
                else: # if it does exist, then check next index
                    file_count_idx += 1
            if not os.path.exists(tap_avg_json): # we succesfully renamed the old tap file, so now we want to write the new one
                with open(tap_avg_json, 'w') as f:
                    f.write("{ \"tap_avg\": " + str(g.taps_avg) + " }")
                    pass
        g.end_after_taps = True
    elif "run-1a" not in g.run_params['run'] and "run-tp" not in g.run_params['run'] and "run-pa" not in g.run_params['run']:
        with open(tap_avg_json, 'r+') as file:
                json_data = json.load(file)
                g.taps_avg = json_data["tap_avg"]
    elif "run-pa" in g.run_params['run']:
        do_slider_practice()
        pass

    if not g.end_after_taps:
        g.trial = 0
        if g.session_params['scan'] == 'True' and "pa" not in g.run_params['run'] and "pb" not in g.run_params['run']:
            StimToolLib.wait_scan_start(g.win)
        elif "pb" in g.run_params['run']:
            StimToolLib.wait_enter_start(g.win)
        else:
            StimToolLib.wait_start(g.win)
        instruct_end_time = g.clock.getTime()
        StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        g.ideal_trial_start = instruct_end_time

    if not g.end_after_taps:
        for t,b_i,p_r_d,i_d,s_d,f in zip(trial_types, base_images, post_rating_durations, iti_durations, stim_durations, flags):
            g.trial_type = t

            do_one_trial(t, b_i, p_r_d, i_d, s_d, f)

            g.trial = g.trial + 1

    if g.run_params['show_score']:
        g.blank.draw()
        g.score.setText("You have completed this run, your score is: " + str(g.total_points))
        g.score.draw()
        g.score_star.draw()
        g.win.flip()
        StimToolLib.just_wait(g.clock, g.ideal_trial_start + 10)

    g.msg.setColor([-1,-1,-1])

  
 


