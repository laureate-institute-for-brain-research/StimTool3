from psychopy import prefs
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui, sound
from psychopy.hardware import joystick
import time

# prefs.hardware['audioLib'] = ['pyo', 'pygame']

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.clock = None #global clock used for timing
        self.output = None #The output file
        self.msg = None
        self.response_type = 'joystick' # The response Type for this task
        self.DIAL_LIMIT = 5 # Number of key in order to register a movement

event_types = {'INSTRUCT_ONSET':1, 
    'TASK_ONSET':2, 
    'SELECTION_MADE':3,
    'RIGHT_MAX':4,
    'LEFT_MAX':5,
    'TASK_END':StimToolLib.TASK_END}
       
def draw_display():
    g.vol_knob.draw()
    g.vol_msg0.draw()
    g.vol_msg1.draw()
    g.vol_msg2.draw()
    g.vol_msg3.draw()

def volume_workup_dial(sound_file, start_volume):
    """
    Volume Workup but for the using dial
    """
    s = sound.Sound(sound_file)
    possible_options = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1']
    index= 5
    last_volume = possible_options[index]
    
    g.win.setColor([-1,-1,-1])
    g.msg.setColor([1,1,1])
    
    g.vol_knob=visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'Images', last_volume +'.png'), units='pix', pos=(23,-180))
    g.vol_msg0 = visual.TextStim(g.win, text="SOUND CHECK", units='pix', color='Yellow', bold=True, pos=(0,190), height=46, alignHoriz='center')
    g.vol_msg1 = visual.TextStim(g.win, text='To increase the volume, rotate the dial RIGHT', units='pix', pos=(-435,131), color=([1,1,1]), height=43, alignHoriz='left', wrapWidth=1000)
    g.vol_msg2 = visual.TextStim(g.win, text='To decrease the volume, rotate the dial LEFT', units='pix', pos=(-435,86), color=([1,1,1]), height=43, alignHoriz='left', wrapWidth=1000)
    g.vol_msg3 = visual.TextStim(g.win, text='To select the volume, push the dial DOWN', units='pix', pos=(-435,41), color=([1,1,1]),height=43,alignHoriz='left', wrapWidth=1000)
    
    dial_left_current = 0
    dial_right_current = 0
    
    next_play = g.clock.getTime() + s.getDuration() # Next Play
    sound_playing = False
    last_key = ''
    while True:
        g.vol_knob.setImage(os.path.join(os.path.dirname(__file__), 'Images', last_volume +'.png'))
        draw_display()
        g.win.flip()
        

        s.setVolume(float(last_volume))
        # print(last_volume)

        # Play sound if sound is not playing
        if not sound_playing:
            s.play()
            sound_playing = True
            next_play = g.clock.getTime() + s.getDuration() # Next Play

        # Stop Sound if past the next_play
        if g.clock.getTime() >= next_play and sound_playing:
            s.stop()
            sound_playing = False
        
        resp = event.getKeys(['t','b',g.session_params['dial_select'], 'escape'])

        if resp and resp[0] == 'escape': raise StimToolLib.QuitException()

        # Rotate Left
        if resp and resp[0] == 'b':
            if last_key != 'b': 
                dial_left_current = 0
                last_key = 'b'
                continue
            
            if dial_left_current <= g.DIAL_LIMIT:
                dial_left_current += 1
                last_key = 'b'
                continue
            dial_left_current = 0

            # Constitute a turn

            # Check if current position is no at the last
            if index > 0:
                index -= 1
                last_volume=possible_options[index]
                last_key = 'b'
                continue

        
        # # Rotate Right

        if resp and resp[0] == 't':
            if last_key != 't': 
                dial_right_current = 0
                last_key = 't'
                continue
            
            if dial_right_current <= g.DIAL_LIMIT:
                dial_right_current += 1
                last_key = 't'
                continue
            dial_right_current = 0

            # Constitute a turn

            # Check if current position is not the highest
            if index < 10:
                index += 1
                last_volume=possible_options[index]
                last_key = 't'
                continue


        if resp and resp[0] == g.session_params['dial_select']: return float(last_volume)




