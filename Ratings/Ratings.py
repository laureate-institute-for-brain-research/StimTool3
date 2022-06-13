from psychopy import prefs

import StimToolLib, os, random, operator, csv
from psychopy import visual, core, event, data, gui, sound

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.win = None #the window where everything is drawn
        self.clock = None #global clock used for timing
        self.x = None #+ fixation stimulus
        self.output = None #The output file
        self.msg = None
        
event_types={'VAS_RATING':1, 
    'POST_RATING':2,
    'AAC_RATING':3,
    'BMT_RATING':4,
    'TASK_END':StimToolLib.TASK_END}

def update_response_string(captured_string, captured_response):
    captured_response.setText(captured_string)
    captured_response.draw()
    g.win.flip()
    
def get_text_response(text_so_far, y_pos):
    captured_response = visual.TextStim(g.win, 
                        units='pix',height = 30,
                        pos=(-840, y_pos), text='',
                        alignHoriz = 'left',alignVert='top',
                        color='Blue', wrapWidth=int(1680))
    if text_so_far == None:
        captured_string = ''
    else:
        captured_string=text_so_far
    done=False
    g.win.flip()
    capital=False
    while True:
        for key in event.getKeys():
            #quit at any point
            if key in ['lshift','rshift']:
                capital=True
            elif key in ['escape']: 
                raise StimToolLib.QuitException()
            #if the participant hits return, save the string so far out 
            #and reset the string to zero length for the next trial
            elif key in ['return']:
                done = True
                return captured_string, done, captured_response
            #allow the participant to do deletions too , using the 
            # delete key, and show the change they made
            elif key in ['delete','backspace']:
                captured_string = captured_string[:-1] #delete last character
                update_response_string(captured_string, captured_response)
            #handle spaces and punctuation
            elif key in ['space']:
                captured_string = captured_string+' '
                update_response_string(captured_string, captured_response)
            elif key in ['period']:
                captured_string = captured_string+'.'
                update_response_string(captured_string, captured_response)
            elif key in ['comma']:
                captured_string = captured_string+','
                update_response_string(captured_string, captured_response)
            elif key in ['semicolon']:
                captured_string = captured_string+';'
                update_response_string(captured_string, captured_response)
            elif key in ['apostrophe']:
                captured_string = captured_string+"'"
                update_response_string(captured_string, captured_response)
            elif key in ['slash']:
                captured_string = captured_string+'/'
                update_response_string(captured_string, captured_response)
            elif key in ['backslash']:
                captured_string = captured_string+'\\'
                update_response_string(captured_string, captured_response)
            #if any other key is pressed, add it to the string and 
            # show the participant what they typed
            elif key in ['1','2','3','4','5','6','7','8','9','0','-','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']: 
                if capital:
                    captured_string=captured_string+key.upper()
                    capital=False
                else:
                    captured_string = captured_string+key
                #show it
                update_response_string(captured_string, captured_response)
            else:
                pass
        if g.mouse.getPressed()[0]:
            return captured_string, done, captured_response
   

