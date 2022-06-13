
from multiprocessing import Process, Queue
#from Queue import Empty
import numpy as np
import multiprocessing, os#, StimToolLib
import ctypes.wintypes
import psutil
from psychopy import core, microphone

#the version of cv2 distributed with psychopy3 at the moment (found here: C:\StimTool3Env\Lib\site-packages\cv2\cv2.cp36-win_amd64.pyd)
#does not work well with some webcams--with some resolutions it will leave black bars on the sides of the video.
#importing this version fixes that problem
import importlib.util
spec = importlib.util.spec_from_file_location("cv2", "C:\StimTool3Env\Lib\site-packages\cv2\cv2.cp36-win_amd64.pyd")
cv2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cv2)

from pyo import Server, Record, Input, Clean_objects, SfPlayer, serverCreated, serverBooted
import subprocess
import sys
sys.path.append('C:\StimTool3Env\Lib\site-packages')
import pyaudio
import wave

class GlobalVars:
    #This class will contain all module specific global variables
    #This way, all of the variables that need to be accessed in several functions don't need to be passed in as parameters
    #It also avoids needing to declare every global variable global at the beginning of every function that wants to use it
    def __init__(self):
        self.q = None
        self.recorder = None
        self.q_video_in = Queue() #initialize so there is always a Queue available--whether or not recording is taking place
        self.q_audio_in = Queue()
        
        self.q_video_out = Queue() # used to communicate from audio/video processes to mux process after completion
        self.q_audio_out = Queue()
        self.capturing = False #keep track of whether or not there are child processes capturing audio/video
        #microphone.switchOn(outputDevice='junk')
        #self.mic = microphone.AdvAudioCapture() #initialize microphone
global g
#g=GlobalVars()
def start_camera():
    #will start capturing video from the camera--but will not start to record until start_recording has been called
    global g
    g = GlobalVars()
    #g.recorder = Process(target = camera_capture_process, args = (g.q,))
    print(os.getpid())
    
    
    g.recorder_audio = Process(target = audio_capture_process, args = (g.q_audio_in, g.q_audio_out, os.getpid())) #give the audio process this pid, so it can quit if this one is killed
    g.recorder_audio.start()
        
    g.recorder_video = Process(target = camera_capture_process, args = (g.q_video_in, g.q_video_out, os.getpid())) #give the camera process this pid, so it can quit if this one is killed
    g.recorder_video.start()

    

    g.mux_process = Process(target = av_mux_process, args = (g.q_video_out, g.q_audio_out, os.getpid())) #give the audio process this pid, so it can quit if this one is killed
    g.mux_process.start()
    
    
