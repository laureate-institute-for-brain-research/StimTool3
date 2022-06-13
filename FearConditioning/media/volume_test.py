
from psychopy import event, core, visual, gui, sound, prefs
import csv, os, ctypes, ast, numpy
from shutil import move
prefs.general['audioLib'] = [u'pyo', u'pygame']
prefs.general[u'audioDriver'] = [u'ASIO4ALL', u'ASIO', u'Audigy']
    
    
s = sound.Sound('Scream2sx3B.wav')
possible_options = ['0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1']
#c = possible_options[int(start_volume * 10):] #don't let the user pick a volume less than the starting volume
last_volume = str(0)
while True:
    myDlg = gui.Dlg(title="Volume Test")
    myDlg.addText('Adjust the volume so you can comfortably hear the sound.  Press OK to play the sound and change "choice" to "accept" once you have found a volume you like.')
    myDlg.addField('Volume', choices=possible_options, initial=last_volume)
    myDlg.addField('Choice', choices=['play', 'accept'], initial='no')
    myDlg.show()  # show dialog and wait for OK or Cancel
    thisInfo = myDlg.data
    if myDlg.OK:  # then the user pressed OK
        last_volume = thisInfo[0]
        if thisInfo[1] == 'accept':
            break
        s.setVolume(float(last_volume))
        s.play()
    else:
        break