def get_BMT_post_ratings(fileName):
    topText=visual.TextStim(g.win, text='Press Enter when you are done.', units='pix', pos=(0,480), wrapWidth=1680, height=30, color='Red')
    
    g.msg.setText('The following are questions about the Face Recognition task you completed in the scanner related to detecting the target faces. For each question, use the mouse to select the response that best describes your opinion regarding the task. Press enter to start.')
    #text = visual.TextStim(g.win, text=msg, units='norm', height=0.1, color='black', pos=[0,0], wrapWidth=int(1.5))
    g.mouse.setVisible(1)
    g.msg.draw()
    g.win.flip()
    event.waitKeys(keyList=["return"])
    g.win.flip()
    topText.setAutoDraw(True)
    questionA = visual.TextStim(g.win, text='', units='pix', alignHoriz='left', pos=(-840,400), wrapWidth=1680, height=30, color=[-1,-1,-1])
    questionB = visual.TextStim(g.win, text='', units='pix', alignHoriz='left', pos=(-840,0), wrapWidth=1680, height=30, color=[-1,-1,-1])
    response_labels = ('      1\nNot at all', '2\n', '    3\nA little', '4\n', '       5\nQuite a bit', '6\n', '        7\nVery much')
    scale_A = visual.RatingScale(g.win, lineColor='Black', precision=1, low=1, high=7,  marker=visual.TextStim(g.win, text='l', units='norm', color='red'),
        textColor='Black', scale=None, textSize=0.7,labels=response_labels,  pos=(0,0.4), showAccept=False, stretch=1.8, tickMarks=[1,2,3,4,5,6,7])
    questions={'1a':'1A. How difficult did you find this task?',
        '1b':'1B. Was there anything about the task that made it particularly easy or difficult? (Type your response in the space below)',
        '2a':'2A. How difficult was it for you to remember the target faces?',
        '2b':'2B. Was there anything about the task that made it particularly easy or difficult to remember the target faces? (Type your response in the space below)',
        '3':'3. In general what was your experience like with this task? (Type your response in the space below)',
        '4':'4. You indicated that you may have saw two faces during this task. Can you explain that a little more? (Type your response in the dialog below)',
        '5':'5. When you saw two faces were you able to distinguish the expression on the first face?'}
    questionA.setAutoDraw(True)
    questionB.setAutoDraw(True)
  
    for q in [1,2,3]:
        scale_A_rating=None
        scale_A.markerStart=None
        resp=None
        start=g.clock.getTime()
        if q==3:
            questionB.setAutoDraw(False)
            questionA.setText(questions[str(q)])
            g.win.flip()
            resp,done,captured_response = get_text_response(resp,300)
            end=g.clock.getTime()
            StimToolLib.mark_event(g.output, str(q), questions[str(q)], event_types['BMT_RATING'], end, end - start, resp, 'NA', False, g.session_params['parallel_port_address'])

        else:
            questionA.setText(questions[str(q)+'a'])
            questionB.setText(questions[str(q)+'b'])
            scale_A.reset()
            
            while True:
                if event.getKeys(["escape"]):
                    raise StimToolLib.QuitException()
                if event.getKeys(["return"]):
                    scale_A_rating=scale_A.getRating()    
                    break
                elif event.getKeys()!=[]:
                    scale_A.setAutoDraw(True)
                    scale_A_rating=scale_A.getRating()
                    resp,done,captured_response = get_text_response(resp,-75)
                    scale_A.setAutoDraw(False)
                    scale_A.reset()
                    scale_A.markerStart=scale_A_rating
                    
                    if done:
                        break
                if resp!=None:
                    captured_response.draw()
                scale_A.draw()
                g.win.flip()
            end=g.clock.getTime()
            StimToolLib.mark_event(g.output, str(q)+'A', questions[str(q)+'a'], event_types['BMT_RATING'], end, end - start, scale_A_rating, 'NA', False, g.session_params['parallel_port_address'])
            StimToolLib.mark_event(g.output, str(q)+'B', questions[str(q)+'b'], event_types['BMT_RATING'], end, end - start, resp, 'NA', False, g.session_params['parallel_port_address'])

            
    questionA.setAutoDraw(False)
    g.msg.setText('Please let the administrator know now that you have completed the ratings.')
    topText.setAutoDraw(False)
    g.msg.draw()
    g.win.flip()
    event.waitKeys('z')
    g.win.flip()
    
    g.output.close()
    
    myDlg=gui.Dlg(title="Review Responses",labelButtonOK=u' Yes ', labelButtonCancel=u' No ')
    myDlg.addField('Output File', fileName)
    myDlg.addText('Are additional questions required?')
    myDlg.show()  # show dialog and wait for OK or Cancel
    if myDlg.OK:  # then the user pressed OK
        #print 'Additional questions requested'
        while True:
            try:
                g.output = open(fileName, 'a')
                break
            except:
                myDlg=gui.Dlg(title="Review Responses")
                myDlg.addText('Please close the excel file before continuing.')
                myDlg.show() 
    else:
        #print 'QUIT!'
        while True:
            try:
                g.output = open(fileName, 'a')
                break
            except:
                myDlg=gui.Dlg(title="Review Responses")
                myDlg.addText('Please close the excel file before continuing.')
                myDlg.show()
        return -1#the user hit cancel so exit 
        
    #Question 4
    resp=None
    start=g.clock.getTime()
    questionA.setText(questions['4'])
    questionA.setAutoDraw(True)
    g.win.flip()
    done=False
    while not done:
        resp,done,captured_response = get_text_response(resp,300)
    end=g.clock.getTime()
    StimToolLib.mark_event(g.output, 4, questions['4'], event_types['BMT_RATING'], end, end - start, resp, 'NA', False, g.session_params['parallel_port_address'])
    
    #Question 5
    start=g.clock.getTime()
    questionA.setText(questions['5'])
    questionA.setAutoDraw(True)
    scale_A = visual.RatingScale(g.win, lineColor='Black', precision=1, low=1, high=2,  marker=visual.TextStim(g.win, text='l', units='norm', color='red'),
        textColor='Black', scale=None, textSize=0.7,labels=('YES','NO'),  pos=(0,0.4), showAccept=False, stretch=1.8, tickMarks=[1,2])  
        
    while True:
        scale_A.draw()
        g.win.flip()
        if event.getKeys(["escape"]):
            questionA.setAutoDraw(False)
            raise StimToolLib.QuitException()
        elif event.getKeys(["return"]):
            questionA.setAutoDraw(False)
            g.win.flip()
            break
    end=g.clock.getTime()
    StimToolLib.mark_event(g.output, 5, questions['5'], event_types['BMT_RATING'], end, end - start, scale_A.getRating(), 'NA', False, g.session_params['parallel_port_address'])
    topText.setAutoDraw(False)
    
    
   
