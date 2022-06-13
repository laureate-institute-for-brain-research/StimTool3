

import importlib.util
spec = importlib.util.spec_from_file_location("cv2", "C:\StimTool3Env\Lib\site-packages\cv2\cv2.cp36-win_amd64.pyd")
cv2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cv2)



import multiprocessing, os#, StimToolLib
import ctypes.wintypes
import psutil

import sys
sys.path.append('C:\StimTool3Env\Lib\site-packages')

#import cv2
    
cap = cv2.VideoCapture(0)
#set video to capture 1280x720instead of 640x480
cap.set(3, 1280)
cap.set(4, 720)

#cap.set(3, 1920)
#cap.set(4, 1080)

fourcc = 'XVID'
xsize = None
ysize = None
count = 0
while True:
    count = count + 1
    
    ret, frame = cap.read() #grab a frame from the camera
    if ret==True:
        xsize = frame.shape[1]
        ysize = frame.shape[0]
        cv2.imshow('frame',frame) #show the recently captured image
        # write the frame
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    #cv2.waitKey(1) #for some reason, you have to make this call or the video frame freezes and no recording takes place
# Release everything if job is finished
cap.release()
cv2.destroyAllWindows()
