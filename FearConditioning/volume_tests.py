
import os, random, operator
from psychopy import visual, core, event, data, gui, sound, prefs
prefs.general['audioLib'] = [u'pyo', u'pygame']
#prefs.general['audioLib'] = [u'pygame']
prefs.general[u'audioDriver'] = [u'ASIO4ALL', u'ASIO', u'Audigy']
#Stop signal task
    
scream = sound.Sound(value=os.path.join(os.path.dirname(__file__), 'media/Scream2sx3B.wav'))

for i in range(1,11):
    scream.setVolume(i * 0.1)
    scream.play()
    core.wait(10)
    
  
 