def camera_capture_process(q_in, q_out, parent_pid):
    sys.stdout = open("cameracap.out", "w")#for debugging
    print('stdout made', flush = True)
    print(os.getpid())
    print(q_in, flush = True)
    print(q_out, flush = True)
    cap = cv2.VideoCapture(0)
    #set video to capture 1280x720instead of 640x480
    cap.set(3, 1280)
    cap.set(4, 720)
	
    #cap.set(3, 1920)
    #cap.set(4, 1080)
	
    recording = False
    #clock = core.Clock()
    fourcc = 'XVID'
    video_writer = cv2.VideoWriter_fourcc(*fourcc)
    xsize = None
    ysize = None
    count = 0
    while True:
        count = count + 1
        if count % 30 == 0: #~once a second, check to see if the parent process is alive.  If not, release the camera and quit.
            #print('checking PID', flush = True)
            if not psutil.pid_exists(parent_pid):
                if recording:
                    video_out.release()
                    time_stamp_out.close()
                    fps = fnumber / (clock.getTime() - start_time)
                    #print(fps)
                    q_out.put(fps)
                break
        if xsize: #don't check the Queue until after the camera is returning frames
            if not q_in.empty(): #see if there's a start/stop command and process it if there is one
                args = q_in.get(False)
                command = args[0] #this will either be quit, stop, or a file prefix
                print(command, flush = True)
                if command == 'quit': 
                    if recording:
                        StimToolLib.error_popup('CALLED QUIT WHEN RECORDING VIDEO: CALL STOP FIRST') #will raise an exception--only happens if the camera is on
                    break
                elif command == 'stop':
                    if not recording:
                        continue #this is probably OK--you can always tell the camera to stop recording, even if it's not already->it just continues not recording
                        #StimToolLib.error_popup('CALLED STOP WHEN NOT RECORDING VIDEO') #will raise an exception--only happens if the camera is on
                    recording = False
                    video_out.release()
                    time_stamp_out.close()
                    fps = fnumber / (clock.getTime() - start_time)
                    #print(fps)
                    q_out.put(fps)
                else:
                    recording = True
                    video_out = cv2.VideoWriter(command + '.avi', video_writer, 30, (xsize,ysize), True) #30 is approx fps--this will be used when playing back video, but actual frame time stamps are avaialble in .VTS file
                    time_stamp_out = open(command + '.VTS', 'w') #video time stamp
                    time_stamp_out.write('Frame_number Time_Stamp\n')
                    clock = args[1]
                    fnumber = 0
                    #in case the first frame is not at time 0, to get FPS
                    start_time = clock.getTime()
        ret, frame = cap.read() #grab a frame from the camera
        if ret==True:
            xsize = frame.shape[1]
            ysize = frame.shape[0]
            cv2.imshow('frame',frame) #show the recently captured image
            # write the frame
            if recording: #only write if currently recording
                video_out.write(frame)
                time_stamp_out.write(str(fnumber) + ' ' + str(clock.getTime()) + '\n')
                fnumber = fnumber + 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #cv2.waitKey(1) #for some reason, you have to make this call or the video frame freezes and no recording takes place
    # Release everything if job is finished
    cap.release()
    cv2.destroyAllWindows()
    q_out.put('quit')
       

def audio_capture_process(q_in, q_out, parent_pid):
    sys.stdout = open("audiocap.out", "w")#for debugging
    print('stdout made', flush = True)
    print(os.getpid(), flush = True)
    print(q_in, flush = True)
    print(q_out, flush = True)
    rate = 44100
    frames_per_buffer = 1024
    channels = 2
    format = pyaudio.paInt16
    audio = pyaudio.PyAudio()
    stream = audio.open(format=format,
                                      channels=channels,
                                      rate=rate,
                                      input=True,
                                      frames_per_buffer = frames_per_buffer)
    count = 0
    recording = False
    print('starting stream', flush = True)
    stream.start_stream()
    print('started stream', flush = True)
    while True:
        ##testing
        #if count > 100:
        #    q_in.put(['stop', None])
        #    q_in.put(['quit', None])
        ##testing
        #try getting data first
        try:
            data = stream.read(frames_per_buffer) 
        except Exception as e:
            print(e)
            #sometimes stream.read() throws:
            #[Errno -9999] Unanticipated host error
            #followed by:
            #[Errno -9988] Stream closed
            #so try restarting the stream
            print('restarting stream')
            try:
                audio = pyaudio.PyAudio()
                stream = audio.open(format=format,
                                      channels=channels,
                                      rate=rate,
                                      input=True,
                                      frames_per_buffer = frames_per_buffer)
                stream.start_stream()
            except Exception as e2:
                print(e2)
            continue
            #if there was a problem getting data, don't process any other commands until the stream is working again
        #print('got data', flush = True)
        if recording:
            audio_frames.append(data)
        
        
        
        count = count + 1
        #print(count)
        if count % 3000 == 0: #~once a second, check to see if the parent process is alive.  If not, release the camera and quit.
            #this doesn't seem to work when running through the PsychoPy3 Experiment Runner--probaby because StimTool.py isn't the parent process, but some other python 'runner' thread is, 
            #and that stays open until all children have closed
            #print(count)
            #print(psutil.pid_exists(parent_pid))
            #print('checking PID', flush = True)
            if not psutil.pid_exists(parent_pid):
                if recording:
                    stream.stop_stream()
                    waveFile = wave.open(audio_filename, 'wb')
                    waveFile.setnchannels(channels)
                    waveFile.setsampwidth(audio.get_sample_size(format))
                    waveFile.setframerate(rate)
                    waveFile.writeframes(b''.join(audio_frames))
                    waveFile.close()
                    #stream.stop_stream()
                    q_out.put(audio_filename[0:-4])
                break
        if not q_in.empty(): #see if there's a start/stop command and process it if there is one
            args = q_in.get(False)
            command = args[0] #this will either be quit, stop, or a file prefix
            print(command, flush = True)
            if command == 'quit': 
                if recording:
                    StimToolLib.error_popup('CALLED QUIT WHEN RECORDING AUDIO: CALL STOP FIRST') #will raise an exception--only happens if the camera is on
                break
            elif command == 'stop':
                if not recording:
                    continue #this is probably OK--you can always tell the camera to stop recording, even if it's not already->it just continues not recording
                    #StimToolLib.error_popup('CALLED STOP WHEN NOT RECORDING VIDEO') #will raise an exception--only happens if the camera is on
                recording = False
                waveFile = wave.open(audio_filename, 'wb')
                waveFile.setnchannels(channels)
                waveFile.setsampwidth(audio.get_sample_size(format))
                waveFile.setframerate(rate)
                waveFile.writeframes(b''.join(audio_frames))
                waveFile.close()
                #stream.stop_stream()
                print('sending: ' + audio_filename[0:-4])
                q_out.put(audio_filename[0:-4])
            else:
                recording = True
                #empty out audio_frames for this audio recording
                audio_frames = []
                # Audio starts being recorded
                
                audio_filename = command + ".wav"
                    
        #if recording: #only poll if currently recording
        #print('getting data', flush = True)
    # Release everything if job is finished
    audio.terminate()
    print('sending: quit')
    q_out.put('quit')



