
import StimToolLib, os, random, operator, sys
from psychopy import visual, core, event, data, gui, sound, prefs
from labjack import ljm
import time


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
        self.volume = None # Default Volume, needs to be set by Volume Workup
        self.anxiety_rating = 0 # Anxiety Rating, can be changed anytime throughout task
        

event_types = {
    'INSTRUCT_ONSET':1,
    'TASK_ONSET':2,
    'TRIAL_ONSET': 3,
    'FIXATION_ONSET':4,
    'STIMTEXT_ONSET': 5,
    'CUE_ONSET':6, 
    'WN_ONSET': 7,
    'SHOCK_ONSET': 8,
    'ANXIETY_RESPONSE': 9,
    'RATING_RESPONSE': 10,
    'TASK_END':StimToolLib.TASK_END
    }


def initiate_startle(idx):
    """
    Startle Subject by writingto DAC0 Register on labjack
    """
    startle_onset_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial_types[idx], g.trial, event_types['WN_ONSET'], g.clock.getTime(), 'NA', '.04', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # Write to Register pin name
    ljm.eWriteName(g.ljhandle, 'DAC0', 2.5) # rise up 
    StimToolLib.just_wait(g.clock, startle_onset_time + .04) # startle for just 40ms
    ljm.eWriteName(g.ljhandle, 'DAC0', 1) # rise down


def initiate_shock(idx):
    """
    Startle Subject by writingto DAC1 Register on labjack
    """
    shock_onset_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, g.trial_types[idx], g.trial, event_types['SHOCK_ONSET'], g.clock.getTime(), 'NA', '100ms', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # Write to Register pin name
    # Pulse Rise every 2ms, since DIGITMER has a limit duration of 2ms
    # So Rise up and Rise down 20 times to make it 100ms, since 1 full period is 5ms
    for stim in range(20):
        ljm.eWriteName(g.ljhandle, 'DAC1', 5) # rise up 
        StimToolLib.just_wait(g.clock, g.clock.getTime() + .002)# Waite 2ms
        ljm.eWriteName(g.ljhandle, 'DAC1', 1) # rise down
        StimToolLib.just_wait(g.clock, g.clock.getTime() + .003)# wait 3ms