def get_AAC_post_imratings(output_info):
    g.msg.setText('Next, please use the scales on the following screens to rate how pleasant/unpleasant and how aroused the presented images make you feel. Press enter to continue.')
    g.msg.setColor('Black')
    g.msg.draw()
    g.win.flip()
    event.waitKeys(keyList=['return'])
    g.msg.setText('Loading...')
    g.msg.draw()
    g.win.flip()
    images=[]
    count = 1
    for file in output_info:
        try:
            output_file=os.path.join(g.session_params['output_dir'],file)
            f=csv.reader(open(output_file), delimiter=',')
            for each_line in f:
                if each_line[2]=='8' or each_line[2]=='9':
                    images.append(visual.ImageStim(g.win, image=each_line[6].split(' ')[0], units='pix')) #load images into memory
            count += 1
        except (TypeError, IOError): #File not selected or does not exist
            #print 'No file for run.'
            pass
            
    
    valence_txt=visual.TextStim(g.win,text='PLEASANTNESS RATING:\n\t1 = unhappy, unsatisfied, bored\n\t5 = neutral, not pleased or displeased\n\t9 = happy, satisfied, content',
        alignHoriz='left', units='pix', height=25, color=[-1,-1,-1], pos=(-701,-79),wrapWidth=1000)
    arousal_txt=visual.TextStim(g.win,text='AROUSAL RATING:\n\t1 = relaxed, sluggish, sleepy\n\t5 = neutral, not very calm, not very excited\n\t9 = excited, jittery, wide awake',
        alignHoriz='left', units='pix', height=25, color=[-1,-1,-1], pos=(-701,-340),wrapWidth=1000)
    bottom_txt=visual.TextStim(g.win,text='PRESS ENTER WHEN YOU ARE DONE', units='pix', height=29, pos=(0,-482), color=[-1,-1,-1],wrapWidth=1000)
    valence_im=visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),'media','valence.png'), units='pix', pos=(316,-65))
    arousal_im=visual.ImageStim(g.win, image=os.path.join(os.path.dirname(__file__),'media','arousal.png'), units='pix', pos=(316,-330))
    scale_v = visual.RatingScale(g.win, lineColor='black', precision=1, size=1.15, marker=visual.TextStim(g.win, text='l', color='Red', height=0.07, units='norm'),
        low=1,high=9, markerStart=5, labels=['1','5','9'],textSize=0.4, textColor='Black', scale=None, showValue=False, pos=(0.325,-0.27), showAccept=False, acceptKeys='z')
    scale_a = visual.RatingScale(g.win, lineColor='black', precision=1, size=1.15, marker=visual.TextStim(g.win, text='l', height=0.07, color='Red', units='norm'),
        low=1,high=9, markerStart=5, labels=['1','5','9'], textSize=0.4, textColor='Black', scale=None, showValue=False, pos=(0.325,-0.70), showAccept=False, acceptKeys='z')
    trial_num=1
    count_txt=visual.TextStim(g.win,text=str(trial_num)+'/'+str(len(images)),
        alignHoriz='right', units='pix', height=25, color=[-1,-1,-1], pos=(900,440),wrapWidth=1000)
    for i in images:
        scale_v.reset()
        scale_a.reset()
        i.size = i.size * 0.5
        i.pos = (0,285)
        trial_start_time=g.clock.getTime()
        while True:
            if event.getKeys(["escape"]):
                raise StimToolLib.QuitException()
            if event.getKeys(["return"]):
                break
            i.draw()
            count_txt.draw()
            valence_txt.draw()
            arousal_txt.draw()
            bottom_txt.draw()
            valence_im.draw()
            arousal_im.draw()
            scale_v.draw()
            scale_a.draw()
            g.win.flip()
        now=g.clock.getTime()
        StimToolLib.mark_event(g.output, str(trial_num)+' (Valence)', i._imName, event_types['AAC_RATING'], now, now - trial_start_time, str(scale_v.getRating()), 'NA', False, g.session_params['parallel_port_address'])
        StimToolLib.mark_event(g.output, str(trial_num)+' (Arousal)', i._imName, event_types['AAC_RATING'], now, now - trial_start_time, str(scale_a.getRating()), 'NA', False, g.session_params['parallel_port_address'])
        trial_num+=1
        count_txt.setText(str(trial_num)+'/'+str(len(images)))    