def volume_workup_joystick(sound_file, start_volume):
    
    s = sound.Sound(sound_file)
    possible_options = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1']
    index= 2 # Starting volume
    last_volume = possible_options[index]
    
    g.win.setColor([-1,-1,-1])
    g.msg.setColor([1,1,1])
    g.win.flip()
    
    g.vol_knob=visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'Images', last_volume +'.png'), units='pix', pos=(23,-180))
    g.vol_msg0 = visual.TextStim(g.win, text="SOUND CHECK", units='pix', color='Yellow', bold=True, pos=(0,190), height=46, alignHoriz='center')
    g.vol_msg1 = visual.TextStim(g.win, text="To increase the volume, push the joystick upward", units='pix', pos=(-435,131), color=([1,1,1]), height=43, alignHoriz='left', wrapWidth=1000)
    g.vol_msg2 = visual.TextStim(g.win, text="To decrease the volume, pull the joystick downward", units='pix', pos=(-435,86), color=([1,1,1]), height=43, alignHoriz='left', wrapWidth=1000)
    g.vol_msg3 = visual.TextStim(g.win, text="To select the volume, press the trigger button.", units='pix', pos=(-435,41), color=([1,1,1]),height=43,alignHoriz='left', wrapWidth=1000)
    
    
    while True:
        g.vol_knob.setImage(os.path.join(os.path.dirname(__file__), 'Images', last_volume +'.png'))
        draw_display()
        g.win.flip()

        s.setVolume(float(last_volume))
        print(last_volume)
        s.play()
        now=g.clock.getTime()

        g.joystick = joystick.Joystick(0) 
        StimToolLib.just_wait(g.clock, now+2)
        s.stop()
        draw_display()
        g.win.flip()

        while g.joystick.getY()<0.8 and g.joystick.getY()>-0.8 and not g.joystick.getButton(g.session_params['joy_forward']):
            k=event.getKeys('escape')
            if k!=[] and k != None:
                if k[0]=='escape':
                    raise StimToolLib.QuitException()
            event.clearEvents()
            draw_display()
            g.win.flip()
    
        now=g.clock.getTime()
        if g.joystick.getButton(g.session_params['joy_forward']):
            return float(last_volume)
        elif  g.joystick.getY()<-0.8:
            try:
                last_volume=possible_options[index + 1]
                index=index+1
            except IndexError:
                g.msg.setText('Maximum volume reached. You can not pick a volume higher than this.')
                g.msg.draw()
                g.win.flip()
                StimToolLib.just_wait(g.clock, now+2.5)
        elif  g.joystick.getY()>0.8:
            if index-1>=0:
                last_volume=possible_options[index - 1]
                index = index - 1
            else:
                g.msg.setText('Minimum volume reached. You can not pick a volume lower than this.')
                g.msg.draw()
                g.win.flip()
                StimToolLib.just_wait(g.clock, now+2.5)




