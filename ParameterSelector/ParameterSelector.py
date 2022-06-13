
import StimToolLib, os, random, operator
from psychopy import visual, core, event, data, gui
import string
import json

#rest module: present crosshairs for a fixed duration

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.title = 'Rest'
        self.output = None

event_types = {'RESPONSE':1, 
    'TASK_END':StimToolLib.TASK_END}
    
    
    
    
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/PS.Default.params', {})
    g.run_params.update(run_params)
    try:
        run_try()
        g.status = 0
    except StimToolLib.QuitException as q:
        g.status = -1
    StimToolLib.task_end(g)
    return g.status
        
def run_try():  
    
    myDlg = gui.Dlg(title="ParameterSelector")
    #question_lists = [f for f in os.listdir(os.path.join(os.path.dirname(__file__))) if f.endswith('.schedule')] 
    schedules = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.schedule')]
    if not g.session_params['auto_advance']:
        myDlg.addField('Question List', choices=schedules, initial=g.run_params['run'])
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
            thisInfo = myDlg.data
        else:
            print('QUIT!')
            return -1#the user hit cancel so exit 
        g.run_params['run'] = thisInfo[0]
    schedule_file = os.path.join(os.path.dirname(__file__), g.run_params['run'])
    g.clock = core.Clock()
    start_time = data.getDateStr()
    
    param_file = g.run_params['run'][0:-9] + '.params' #every .schedule file can (probably should) have a .params file associated with it to specify running parameters (including part of the output filename)
    StimToolLib.get_var_dict_from_file(os.path.join(os.path.dirname(__file__), param_file), g.run_params)
    
    print(param_file)
    g.prefix = StimToolLib.generate_prefix(g)
    fileName = os.path.join(g.prefix + '.csv')
    
    g.output= open(fileName, 'w')
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Parameter File:,' +  schedule_file + ",Event Codes:," + str(sorted_events) + '\n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
    StimToolLib.task_start(StimToolLib.PARAMETERSELECTOR_CODE, g) #send message that this task is starting
    
    instruct_onset = g.clock.getTime()
    
    options_dict = json.load(open(schedule_file, 'r'))
    
    myDlg = gui.Dlg(title='ParameterSelector')
    #options_dict = {}
    for this_key in options_dict.keys(): 
        options = options_dict[this_key].keys()
        #so they're in numeric order
        options = sorted(options)
        myDlg.addField(this_key, choices = options)


    myDlg.show()  # show dialog and wait for OK or Cancel
    if myDlg.OK:  # then the user pressed OK
        thisInfo = myDlg.data
    else:
        raise StimToolLib.QuitException()
 
    print(options_dict)
    print(g.session_params)
    for option,selection in zip(options_dict.keys(), thisInfo):
       this_selection = options_dict[option][selection]
       for k in this_selection.keys():
          g.session_params[k] = this_selection[k]
    print(thisInfo)
    print(g.session_params)


   #q_start = g.clock.getTime()
   #resp = get_one_response(l[0], l[1]=='True')
   #now = g.clock.getTime()
   #StimToolLib.mark_event(g.output, g.trial, 'NA', event_types['RESPONSE'], now, now - q_start, resp, l[0], g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        
    
    
    
    

  
 