def do_one_trial(idx):
    """
    Function for 1 trial

    Parameters
    ----------
    idx : int, rquired
        The integer or trial number, used to grab duration, stim, file, etc from already made array
    """
    g.win.flip()

    trial_start_time = g.clock.getTime()
    g.trial_onset = g.clock.getTime()
    
    # Setup Trial
    trial_type = g.trial_types[idx] # P_1_1_0
    show_cue = trial_type[2] # 0=don't show, 1=show cue
    startle = trial_type[4] # 0=don't startle, 1=startle, refer to the startle_onset of when to startle
    shock= trial_type[6] # 0=don't shock, 1=shock, refer to the shock_onset of when to startle
    cue_onset = g.trial_onset + float(g.cue_onsets[idx]) / 1000.0
    # Stim_onset is in this format: 6000_0
    startle_onset = g.trial_onset  + float(g.stim_onsets[idx].split('_')[0]) / 1000.0 # change to seconds
    shock_onset = g.trial_onset +float(g.stim_onsets[idx].split('_')[1]) / 1000.0

    StimToolLib.mark_event(g.output, g.trial_types[idx], g.trial, event_types['TRIAL_ONSET'],  g.trial_onset, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    # Set text based on condition
    if trial_type[0] == 'N': g.stim_text.setText('No Shock')
    if trial_type[0] == 'P': g.stim_text.setText('Shock only during red square')
    if trial_type[0] == 'U': g.stim_text.setText('Shock at any time')

    ##JUst for TEsting
    #if shock == '1': g.stim_text.setText('Will Shock')

    if show_cue == '1':
        g.stim_text.draw() # Show text
        g.win.flip()

    cue_endset = cue_onset + 8 # cue is always 8 seconds
    startle_endset = startle_onset + .04 # cue is always 8 seconds
    showed_stimtext = False
    showed_cue = False
    startled = False # 
    shocked = False

    while g.clock.getTime() <= g.trial_onset + 17: # 17 second per trialt
        g.stim_text.draw() # Show text
        g.anxiety_rating_stim.draw() # Show the anxiety rating

        k = event.getKeys(['escape', 'z', 'up', 'down'])
        if k:
            if k[0] == 'escape': raise StimToolLib.QuitException()
            if k[0] == 'z': break
            if k[0] == 'up':
                # Increase Anxiety Rating Up

                # Allow increase if it's less than 10. Since Max is 10
                if g.anxiety_rating < 10:
                    g.anxiety_rating += 1
                    g.anxiety_rating_stim.setText(str(g.anxiety_rating))
                    StimToolLib.mark_event(g.output, g.trial_types[idx], g.trial, event_types['ANXIETY_RESPONSE'], g.clock.getTime(), 'NA', 'increased', str(g.anxiety_rating), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            if k[0] == 'down':
                # Increase Anxiety Rating Down

                # Allow decrease if it's more than 0, Since Min is 0
                if g.anxiety_rating > 0:
                    g.anxiety_rating -= 1
                    g.anxiety_rating_stim.setText(str(g.anxiety_rating))
                    StimToolLib.mark_event(g.output, g.trial_types[idx], g.trial, event_types['ANXIETY_RESPONSE'], g.clock.getTime(), 'NA', 'decreased', str(g.anxiety_rating), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

        
        # Show Cue on onset
        if (show_cue == '1') and (g.clock.getTime() >= cue_onset) and (g.clock.getTime() <= cue_endset):
            if not showed_cue:
                StimToolLib.mark_event(g.output, g.trial_types[idx], g.trial, event_types['CUE_ONSET'], g.clock.getTime(), 'NA', '8', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
                showed_cue = True

            if trial_type[0] == 'N': g.circle.draw()
            if trial_type[0] == 'P': g.square.draw()
            if trial_type[0] == 'U': g.triangle.draw()

        # Starle on Cue Onset
        if (startle == '1') and (g.clock.getTime() >= startle_onset) and not startled:
            initiate_startle(idx)
            startled = True

        # Shock on Onset
        if (shock == '1') and (g.clock.getTime() >= shock_onset) and not shocked:
            initiate_shock(idx)
            shocked = True
        
        if not showed_stimtext:
            StimToolLib.mark_event(g.output, g.trial_types[idx], g.trial, event_types['STIMTEXT_ONSET'], g.clock.getTime(), 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            showed_stimtext = True
        g.win.flip()


def run_general_ratings():
    """
    General Ratings:
    1) How anxious are you: (1-10)
    2) How afraid are you: (1-10)
    3) How happy are you: (1-10)
    """
    g.win.flip()
    footer_stim = visual.TextStim(g.win, text = 'Press Enter when done', units = 'norm', color = 'white', pos = (0,-.9), height = .08)

    anxious_stim = visual.TextStim(g.win, text = 'How anxious are you?', units = 'norm', color = 'white', pos = (0,.9), height = .08)
    anxious_slider = visual.Slider(g.win, ticks = range(1,11),labels= range(1,11), pos = (0,.75), size = (1,.08), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)

    afraid_stim = visual.TextStim(g.win, text = 'How afraid are you?', units = 'norm', color = 'white', pos = (0,.35), height = .08)
    afraid_slider = visual.Slider(g.win, ticks = range(1,11),labels= range(1,11), pos = (0,.2), size = (1,.08), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07) 

    happy_stim = visual.TextStim(g.win, text = 'How happy are you?', units = 'norm', color = 'white', pos = (0,-.3), height = .08)
    happy_slider = visual.Slider(g.win, ticks = range(1,11),labels= range(1,11), pos = (0,-.45), size = (1,.08), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)
    while True:
        anxious_stim.draw()
        anxious_slider.draw()

        afraid_stim.draw()
        afraid_slider.draw()

        happy_stim.draw()
        happy_slider.draw()

        footer_stim.draw()

        k = event.getKeys(['escape', 'return'])
        if k:
            if k[0] == 'escape': raise StimToolLib.QuitException()
            if k[0] == 'return' and anxious_slider.markerPos and afraid_slider.markerPos and happy_slider.markerPos: break

        g.win.flip()

    StimToolLib.mark_event(g.output, 'anxious', '-1', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(anxious_slider.markerPos),'How anxious are you?' , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, 'afraid', '-2', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(afraid_slider.markerPos),'How afraid are you?', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, 'happy', '-3', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(happy_slider.markerPos),'How happy are you?', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])


def run_stimulus_ratings():
    """
    Stimulu Ratings:
    1\nnot at all; 5\nmoderately; 10\nextremely
 
    1) How anxious were you during:
        Neutral Period
            Cue: (1-10)
            No Cue:1 (1-10)
        Predictable Period
            Cue: 1-10
            No Cue: 1-10
    
        Unpredictable Period
            Cue: (1-10)
            No Cue: (1-10)
    
    2) How afraid were you during:
        Neutral Period
            Cue: (1-10)
            No Cue:1 (1-10)
        Predictable Period
            Cue: 1-10
            No Cue: 1-10
    
        Unpredictable Period
            Cue: (1-10)
            No Cue: (1-10)
                
    4) How would you rate the intensity of the electrical stimulation? (1-10)
        Not painful at all = 1
        uncomfortable but not painful = 10
 
    5) How would you rate the intensity of the noise? (1-10)
        Not unpleasant at all = 1
        extremely unpleasant = 10

    """
    g.win.flip()
    
    
    # Question 1
    footer_stim = visual.TextStim(g.win, text = 'Press Enter when done', units = 'norm', color = 'white', pos = (0,-.9), height = .08)
    question_stim = visual.TextStim(g.win, text = 'How anxious were you during:', units = 'norm', color = 'white', pos = (0,.9), height = .1)
    period_stim = visual.TextStim(g.win, text = 'Neutral Period\n(No Shocks)', units = 'norm', color = 'white', pos = (0,.65), height = .08,  bold=True)

    g.circle.radius = 40
    g.circle.pos = (-200,210)
    cue_stim = visual.TextStim(g.win, text = 'Cue on screen:', units = 'norm', color = 'white', pos = (0,.35), height = .07)
    cue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,.20), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)

    nocue_stim = visual.TextStim(g.win, text = 'No Cue on screen:', units = 'norm', color = 'white', pos = (0,-.2), height = .07)
    nocue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,-.35), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)
    while True:
        g.circle.draw()
        question_stim.draw()
        period_stim.draw()
        cue_stim.draw()
        cue_slider.draw()
        nocue_stim.draw()
        nocue_slider.draw()
        footer_stim.draw()
        k = event.getKeys(['escape', 'return'])
        if k and k[0] == 'escape': raise StimToolLib.QuitException()
        if k and k[0] == 'return' and cue_slider.markerPos and nocue_slider.markerPos: break
        g.win.flip()
    StimToolLib.mark_event(g.output, 'anxious_neutral_cue', '-4', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(cue_slider.markerPos),'How anxious were you during: Neutral Period - Cue' , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, 'anxious_neutral_nocue', '-5', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(nocue_slider.markerPos),'How anxious were you during: Neutral Period - No Cue', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    g.win.flip()

    question_stim = visual.TextStim(g.win, text = 'How anxious were you during:', units = 'norm', color = 'white', pos = (0,.9), height = .1)
    period_stim = visual.TextStim(g.win, text = 'Predictable Period\n(Shocks only during red square)', units = 'norm', color = 'white', pos = (0,.65), height = .08,  bold=True)

    g.square.width = 40
    g.square.height = 40
    g.square.pos = (-200,210)
    cue_stim = visual.TextStim(g.win, text = 'Cue on screen:', units = 'norm', color = 'white', pos = (0,.35), height = .07)
    cue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,.20), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)

    nocue_stim = visual.TextStim(g.win, text = 'No Cue on screen:', units = 'norm', color = 'white', pos = (0,-.2), height = .07)
    nocue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,-.35), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)
    while True:
        g.square.draw()
        question_stim.draw()
        period_stim.draw()
        cue_stim.draw()
        cue_slider.draw()
        nocue_stim.draw()
        nocue_slider.draw()
        footer_stim.draw()
        k = event.getKeys(['escape', 'return'])
        if k and k[0] == 'escape': raise StimToolLib.QuitException()
        if k and k[0] == 'return' and cue_slider.markerPos and nocue_slider.markerPos: break
        g.win.flip()
    StimToolLib.mark_event(g.output, 'anxious_predictable_cue', '-6', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(cue_slider.markerPos),'How anxious were you during: Predictable Period - Cue' , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, 'anxious_predictable_nocue', '-7', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(nocue_slider.markerPos),'How anxious were you during: Predictable Period - No Cue', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    g.win.flip()

    question_stim = visual.TextStim(g.win, text = 'How anxious were you during:', units = 'norm', color = 'white', pos = (0,.9), height = .1)
    period_stim = visual.TextStim(g.win, text = 'Unpredictable Period\n(Shocks at anytime)', units = 'norm', color = 'white', pos = (0,.65), height = .08,  bold=True)

    g.triangle.radius = 40
    g.triangle.pos = (-200,210)
    cue_stim = visual.TextStim(g.win, text = 'Cue on screen:', units = 'norm', color = 'white', pos = (0,.35), height = .07)
    cue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,.20), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)

    nocue_stim = visual.TextStim(g.win, text = 'No Cue on screen:', units = 'norm', color = 'white', pos = (0,-.2), height = .07)
    nocue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,-.35), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)
    while True:
        g.triangle.draw()
        question_stim.draw()
        period_stim.draw()
        cue_stim.draw()
        cue_slider.draw()
        nocue_stim.draw()
        nocue_slider.draw()
        footer_stim.draw()
        k = event.getKeys(['escape', 'return'])
        if k and k[0] == 'escape': raise StimToolLib.QuitException()
        if k and k[0] == 'return' and cue_slider.markerPos and nocue_slider.markerPos: break
        g.win.flip()
    StimToolLib.mark_event(g.output, 'anxious_unpredictable_cue', '-8', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(cue_slider.markerPos),'How anxious were you during: Unpredictable Period - Cue' , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, 'anxious_unpredictable_nocue', '-9', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(nocue_slider.markerPos),'How anxious were you during: Unpredictable Period - No Cue', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])


    g.win.flip()

    # Question 2
    footer_stim = visual.TextStim(g.win, text = 'Press Enter when done', units = 'norm', color = 'white', pos = (0,-.9), height = .08)
    question_stim = visual.TextStim(g.win, text = 'How afraid were you during:', units = 'norm', color = 'white', pos = (0,.9), height = .1)
    period_stim = visual.TextStim(g.win, text = 'Neutral Period\n(No Shocks)', units = 'norm', color = 'white', pos = (0,.65), height = .08,  bold=True)

    g.circle.radius = 40
    g.circle.pos = (-200,210)
    cue_stim = visual.TextStim(g.win, text = 'Cue on screen:', units = 'norm', color = 'white', pos = (0,.35), height = .07)
    cue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,.20), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)

    nocue_stim = visual.TextStim(g.win, text = 'No Cue on screen:', units = 'norm', color = 'white', pos = (0,-.2), height = .07)
    nocue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,-.35), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)
    while True:
        g.circle.draw()
        question_stim.draw()
        period_stim.draw()
        cue_stim.draw()
        cue_slider.draw()
        nocue_stim.draw()
        nocue_slider.draw()
        footer_stim.draw()
        k = event.getKeys(['escape', 'return'])
        if k and k[0] == 'escape': raise StimToolLib.QuitException()
        if k and k[0] == 'return' and cue_slider.markerPos and nocue_slider.markerPos: break
        g.win.flip()
    StimToolLib.mark_event(g.output, 'afraid_neutral_cue', '-10', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(cue_slider.markerPos),'How afraid were you during: Neutral Period - Cue' , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, 'afraid_neutral_nocue', '-11', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(nocue_slider.markerPos),'How afraid were you during: Neutral Period - No Cue', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    g.win.flip()

    question_stim = visual.TextStim(g.win, text = 'How afraid were you during:', units = 'norm', color = 'white', pos = (0,.9), height = .1)
    period_stim = visual.TextStim(g.win, text = 'Predictable Period\n(Shocks only during red square)', units = 'norm', color = 'white', pos = (0,.65), height = .08,  bold=True)

    g.square.width = 40
    g.square.height = 40
    g.square.pos = (-200,210)
    cue_stim = visual.TextStim(g.win, text = 'Cue on screen:', units = 'norm', color = 'white', pos = (0,.35), height = .07)
    cue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,.20), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)

    nocue_stim = visual.TextStim(g.win, text = 'No Cue on screen:', units = 'norm', color = 'white', pos = (0,-.2), height = .07)
    nocue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,-.35), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)
    while True:
        g.square.draw()
        question_stim.draw()
        period_stim.draw()
        cue_stim.draw()
        cue_slider.draw()
        nocue_stim.draw()
        nocue_slider.draw()
        footer_stim.draw()
        k = event.getKeys(['escape', 'return'])
        if k and k[0] == 'escape': raise StimToolLib.QuitException()
        if k and k[0] == 'return' and cue_slider.markerPos and nocue_slider.markerPos: break
        g.win.flip()
    StimToolLib.mark_event(g.output, 'afraid_predictable_cue', '-12', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(cue_slider.markerPos),'How afraid were you during: Predictable Period - Cue' , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, 'afraid_predictable_nocue', '-13', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(nocue_slider.markerPos),'How afraid were you during: Predictable Period - No Cue', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    g.win.flip()

    question_stim = visual.TextStim(g.win, text = 'How afraid were you during:', units = 'norm', color = 'white', pos = (0,.9), height = .1)
    period_stim = visual.TextStim(g.win, text = 'Unpredictable Period\n(Shocks at anytime)', units = 'norm', color = 'white', pos = (0,.65), height = .08,  bold=True)

    g.triangle.radius = 40
    g.triangle.pos = (-200,210)
    cue_stim = visual.TextStim(g.win, text = 'Cue on screen:', units = 'norm', color = 'white', pos = (0,.35), height = .07)
    cue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,.20), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)

    nocue_stim = visual.TextStim(g.win, text = 'No Cue on screen:', units = 'norm', color = 'white', pos = (0,-.2), height = .07)
    nocue_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nnot at all', '5\nmoderately', '10\nextremely'], pos = (0,-.35), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)
    while True:
        g.triangle.draw()
        question_stim.draw()
        period_stim.draw()
        cue_stim.draw()
        cue_slider.draw()
        nocue_stim.draw()
        nocue_slider.draw()
        footer_stim.draw()
        k = event.getKeys(['escape', 'return'])
        if k and k[0] == 'escape': raise StimToolLib.QuitException()
        if k and k[0] == 'return' and cue_slider.markerPos and nocue_slider.markerPos: break
        g.win.flip()
    StimToolLib.mark_event(g.output, 'afraid_unpredictable_cue', '-14', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(cue_slider.markerPos),'How afraid were you during: Unpredictable Period - Cue' , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, 'afraid_unpredictable_nocue', '-15', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(nocue_slider.markerPos),'How afraid were you during: Unpredictable Period - No Cue', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    g.win.flip()

    # Question 4 and 5
    footer_stim = visual.TextStim(g.win, text = 'Press Enter when done', units = 'norm', color = 'white', pos = (0,-.9), height = .08)
    
    intensity_shock_question_stim = visual.TextStim(g.win, text = 'How would you rate the intensity of the electrical stimulation?', units = 'norm', color = 'white', pos = (0,.8), height = .07)
    intensity_shock_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nNot painful at all', '5', '10\nuncomfortable but not painful'], pos = (0,.65), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)

    intensity_noise_question_stim = visual.TextStim(g.win, text = 'How would you rate the intensity of the noise?', units = 'norm', color = 'white', pos = (0,0), height = .07)
    intensity_noise_slider = visual.Slider(g.win, ticks = range(1,11),labels= ['1\nNot unpleasant at all', '5', '10\nextremely unpleasant'], pos = (0,-.35), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
        color = 'white', font='Helbetica Bold', labelHeight = 0.07)
    while True:
        intensity_shock_question_stim.draw()
        intensity_shock_slider.draw()
        
        intensity_noise_question_stim.draw()
        intensity_noise_slider.draw()

        footer_stim.draw()
        k = event.getKeys(['escape', 'return'])
        if k and k[0] == 'escape': raise StimToolLib.QuitException()
        if k and k[0] == 'return' and intensity_shock_slider.markerPos and intensity_noise_slider.markerPos: break
        g.win.flip()
    StimToolLib.mark_event(g.output, 'intensity_shock', '-16', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(intensity_shock_slider.markerPos),'How would you rate the intensity of the electrical stimulation?' , g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, 'intensity_noise', '-17', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(intensity_noise_slider.markerPos),'How would you rate the intensity of the noise?', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    g.win.flip()

def stimulus_workup():
    """
    Function for running stimulus workup
    """
    footer_stim = visual.TextStim(g.win, text = 'Press Enter to continue', units = 'norm', color = 'white', pos = (0,0), height = .08)
    
    while True:
        footer_stim.draw()
        g.win.flip()
        k = event.getKeys(['escape', 'return'])
        if k and k[0] == 'escape': raise StimToolLib.QuitException()
        if k and k[0] == 'return': break

    footer_stim.pos = (0,-.9)
    top_text_stim = visual.TextStim(g.win, text = 'Please let the experimenter know if you can hear the sound.', units = 'norm', color = 'white', pos = (0,0), height = .1)
    # Startle them for 9 times
    for idx in range(9):
        k = event.getKeys(['escape', 'z'])
        if k and k[0] == 'escape': raise StimToolLib.QuitException()
        if k and k[0] == 'z': break
        g.fixation.draw()
        g.win.flip()
        initiate_startle(0)
        StimToolLib.just_wait(g.clock, g.clock.getTime() + .3) # 1 second between each startle?


    ## Shock Workup
    StimToolLib.do_one_slide_keyselect('NPU_R0_2.JPG,NPU_R0_2.aiff,-1'.split(','), os.path.join(os.path.dirname(__file__), 'media', 'instructions'), g)
    top_text_stim = visual.TextStim(g.win, text = 'When the experimenter says the device is ready press enter to deliver the shock.', units = 'norm', color = 'white', pos = (0,.8), height = .07)
    
    slider_question = visual.TextStim(g.win, text = 'Please rate the level of the shock.', units = 'norm', color = 'white', pos = (0,.2), height = .06)
    md_text_stim = visual.TextStim(g.win, text = 'Please let the experimenter know and they will increase the level.', units = 'norm', color = 'white', pos = (0,-.6), height = .1)
    

    repeat = True
    shocked = False
    wait_ = False
    ask_not_painful = False
    ask_shock_painful = False
    short_wait_ = False
    key_list = ['escape', 'return']
    
    play_experimtner_says = True
    play_question_rate_level = False

    play_decrease = False
    play_increase = False
    play_start = False

    while repeat:
        top_text_stim.draw()
        if play_experimtner_says:
            g.win.flip()
            g.statement_when_experminter.play()
            
            k = event.waitKeys(keyList = key_list)

            if k and k[0] == 'escape': raise StimToolLib.QuitException()
            if k and k[0] == 'return' and not shocked:
                if g.statement_when_experminter: g.statement_when_experminter.stop()
                ## Delivery Shock
                initiate_shock(0)
                # Please rate the level of the shock
                shock_slider =  visual.Slider(g.win, ticks = range(1,6), labels= ['1\nBarely Felt','5\nVery unpleasant/uncomfortable'],pos = (0,0), size = (1,.05), units = 'norm', flip=False, granularity = 1, readOnly = False,
            color = 'white', font='Helbetica Bold', labelHeight = 0.04)
                shocked = True
                play_experimtner_says = False
                play_question_rate_level = True
                

        if shocked:
            slider_question.draw()
            shock_slider.draw()
            # g.win.flip()
            # if play_question_rate_level:
            #     g.statement_rate_level.play()

            if shock_slider.markerPos and  shock_slider.markerPos < 4:
                repeat = True
                md_text_stim.draw()
                #wait_ = True
                shocked = False
                play_increase = True
                play_experimtner_says = True
                if g.statement_rate_level: g.statement_rate_level.stop()
                play_question_rate_level = False
                StimToolLib.mark_event(g.output, 'shock_rating', 'NA', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(shock_slider.markerPos),'Please rate the level of the shock.', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

            if shock_slider.markerPos and shock_slider.markerPos >= 4:
                ask_not_painful = True
                ask_shock_painful = False
                shocked = False
                top_text_stim.setText('\n\n\n\n\n\n\n\n\n\n\n\n\nIs this level of shock uncomfortable but not painful?\n\nYes = Press the "y" key\nNo = Press the "n" key')
                key_list = ['escape', 'y', 'n']
                short_wait_ = True
                play_question_rate_level = False
                if g.statement_rate_level: g.statement_rate_level.stop()
                StimToolLib.mark_event(g.output, 'shock_rating', 'NA', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', str(shock_slider.markerPos),'Please rate the level of the shock.', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        
        elif ask_not_painful:
            g.win.flip()
            g.question_level_shock_painful.play()
            k = event.waitKeys(keyList = key_list)
            if k and k[0] == 'escape': raise StimToolLib.QuitException()
            if k and k[0] == 'y':
                md_text_stim.setText('Please let the experimenter know when you are ready to start the task.')
                md_text_stim.draw()
                #wait_ = True
                repeat = False
                ask_not_painful = False
                play_start = True
                event.clearEvents()
                if g.question_level_shock_painful: g.question_level_shock_painful.stop()
                StimToolLib.mark_event(g.output, 'ask_not_painful', 'NA', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', 'Yes','Is this level of shock uncomfortable but not painful?', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

            if k and k[0] == 'n':
                print('Pressed no')
                top_text_stim.setText('\n\n\n\n\n\n\n\n\n\n\n\n\nWere the shocks painful?\n\nYes = Press the "y" key\nNo = Press the "n" key')
                ask_shock_painful = True
                repeat = True
                ask_not_painful = False
                if g.question_level_shock_painful: g.question_level_shock_painful.stop()
                event.clearEvents()
                StimToolLib.mark_event(g.output, 'ask_not_painful', 'NA', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', 'No','Is this level of shock uncomfortable but not painful?', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        
        elif ask_shock_painful:
            g.win.flip()
            g.question_shocks_painful.play()
            k = event.waitKeys(keyList = key_list)
            if k and k[0] == 'escape': raise StimToolLib.QuitException()
            if k and k[0] == 'y':
                md_text_stim.setText('Please let the experimenter know and they will decrease the level.')
                top_text_stim.setText('When the experimenter says the device is ready press enter to deliver the shock.')
                key_list = ['escape', 'return']
                md_text_stim.draw()
                #wait_ = True
                repeat = True
                ask_shock_painful = False
                play_decrease = True
                play_experimtner_says = True
                if g.question_shocks_painful: g.question_shocks_painful.stop()
                StimToolLib.mark_event(g.output, 'ask_shock_painful', 'NA', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', 'Yes','Were the shocks painful?', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
            
            if k and k[0] == 'n':
                md_text_stim.setText('Please let the experimenter know when you are ready to start the task.')
                md_text_stim.draw()
                #wait_ = True
                repeat = False
                ask_shock_painful = False
                play_start = True
                if g.question_shocks_painful: g.question_shocks_painful.stop()
                StimToolLib.mark_event(g.output, 'ask_shock_painful', 'NA', event_types['RATING_RESPONSE'], g.clock.getTime(), 'NA', 'No','Were the shocks painful?', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

        g.win.flip()

        if play_start:
            g.statement_start_task.play()
            StimToolLib.just_wait(g.clock, g.clock.getTime() + g.statement_start_task.getDuration())
            play_start = False

        if play_decrease:
            g.statement_decrease_level.play()
            StimToolLib.just_wait(g.clock, g.clock.getTime() + g.statement_decrease_level.getDuration())
            play_decrease = False

        if play_increase:
            g.statement_increase_level.play()
            StimToolLib.just_wait(g.clock, g.clock.getTime() + g.statement_increase_level.getDuration())
            play_increase = False

        # Shock, wasn't that painful so we will wait and repeat
        if wait_: 
            StimToolLib.just_wait(g.clock, g.clock.getTime() + 5)
            wait_ = False
        if short_wait_:
            StimToolLib.just_wait(g.clock, g.clock.getTime() + 1)
            short_wait_ = False

    pass

def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/NPU.Default.params', {})
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
    #param_filename = os.path.dirname(__file__) + '/data/' + g.session_params['SID'] + '-' + g.session_params['session_id'] + '-' + 'FC.params'
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="NPU")
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


    # Check if Labjack in plugged in
    # Open first found LabJack
    try:
        g.ljhandle = ljm.openS("ANY", "ANY", "ANY")
        # set DAC pins to 0
        ljm.eWriteName(g.ljhandle, 'DAC0', 1)
        ljm.eWriteName(g.ljhandle, 'DAC1', 1)
    except:
        myDlg = gui.Dlg(title="LabJack Error")
        myDlg.addText("It doesn't look like you have labjack plugged in?\nPlease plug in the labjack to run this task.")
        myDlg.show()  # show dialog and wait for OK or Cancel
        raise StimToolLib.QuitException()


   
    StimToolLib.general_setup(g, winType = 'pyglet')

    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    
    g.prefix = StimToolLib.generate_prefix(g)
    g.subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '_' + g.run_params['param_file'])

    
    if '_RX_' in g.run_params['run']:
        # Counterbalance based on subject ID
        while True:
            # check if subject id number is a number, open a popup if it's not
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

        run_order_dict = {
            0: 'AB', # Event Order
            1: 'BA', # Odd Order
        }

        order_idx = id_number % 2
        run_order = run_order_dict[order_idx]

        StimToolLib.write_var_to_file(os.path.join(os.path.dirname(__file__), g.subj_param_file), 'run_order', run_order)

        # Set the run schdule based on the order
        if '_RX_A' in g.run_params['run']:   g.run_params['run'] = g.run_params['run'].replace('_RX_A','_RX_%s' % run_order[0] )
        elif '_RX_B' in g.run_params['run']: g.run_params['run'] = g.run_params['run'].replace('_RX_B','_RX_%s' % run_order[1] )
        
        print("NEW g.run_params['run'] = %s" % g.run_params['run'] )
        # Getting New Params 
        # Uncomment below if we think we want to grap all the run paramatesrs as well. Proabably unlikely since instructions we want the same
        #StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), g.run_params['run'][0:-9] + '.params'), g.run_params)


    print("RUN PARAMS")
    print(g.run_params)
    start_time = data.getDateStr()

    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    g.trial_types,blank,g.cue_onsets, g.stim_onsets = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    

    fileName = os.path.join(g.prefix + '.csv')
    g.output = open(fileName, 'w')
    
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  param_file + ',Event Codes:,' + str(sorted_events) + 'TrialTypes X_X_X_X X[0]->NPU X[1]->CUE(1=Show CUE|0=Dont Show) X[2]-> STARTLE(1=STARTLE|0=Dont Startle) X[3]->SHOCK(1=Shock|0=Dont Shock),,cue_onset,stim_onsets\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    

    text_height = 80
    
    # Task Media Only used for this task
    g.fixation = visual.TextStim(g.win, text = '+', units = 'norm', color = 'white', pos = (0,0), height = .4)
    g.stim_text = visual.TextStim(g.win, text = 'No Shocks', units = 'norm', pos = (0,.7), color = 'white', height = .2)
    g.circle = visual.Circle(g.win, radius = 170, units = 'pix', pos = (0,0),lineWidth=10, lineColor  = 'green')
    g.square = visual.Rect(g.win, width = 200, height =200, units = 'pix', pos = (0,0),lineWidth=10, lineColor = 'red')
    g.triangle = visual.Polygon(g.win, edges = 3, radius = 170, units = 'pix', pos = (0,0),lineWidth=10, lineColor = 'blue')
    g.anxiety_rating_stim = visual.TextStim(g.win, text = str(g.anxiety_rating), units = 'norm', color = 'white', pos = (0,0), height = .2)

    # Get the String Array List to show letters
    #print g.trial_types
    g.cue_onsets = g.cue_onsets[0]
    g.stim_onsets = g.stim_onsets[0]


    #print(g.stim_paths)
    # hide the mouse
    if g.mouse: g.mouse.setVisible(False)

    print('SCHEDULE')
    print(g.trial_types)
    print(g.cue_onsets)
    print(g.stim_onsets)
    print('RUN PARAMS')
    print(g.run_params)
    StimToolLib.task_start(StimToolLib.NPU_CODE, g)
    instruct_start_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_start_time, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])


    ### TESTING PURPOSE
    #run_stimulus_ratings()

    StimToolLib.run_instructions_keyselect(os.path.join(os.path.dirname(__file__), 'media', 'instructions', g.run_params['instruction_schedule']), g)

    if '_R0_' in g.run_params['run']:
        ### import audio for workup
        g.statement_when_experminter = sound.Sound(value = os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'NPU_R0_statememt_when_experimenter.aiff' ))
        g.question_shocks_painful = sound.Sound(value = os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'NPU_R0_question_were_shocks_painful.aiff' ))
        g.question_level_shock_painful = sound.Sound(value = os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'NPU_R0_question_level_shock_painful.aiff' ))
        g.statement_rate_level = sound.Sound(value = os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'NPU_R0_statememt_rate_level.aiff' ))
        g.statement_decrease_level = sound.Sound(value = os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'NPU_R0_statememt_decrease_level.aiff' ))
        g.statement_increase_level = sound.Sound(value = os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'NPU_R0_statememt_increase_level.aiff' ))
        g.statement_start_task = sound.Sound(value = os.path.join(os.path.dirname(__file__), 'media', 'instructions', 'NPU_R0_statememt_start_task.aiff' ))
        stimulus_workup()
        return

    g.trial = 0
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win, five_only = True)
    else:
        StimToolLib.wait_start(g.win)
    g.win.flip()
    instruct_end_time = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end_time, instruct_end_time - instruct_start_time, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])

    g.ideal_trial_start = instruct_end_time

     # Startle them for 4 times
    for idx in range(4):
        k = event.getKeys(['escape', 'z'])
        if k and k[0] == 'escape': raise StimToolLib.QuitException()
        if k and k[0] == 'z': break
        g.fixation.draw()
        g.win.flip()
        initiate_startle(0)
        StimToolLib.just_wait(g.clock, g.clock.getTime() + .3) # 1 second between each startle?
    

    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['FIXATION_ONSET'], g.clock.getTime(), 'NA', 'NA', '8', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    # Wait 8 seconds after scanner start
    while g.clock.getTime() <= instruct_end_time + 8:
        g.fixation.draw()
        g.win.flip()
        k = event.getKeys(['escape', 'z'])
        if k:
            if k[0] == 'escape': raise StimToolLib.QuitException()
            if k[0] == 'z': break
    
    

    #####StimToolLib.just_wait(g.clock, g.clock.getTime() + 8)
    g.ideal_trial_start = instruct_end_time + 8

    indices = range(len(g.trial_types))
    g.trial = 0
    for idx in  indices:
        do_one_trial(idx)
        g.trial = g.trial + 1
    
    ## General Ratings After each run
    run_general_ratings()
    run_stimulus_ratings()

    # Displya Break Slide after Run 1

    if '-R1-' in g.run_params['run_id']:
        StimToolLib.do_one_slide_keyselect('NPU_R1_break.JPG,None,-1'.split(','), os.path.join(os.path.dirname(__file__), 'media', 'instructions'), g)