def av_mux_process(q_fromvideo, q_fromaudio, parent_pid):
    #this process waits until both audio and video processes have finished, then re-encodes the video to the accurate FPS and combines
    #both audio and video files 
    sys.stdout = open("muxcap.out", "w")#for debugging
    print('stdout made', flush = True)
    print(os.getpid(), flush = True)
    print(q_fromvideo, flush = True)
    print(q_fromaudio, flush = True)
    while(True):
        core.wait(1)
        #if not q_fromvideo.empty():
        #    fps = q_fromvideo.get()
        #    print('from video', flush = True)
        #    print(fps, flush = True)
        #    fps = q_fromvideo.put(fps)
        #if not q_fromaudio.empty():
        #    prefix= q_fromaudio.get()
        #    print('from audio', flush = True)
        #    print(prefix, flush = True)
        #    q_fromaudio.put(prefix)
        if not q_fromvideo.empty() and not q_fromaudio.empty():
            #get fps from video thread and file prefix from audio thread
            fps = q_fromvideo.get()
            prefix = q_fromaudio.get()
            print('from video', flush = True)
            print(fps, flush = True)
            print('from audio', flush = True)
            print(prefix, flush = True)
            if fps == 'quit' and prefix == 'quit':
                #both will send 'quit' to kill this process
                print('exiting here')
                break
            print("Re-encoding")
            #cmd = "C:\\StimTool3Env\\ffmpeg-20200831-4a11a6f-win64-static\\bin\\ffmpeg -r " + str(fps) + " -i " + prefix + ".avi -pix_fmt yuv420p " + prefix + "-recoded.avi"
            #-itsscale means scale the input timeseries, -codec copy just copies the input frames
            #the input FPS metadata says the video was recorded at 30fps, but this is not accurate (depending on the camera, conditions, etc.)
            #so what we are doing here is setting the metadata FPS to the actual FPS recorded before combining with the audio data
            #-y to force overwrite, so the test video doesn't cause any problems
            cmd = "C:\\StimTool3Env\\ffmpeg-20200831-4a11a6f-win64-static\\bin\\ffmpeg -y -r " + str(fps) + " -itsscale " + str(30/fps) + " -i " + prefix + ".avi -pix_fmt yuv420p -codec copy " + prefix + "-recoded.avi"
            print(cmd, flush = True)
            subprocess.call(cmd, shell=True)
    
            print("Muxing")
            cmd = "C:\\StimTool3Env\\ffmpeg-20200831-4a11a6f-win64-static\\bin\\ffmpeg -y -ac 2 -channel_layout stereo -i " + prefix + ".wav -i " + prefix + "-recoded.avi -pix_fmt yuv420p -codec copy " + prefix + "-combined.avi"
            print(cmd, flush = True)
            subprocess.call(cmd, shell=True)
    
            #remove -recoded.avi to save space
            os.remove(prefix + "-recoded.avi")
        #print('checking PID')
        if not psutil.pid_exists(parent_pid):
            print('quitting there')
            break





