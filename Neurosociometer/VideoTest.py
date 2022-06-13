from psychopy import visual, core, event


win = visual.Window([1024,768])
mov = visual.MovieStim3(win, 'Videos/On.mp4', size=[1024,768],
                       flipVert=False, flipHoriz=False, loop=True)
                       
#mov = visual.MovieStim3(win, 'Videos/jwpIntro.mov', size=[320,240],
#                       flipVert=False, flipHoriz=False, loop=True)
                       
#print 'orig movie size=[%i,%i]' %(mov.format.width, mov.format.height)
#print 'duration=%.2fs' %(mov.duration)
globalClock = core.Clock()

while mov.status != visual.FINISHED:
    mov.draw()
    win.flip()
    for key in event.getKeys():
        if key in ['escape','q']:
            win.close()
            core.quit()

core.quit()