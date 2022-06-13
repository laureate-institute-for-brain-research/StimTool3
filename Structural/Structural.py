
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui

#rest module: present crosshairs for a fixed duration

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.title = 'Rest'
        self.output = None
        self.image_time = 10
        self.task_duration=420

    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/S.Default.params', {})
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
        myDlg = gui.Dlg(title="STRUCT")
        myDlg.addField('Run Number', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            #print 'QUIT!'
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    
    
    StimToolLib.general_setup(g)
    
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    #param_file = os.path.join(os.path.dirname(__file__),'T1000_Rest_Schedule1.csv')
    junk,images,junk,junk = StimToolLib.read_trial_structure(schedule_file, g.win, g.msg)
    
    # print('images"')
    # print(images)
    start_time = data.getDateStr()
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    
    start = g.clock.getTime()
    idx=0

    g.fixation = visual.TextStim(g.win, text = '+', units = 'norm', pos = (0,0), height = .3)

    is_blank = False
    try:
        is_blank = g.run_params['blank']
    except:
        pass

    duration = False # default is false so structural scan runs indefinitley
    try:
        duration = g.run_params['duration']
    except:
        pass

    response_type = 'button_box' #default response box
    try:
        response_type = g.run_params['response_type']
    except:
        # if it gets to here, probably means, there's no reponse_type in run params
        pass
    # Wait Scan Start only for when duration params is set
    # To avoid inconsistency from previou study that doesn't nee to auto_advance when structurals are done.
    if duration:
        # Allow Wait Scan start to be started by 5 only
        five_only = False
        if response_type == 'dial': five_only = True
        StimToolLib.wait_scan_start(g.win, five_only = five_only)

    now =g.clock.getTime()

    print("RUN PARAMS")
    print(g.run_params)

    ##
    while True:
        if is_blank:
            g.win.flip()
            g.fixation.draw()
            g.win.flip()
            StimToolLib.check_for_esc()

            # If there is a duration, than show fixation for that long
            if duration: 
                StimToolLib.just_wait(g.clock, now + duration)
                break
        else:
            new_image_onset=g.clock.getTime()
            images[0][idx].size = [g.session_params['screen_x'], g.session_params['screen_y']]
            # i_size=images[0][idx].size
            # if i_size[0]>=i_size[1]:
            #     images[0][idx].size = (images[0][idx].size) * (g.session_params['screen_x']-10)*1.0/i_size[0]
            #     if images[0][idx].size[1]>(g.session_params['screen_y']-10):
            #         images[0][idx].size = (images[0][idx].size) * (g.session_params['screen_y']-10)*1.0/i_size[1]
            # elif i_size[0]<i_size[1]:
            #     images[0][idx].size = (images[0][idx].size) * (g.session_params['screen_y']-10)*1.0/i_size[1]    
            #     if images[0][idx].size[0]>(g.session_params['screen_x']-10):
            #         images[0][idx].size = (images[0][idx].size) * (g.session_params['screen_x']-10)*1.0/i_size[0]

            images[0][idx].draw()
            g.win.flip()
            StimToolLib.just_wait(g.clock, new_image_onset + g.image_time)
            idx=idx + 1 
            if idx==len(images[0])-1:
                idx=0
        
    
    

  
 