def start_recording(prefix, clock):
    #starts recording video frames
    #video will be stored in prefix.avi, frame/time stamps will be stored in prefix.ts
    #will cause an error if the process is already recording
    g.q_video_in.put([prefix, clock])
    g.q_audio_in.put([prefix, clock])
    
def stop_recording():
    #stops recording and closes files
    #will cause an error if not already recording
    g.q_video_in.put(['stop', None])
    g.q_audio_in.put(['stop', None])
    
def stop_capture():
    if not g.capturing:
        return
    g.q_video_in.put(['quit', None])
    g.q_audio_in.put(['quit', None])
    #wait for children to exit--so that we don't try to move files while muxing is still happening
    while not(g.q_video_in.empty() and g.q_audio_in.empty() and g.q_video_out.empty() and g.q_audio_out.empty()):
        core.wait(1)
    #in case this gets called twice, we don't want to hang forever (since the recorders will already be dead)
    g.capturing = False

def test_camera():
    #test to make sure there is a camera process running
    #tell it to start then stop recording, and see if it empties out the Queue
    
    start_recording('test', core.Clock())
    #g.q_video_in.put(['test', core.Clock()])
    #g.q_video_in.put(['stop', None])
    stop_recording()
    #g.q_audio_in.put(['test', core.Clock()])
    #g.q_audio_in.put(['stop', None])
    
    print('video in')
    print(g.q_video_in)
    
    print('audio in')
    print(g.q_audio_in)
    
    for i in range(600): #wait up to 60 seconds--checking every 100ms, then give up
        core.wait(0.100)
        if g.q_video_in.empty() and g.q_audio_in.empty():
            print('camera started after:' + str(i/10) + ' seconds')
            return True
    
    
    return False
    
def start_and_test_camera():
    #start the camera, then test to see if it's working
    start_camera()
    g.capturing = True
    return test_camera()



if __name__ == '__main__':
    
    #g = GlobalVars()
    clock = core.Clock()
    #g.q_audio.put(['audio1', clock])
    #audio_capture_process(g.q_audio, os.getpid())
    ##TESTING
    #global g
    #g = GlobalVars()
    #g.q_audio_in.put(['test', clock])
    #g.q_audio_in.put(['stop', None])

    #g.q_audio_in.put(['quit', None])
    #audio_capture_process(g.q_audio_in, g.q_audio_out, os.getpid())
    #quit()
    ##TESTING
    
    print(start_and_test_camera())
    #start_camera()
    #start_recording('fileA', clock)
    #camera_capture_process(g.q_video_in, g.q_video_out, os.getpid())
    clock.reset()
    start_recording('fileA', clock)
    print('here')
    core.wait(2)
    print('stopping')
    stop_recording()
    print('stopped')
    #clock.reset()
    #start_recording('fileB', clock)
    #core.wait(10)
    #stop_recording()
    core.wait(2)
    start_recording('fileB', clock)
    print('started')
    core.wait(2)
    stop_recording()
    print('stopped 2')
    stop_capture()
    #g.recorder.join()
    core.wait(10) #wait for the audio file to be written
   
  
 
 

