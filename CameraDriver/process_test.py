from  Queue import Empty
from multiprocessing import Process, Queue
import numpy as np
import cv2, multiprocessing
from psychopy import core

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.q = None
        self.recorder = None
g = GlobalVars

def start_camera():
    #will start capturing video from the camera--but will not start to record until start_recording has been called
    global g
    g.q = Queue()
    #g.recorder = Process(target = camera_capture_process, args = (g.q,)) #give the camera 
    g.recorder = Process(target = camera_capture_process, args = (g.q,os.getpid(),)) #give the camera process this pid, so it can quit if this one is killed
    g.recorder.start()
    
def camera_capture_process(q, parent_pid):
    cap = cv2.VideoCapture(0)
    recording = False
    clock = None
    fourcc = cv2.cv.CV_FOURCC(*'XVID')
    while True:
        try: #see if there's a start/stop command and process it if there is one
            args = q.get(False)
            command = args[0] #this will either be quit, stop, or a file prefix
            if command == 'quit': 
                if recording:
                    StimToolLib.ErrorPopup('CALLED QUIT WHEN RECORDING VIDEO: CALL STOP FIRST') #will raise an exception
                break
            elif command == 'stop':
                if not recording:
                    StimToolLib.ErrorPopup('CALLED STOP WHEN NOT RECORDING VIDEO') #will raise an exception
                recording = False
                out.release()
                break
            else:
                recording = True
                out = cv2.VideoWriter(command + '.avi', fourcc, 20.0, (640,480), True)
                clock = args[1]
        except Empty: #happens when there isn't a new command waiting
            pass
        ret, frame = cap.read() #grab a frame from the camera
        if ret==True:
            cv2.imshow('frame',frame) #show the recently captured image
            # write the frame
            if recording: #only write if currently recording
                out.write(frame)
        cv2.waitKey(1) #for some reason, you have to make this call or the video frame freezes and no recording takes place

    # Release everything if job is finished
    cap.release()
    cv2.destroyAllWindows()
       
def start_recording(prefix, clock):
    #starts recording video frames
    #video will be stored in prefix.avi, frame/time stamps will be stored in prefix.ts
    #will cause an error if the process is already recording
    g.q.put([prefix, clock])
    
def stop_recording():
    #stops recording and closes files
    #will cause an error if not already recording
    g.q.put(['stop', None])    
    
def stop_capture():
    g.q.put(['quit', None])
    g.recorder.join()
    
if __name__ == '__main__':
    global g
    start_camera()
    clock = core.Clock()
    core.wait(2)
    start_recording('fileA', clock)
    core.wait(5)
    stop_recording()
    clock.reset()
    start_recording('fileB', clock)
    core.wait(10)
    stop_recording()
    
    stop_capture()    
   
  
 #import numpy as np
#import cv2, multiprocessing

#cap = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object
#fourcc = cv2.cv.CV_FOURCC(*'CVID') #cv2.VideoWriter_fourcc(*'XVID')
#fourcc = cv2.cv.CV_FOURCC(*'XVID') #cv2.VideoWriter_fourcc(*'XVID')
#out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480), True)

#while(cap.isOpened()):
#    ret, frame = cap.read()
#    if ret==True:
        # write the flipped frame
#        out.write(frame)

#        cv2.imshow('frame',frame)
#        if cv2.waitKey(1) & 0xFF == ord('q'):
#            break

# Release everything if job is finished
#cap.release()
#out.release()
#cv2.destroyAllWindows()
 