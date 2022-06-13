# Make Schedules for NCAIR


import glob, random, shutil


### Output Format
#TT,None,duration,media_path


def get_iti(mean, sd = .5):
    """
    Returns ITI with mean and standard deviation
    """
    return random.gauss( mean, sd)

def get_run(media_paths, run_name, ttype):
    """
    Generate Runs
    """
    audio_files = glob.glob(media_paths)
    audio_paths = []
    for audio_path in audio_files:
        #print audio_path
        audio_paths.append(audio_path.replace('C:/StimTool3/Ncair/', ''))

    
    random.shuffle(audio_paths)

    run1_file = open(run_name, 'w')
    # writ header
    output_lines = ['TrialTypes X_X X[0] -> Cultural|Comparator (0|1); 1 -> Cultural X[1]:Stimuli Type 0-> Audio;1-> Video; 2-> Picture,Durations,stim_path\n']
    for ap in audio_paths:
        print ap
        output_lines.append('%s,,%f,%s\n' % ( ttype,get_iti(2), ap))
    run1_file.writelines(output_lines)
    run1_file.close()

    # COPY for LEFT version
    shutil.copyfile(run_name, run_name.replace('_RIGHT.schedule','_LEFT.schedule'))




def get_first_four_runs():
    """
    Get fisrt for RUns
    """
    get_run('C:/StimTool3/Ncair/media/cultural_audio/cultural/*.mp3','NCAIR_R1_RIGHT.schedule', '0_0' )
    get_run('C:/StimTool3/Ncair/media/cultural_audio/comparator/*.mp3','NCAIR_R2_RIGHT.schedule', '1_0')
    get_run('C:/StimTool3/Ncair/media/cultural_videos/cultural/*.mp4','NCAIR_R3_RIGHT.schedule', '0_1' )
    get_run('C:/StimTool3/Ncair/media/cultural_videos/comparator/*.mp4','NCAIR_R4_RIGHT.schedule', '1_1')

def get_picture_run():
    """
    Run The Last Runs (picture)
    """
    cultural_pictures = glob.glob('C:\stimtool3\Ncair\media\cultural_pictures\*.jpg')
    comparator_pictures = glob.glob('C:\stimtool3\Ncair\media\\neutral_pictures\*.jpg')

    print 'cultural pics', len(cultural_pictures)
    print 'comparator pics',len(comparator_pictures)

    file_path_order = []

    # Randomly select cultural or comparator image file path
    available_cultural = len(cultural_pictures) != 0
    available_comparator = len(comparator_pictures) != 0

    run_file = open('NCAIR_R5_RIGHT.schedule', 'w')
    output_lines = ['TrialTypes X_X X[0] -> Cultural|Comparator (0|1); 1 -> Cultural X[1]:Stimuli Type 0-> Audio;1-> Video; 2-> Picture,Durations,stim_path\n']

    
    # Keep Looping until either cultural has been selected
    count = 0 # Use this to keep track of the index image. 
    # When it's at 0, take image from cultural
    # When it's at 1, take image from comparator

    while (available_cultural or available_comparator):
        print count

        #print 'cultural pics', len(cultural_pictures)
        #print 'comparator pics',len(comparator_pictures)


        if (len(cultural_pictures) == 0) and (count % 2 == 0): count += 1
        if (len(comparator_pictures) == 0) and (count % 2 == 1): count +=1
        if (count % 2 == 0):
            # Get append image from cultural
            current_image = random.choice(cultural_pictures)
            output_lines.append('%s,,%f,%s\n' % ( '0_2',get_iti(2), current_image.replace('C:\stimtool3\Ncair\\','')))

            cultural_pictures.remove(current_image)
        else:
            current_image = random.choice(comparator_pictures)
            output_lines.append('%s,,%f,%s\n' % ( '1_2',get_iti(2), current_image.replace('C:\stimtool3\Ncair\\','')))

            comparator_pictures.remove(current_image)
        
        available_cultural = len(cultural_pictures) != 0
        available_comparator = len(comparator_pictures) != 0
        count += 1
    
    run_file.writelines(output_lines)
    run_file.close()

    # copy the same output for left side
    shutil.copyfile('NCAIR_R5_RIGHT.schedule', 'NCAIR_R5_LEFT.schedule')


    

if __name__ == '__main__':
    get_first_four_runs()
    get_picture_run()
    