def get_vas_ratings():
    g.mouse.setVisible(1)
    top_text = visual.TextStim(g.win, text="Please rate how you feel", units='norm', height=0.1, color='black', pos=[0,0.7], wrapWidth=int(1.5))
    
    text_1 = visual.TextStim(g.win, text="PLEASANT", units='norm', height=0.05, color='black', pos=[0,0.33], wrapWidth=int(1600))
    scale_1 = visual.RatingScale(g.win, lineColor='Black', marker=visual.TextStim(g.win, text='l', units='norm', color='black'), precision=1, low=0, 
        high=100, textColor='Black', markerStart=50, scale=None, labels=['not at all', 'extremely'], tickMarks=[0,100], showValue=False, pos=(0,0.4), showAccept=False, acceptKeys='z')
    
    text_2 = visual.TextStim(g.win, text="UNPLEASANT", units='norm', height=0.05, color='black', pos=[0,-0.07], wrapWidth=int(1600))
    scale_2 = visual.RatingScale(g.win, lineColor='Black', marker=visual.TextStim(g.win, text='l', units='norm', color='black'), precision=1, low=0, 
        high=100, textColor='Black', markerStart=50, scale=None, labels=['not at all', 'extremely'], tickMarks=[0,100], showValue=False, pos=(0,0), showAccept=False, acceptKeys='z')
    
    text_3 = visual.TextStim(g.win, text="INTENSE", units='norm', height=0.05, color='black', pos=[0,-0.47], wrapWidth=int(1600))
    scale_3 = visual.RatingScale(g.win, lineColor='Black', marker=visual.TextStim(g.win, text='l', units='norm', color='black'), precision=1, low=0, 
        high=100, textColor='Black', markerStart=50, scale=None, labels=['not at all', 'extremely'], tickMarks=[0,100], showValue=False, pos=(0,-0.4), showAccept=False, acceptKeys='z')
    bot_text = visual.TextStim(g.win, text="Press enter when done", units='pix', height=50, color='black', pos=[0,-450], wrapWidth=int(1600))
    vas_start_time = g.clock.getTime()
    while True:
        if event.getKeys(["escape"]):
            raise StimToolLib.QuitException()
        if event.getKeys(["return"]):
            break
        #item.draw()
        text_1.draw()
        text_2.draw()
        text_3.draw()
        scale_1.draw()
        scale_2.draw()
        scale_3.draw()
        top_text.draw()
        bot_text.draw()
        g.win.flip()
    now = g.clock.getTime()
    StimToolLib.mark_event(g.output, -1, 'NA', event_types['VAS_RATING'], now, now - vas_start_time, str(scale_1.getRating()), 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, -2, 'NA', event_types['VAS_RATING'], now, now - vas_start_time, str(scale_2.getRating()), 'NA', False, g.session_params['parallel_port_address'])
    StimToolLib.mark_event(g.output, -3, 'NA', event_types['VAS_RATING'], now, now - vas_start_time, str(scale_3.getRating()), 'NA', False, g.session_params['parallel_port_address'])
    g.mouse.setVisible(0)
    
    