def volume_workup_buttons(sound_file, start_volume):
    
    s = sound.Sound(sound_file)
    possible_options = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1']
    index= 2 # Starting volume
    last_volume = possible_options[index]
    
    g.win.setColor([-1,-1,-1])
    g.msg.setColor([1,1,1])
    g.win.flip()
    
    g.vol_knob=visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__), 'Images', last_volume +'.png'), units='pix', pos=(23,-180))
    g.vol_msg0 = visual.TextStim(g.win, text="SOUND CHECK", units='pix', color='Yellow', bold=True, pos=(0,190), height=46, alignHoriz='center')
    g.vol_msg1 = visual.TextStim(g.win, text="To increase the volume, push the left button", units='pix', pos=(-435,131), color=([1,1,1]), height=43, alignHoriz='left', wrapWidth=1000)
    g.vol_msg2 = visual.TextStim(g.win, text="To decrease the volume, push the right button", units='pix', pos=(-435,86), color=([1,1,1]), height=43, alignHoriz='left', wrapWidth=1000)
    g.vol_msg3 = visual.TextStim(g.win, text="To select the volume, push the select button.", units='pix', pos=(-435,41), color=([1,1,1]),height=43,alignHoriz='left', wrapWidth=1000)
    
    while True:
        g.vol_knob.setImage(os.path.join(os.path.dirname(__file__), 'Images', last_volume +'.png'))
        draw_display()
        g.win.flip()

        s.setVolume(float(last_volume))
        print(last_volume)
        s.play()
        now=g.clock.getTime()

        StimToolLib.just_wait(g.clock, now+2)
        s.stop()
        draw_display()
        g.win.flip()

        resp = event.waitKeys(keyList = [g.session_params['left'],g.session_params['right'],g.session_params['select'], 'escape'])

        #if not resp:
        #    continue
        if resp and resp[0] == 'escape': raise StimToolLib.QuitException()

        now=g.clock.getTime()
        if resp[0] == g.session_params['select']:
            return float(last_volume)
        elif  resp[0] == g.session_params['right']:
            try:
                last_volume=possible_options[index + 1]
                index=index+1
            except IndexError:
                g.msg.setText('Maximum volume reached. You can not pick a volume higher than this.')
                g.msg.draw()
                g.win.flip()
                StimToolLib.just_wait(g.clock, now+2.5)
        elif  resp[0] == g.session_params['left']:
            if index-1>=0:
                last_volume=possible_options[index - 1]
                index = index - 1
            else:
                g.msg.setText('Minimum volume reached. You can not pick a volume lower than this.')
                g.msg.draw()
                g.win.flip()
                StimToolLib.just_wait(g.clock, now+2.5)



def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/VW.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status