def get_AAC_post_ratings():
    
    g.msg.setText('The following are questions about the Runway task you completed in the scanner related to gaining points and/or seeing negative or neutral pictures. For each question, use the mouse to select the response that best describes your opinion regarding the task. Press enter to start.')
    #text = visual.TextStim(g.win, text=msg, units='norm', height=0.1, color='black', pos=[0,0], wrapWidth=int(1.5))
    g.mouse.setVisible(1)
    g.msg.draw()
    g.win.flip()
    event.waitKeys(keyList=["return"])
    g.win.flip()
    response_labels = ('      1\nNot at all', '2\n', '    3\nA little', '4\n', '       5\nQuite a bit', '6\n', '        7\nVery much')
    questions = open(os.path.join(os.path.dirname(__file__),'T1000_AAC_PostQuestions.csv'))
    i = -1 #index of current question
    for line in questions:
        resp,end_time,resp_time = StimToolLib.get_one_rating(line, response_labels, g.win, g.clock)
        StimToolLib.mark_event(g.output, i, 'NA', event_types['POST_RATING'], end_time, resp_time, resp, line.rstrip(), g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
        i = i - 1
    if int(resp) > 1:
        resp,end_time,resp_time = StimToolLib.get_text_response('Please describe (type) any other strategies used to manage emotions triggered by negative pictures.  Press enter when done.', g.win, g.clock)
        StimToolLib.mark_event(g.output, i, 'NA', event_types['POST_RATING'], end_time, resp_time, resp, 'NA', g.session_params['signal_parallel'], g.session_params['parallel_port_address'])
    #r = StimToolLib.get_one_rating("When a NEGATIVE picture and sound were displayed, I tried to think about something unrelateed to the picture to distract myself:", response_labels, g.win)
   
  
def run(session_params, run_params):
    global g
    g = GlobalVars()
    g.session_params = session_params
    g.run_params = StimToolLib.get_var_dict_from_file(os.path.dirname(__file__) + '/PR.Default.params', {})
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
        myDlg = gui.Dlg(title="PR")
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
    subj_param_file = os.path.join(os.path.dirname(g.prefix), g.session_params['SID'] + '_' + g.run_params['param_file'])
    
    
    if g.run_params['stage']=='postMRI':
        AAC_run_id=g.run_params['AAC_run_id']
        myDlg=gui.Dlg(title="Select AAC Runs")
        
        for version in ['A','B','C']:
            #choices=[os.path.join(g.session_params['output_dir'],f) for f in os.listdir(g.session_params['output_dir']) if f.startswith(g.session_params['SID']+'-'+g.session_params['anxdep']+AAC_run_id+version)]
            choices=[os.path.join(g.session_params['output_dir'],f) for f in os.listdir(g.session_params['output_dir']) if f.startswith(g.session_params['SID']) and (AAC_run_id+version) in f]
            choices_wstats=[[f,os.stat(f).st_ctime,os.stat(f).st_size] for f in choices]
            choices_sorted = sorted(choices_wstats, key=operator.itemgetter(1), reverse=True)
            choices_sorted.append(['None','None','None'])
            mat=list(zip(*choices_sorted))
            myDlg.addField('Run '+version, choices=mat[0])
        
        myDlg.show()  # show dialog and wait for OK or Cancel
        if myDlg.OK:  # then the user pressed OK
                output_info = myDlg.data
        else:
            #print 'QUIT!'
            return -1#the user hit cancel so exit 
        
  
    StimToolLib.general_setup(g)
    
    start_time = data.getDateStr()
    #g.prefix = 'AAC-' + g.session_params['SID'] + '-Admin_' + g.session_params['raID'] + '-run_' + str(g.run_params['run']) + '-' + start_time
    fileName = os.path.join(g.prefix +'.csv')
    g.output = open(fileName, 'w')
    sorted_events = sorted(event_types.items(), key=lambda item: item[1])
    g.output.write('Administrator:,' + g.session_params['admin_id'] + ',Original File Name:,' + fileName + ',Time:,' + start_time + ',Schedule File:,' +  schedule_file + ',Post-question file:,T1000_AAC_PostQuestions.csv,Event Codes:,' + str(sorted_events) + ', For ratings the trial number is negative and used to identify the question being rated.  VAS ratings are in the order pleasant-unpleasant-intense and are from 0 (not at all) to 100 (very much) \n')
    g.output.write('trial_number,trial_type,event_code,absolute_time,response_time,response,result\n')
   
    g.mouse.setVisible(True)
    g.win.setColor([1,1,1])
    g.msg.setColor([-1,-1,-1])
    g.win.flip()
    
    if g.run_params['stage']=='preMRI' or g.run_params['stage']=='preBEH' or g.run_params['stage']=='postBEH':
        get_vas_ratings()
        #print 'is this happening'
        
    elif g.run_params['stage']=='postMRI':
        get_vas_ratings()
        get_AAC_post_ratings() 
        get_AAC_post_imratings(output_info) 