def run_try():  
   
    # prefs.hardware['audioLib'] = ['PTB', 'pygame']
    # prefs.hardware['audioDriver'] = ['ASIO4ALL', 'ASIO', 'Audigy']
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg = gui.Dlg(title="VW")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            #print 'QUIT!'
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    g.prefix = StimToolLib.generate_prefix(g)
    fileName = os.path.join(g.prefix + '.csv')
    subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '_' + g.run_params['param_file'])
    g.output= open(fileName, 'w')
    #sorted_events = sorted(event_types.iteritems(), key=operator.itemgetter(1))
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    start_time = data.getDateStr()
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  schedule_file + ",Event Codes:," + str(sorted_events) + '\n')    
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    

    g.response_type = 'joystick' # default response type is joystick

    try:
        g.response_type = g.run_params['response_type']
    except:
        # probably doesn't have response_type params
        pass
    
    winType = 'pyglet'
    if g.response_type == 'joystick': winType = 'pygame'

    StimToolLib.general_setup(g, winType=winType)

    if g.response_type == 'joystick':
        # setup joystic
        joystick.backend=g.win.winType
        nJoysticks=joystick.getNumJoysticks()
        if nJoysticks>0:
            g.joystick = joystick.Joystick(0) 
    #            if nJoysticks>1:
    #                StimToolLib.error_popup("Multiple joysticks connected, please only have task joystick plugged in")
        else:
            StimToolLib.error_popup("You don't have a joystick connected?")


    StimToolLib.task_start(StimToolLib.VOLUME_WORKUP_CODE, g) #send message that this task is starting
    instruct_onset = g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['INSTRUCT_ONSET'], instruct_onset, 'NA', 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    
    if g.response_type == 'joystick':
        StimToolLib.run_instructions_joystick(os.path.join(os.path.dirname(__file__), 'Instructions',  g.run_params['instruction_schedule']), g)
    
    if g.response_type == 'dial':
        StimToolLib.run_instructions_dial(os.path.join(os.path.dirname(__file__), 'Instructions', g.run_params['instruction_schedule']), g)

    if g.response_type == 'buttons':
        StimToolLib.run_instructions(os.path.join(os.path.dirname(__file__), 'Instructions', g.run_params['instruction_schedule']), g)

    # Allow Wait Scan start to be started by 5 only
    five_only = False
    if g.response_type == 'dial': five_only = True
    if g.session_params['scan']:
        StimToolLib.wait_scan_start(g.win, five_only = five_only)
    else:
        StimToolLib.wait_start(g.win)
    instruct_end=g.clock.getTime()
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['TASK_ONSET'], instruct_end, instruct_end - instruct_onset, 'NA', 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    g.win.flip()
    g.win.setColor([-1,-1,-1])
    g.msg.setColor([1,1,1])
    g.win.flip()
    
    if g.response_type == 'joystick':
        selected_volume=volume_workup_joystick(os.path.join(os.path.dirname(__file__),'Kid_laugh.aiff'), 0.1)
    if g.response_type == 'dial':
        selected_volume=volume_workup_dial(os.path.join(os.path.dirname(__file__),'Kid_laugh.aiff'), 0.1)
    if g.response_type == 'buttons':
        selected_volume=volume_workup_buttons(os.path.join(os.path.dirname(__file__),'Kid_laugh.aiff'), 0.1)


    sel_time=g.clock.getTime()
    StimToolLib.write_var_to_file(subj_param_file, 'volume', selected_volume)
    StimToolLib.mark_event(g.output, 'NA', 'NA', event_types['SELECTION_MADE'], sel_time, sel_time-instruct_end, selected_volume, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    if g.response_type == 'buttons':
        return
    g.win.setColor([0,0,0])
    g.msg.setColor([-1,-1,-1])
    g.win.flip()
    
    g.win.setColor('white')
    #g.msg.setColor([-1,-1,-1])
    g.win.flip()
    
    sel_time=g.clock.getTime()
    g.msg = visual.TextStim(g.win, text = '', units = 'norm', pos=(0,0), color = 'black', alignHoriz='center', font = 'helvetica')
    #g.msg.setText('1bcdefghijklmnopqrstuvwxyz12345678902bcdefghijklmnopqrstuvwxyz12345678903bcdefghijklmnopqrstuvwxyz12345678904bcdefghijklmnopqrstuvwxyz1234567890')
    g.msg.setText('press Enter')
    # For pygame, setting the text in the middle can't be done by anchoring text
    # So we need to se the positive manually. This is done by finding the length of the text and setting the position based of screen size

    #g.msg.pos = StimToolLib.getMSGPosition(g.win.size, g.msg)
    g.msg.draw()
    g.win.flip()

    #global event

    # while True:
    #     for pevent in pygame.event.get():
    #         if pevent.type == pygame.KEYDOWN: break

    event.clearEvents()
    while True:
        event.clearEvents()
        time.sleep(.5)
        print('inside the inf loop')
        key = event.getKeys(['return'])
        if key: break
    circ = visual.Circle(g.win,units='pix',pos=[0,-100],radius=30,fillColor='red')
    circ.draw()
    g.win.flip()
        
    pressed=False

    # ######## Custom pygame backend for joystick ############
    # print('#####USING PYGAME as Joystick BACKEND')
    # pygame.display.init()
    # pygame.joystick.init()

    # g.joystick = pygame.joystick.Joystick(0)
    # g.joystick.init()
    #########################################################


    
    # print(g.joystick.get_name())
    # print('First X position %s' % g.joystick.get_axis(0))
    # g.joystick = joystick.Joystick(0) 
    g.msg.setColor('red')
    if g.response_type == 'joystick':
        g.msg.setText('Move the the joystick all the way RIGHT and press the trigger button.')
    if g.response_type == 'dial':
        g.msg.setText('Rotate the the dial all the way RIGHT and press Enter.')
    #g.msg.pos = StimToolLib.getMSGPosition(g.win.size, g.msg)
    
    #g.msg.color = 'red'
    event.clearEvents()
    dial_x = 0
    circ.pos[0] = 0
    # env1 = EnvelopeGrating(g.win, ori=0, units='norm', carrier='sin', envelope='sin', mask='gauss', sf=4, envsf=8, size=1, contrast=1.0, moddepth=0.0, envori=0, pos=[0, .5], interpolate=0)
    while True:
        # env1.ori += 0.1
        # env1.draw()
        g.msg.draw()
        #pygame.event.pump()
        resp = event.getKeys(['t', 'b', 'return', 'escape'])
        if g.response_type == 'joystick':
            x = g.joystick.getX()
            circ.pos[0] = x * g.session_params['screen_x']/2

        if g.response_type == 'dial':
            if resp and resp[0] == 't':
                if circ.pos[0] < ( int(g.session_params['screen_x']) /2):
                    circ.pos[0] += 20
                
            if resp and resp[0] == 'b':
                if circ.pos[0] > -(int(g.session_params['screen_x']) /2):
                    # On the edge of the screen
                    circ.pos[0] -= 20
                
        circ.pos  = circ.pos # For som reason, this has to be here
        # print(circ.pos)
        circ.draw()
       
        #k = event.getKeys(keyList=['return'])
        if g.response_type == 'joystick' and g.joystick.getButton(g.session_params['joy_forward']): break
        if resp and resp[0] == 'return': break

        if resp and resp[0] == 'escape': raise StimToolLib.QuitException()
        g.win.flip()
        # event.clearEvents()

    g.win.flip()
    g.msg.setColor('black')
    g.msg.setText('Press enter to continue.')
    #g.msg.pos = StimToolLib.getMSGPosition(g.win.size, g.msg)
    g.msg.draw()
    g.win.flip()
    # evt.clear()
    # evt.get()
    
    event.clearEvents()
    while True:
        event.clearEvents()
        time.sleep(.5)
        print('inside the inf loop')
        key = event.getKeys(['return'])
        if key: break
    pressed=False
    #g.joystick = joystick.Joystick(0) 
    g.msg.setColor('blue')
    if g.response_type == 'joystick':
        g.msg.setText('Move the the joystick all the way LEFT and press the trigger button.')
    if g.response_type == 'dial':
        g.msg.setText('Rotate the the dial all the way LEFT and press Enter.')

    #g.msg.pos = StimToolLib.getMSGPosition(g.win.size, g.msg)
    #g.msg.setColor('blue')
    circ.fillColor='blue'
    event.clearEvents() 
    circ.pos[0] = 0  
    while True:
        g.msg.draw()
        resp = event.getKeys(['t', 'b', 'return', 'escape'])
        if g.response_type == 'joystick':
            x = g.joystick.getX()
            circ.pos[0] = x * g.session_params['screen_x']/2

        if g.response_type == 'dial':
            if resp and resp[0] == 't':
                if circ.pos[0] < ( int(g.session_params['screen_x']) /2):
                    circ.pos[0] += 20
                
            if resp and resp[0] == 'b':
                if circ.pos[0] > -(int(g.session_params['screen_x']) /2):
                    # On the edge of the screen
                    circ.pos[0] -= 20
        
        circ.pos  = circ.pos 
        circ.draw()
       
        #k = event.getKeys(keyList=['return'])
        if g.response_type == 'joystick' and g.joystick.getButton(g.session_params['joy_forward']): break
        if resp and resp[0] == 'return': break

        if resp and resp[0] == 'escape': raise StimToolLib.QuitException()
        g.win.flip() 


    g.win.flip()
    g.win.setColor('white')
    g.msg.setColor('black')
    g.win.flip()  

    # g.joystick._device.close()
    event.clearEvents()
    #g.joystick._device.close()
    #print(g.joystick.__dict__)
        

