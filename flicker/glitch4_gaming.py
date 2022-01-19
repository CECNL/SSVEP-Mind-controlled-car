from psychopy import visual, core, event # import some libraries from PsychoPy
import numpy as np
import time as T
import random
from pylsl import StreamInfo, StreamOutlet
#create a window
mywin = visual.Window([1000,1300],pos=[2600,500], monitor="testMonitor", units="pix",color=[-1, -1, -1])
print(mywin.getActualFrameRate())



list_freqs = [11,12,13,14]
num_freqs = len(list_freqs)
fs = 60
up_height = 150
image_width = 120



all_flicker = []
for freq_i in range(num_freqs):
    stim_freq = list_freqs[freq_i]  
    num_smpls = np.lcm.reduce([fs , stim_freq])
    tidx = np.arange(1,num_smpls+1)
    # Sin and Cos
    flicker = 0.30*(1+np.sin(2*np.pi*stim_freq*(tidx /fs)))
    all_flicker.extend([flicker])


lcm_number = np.lcm.reduce([len(all_flicker[0]),
                            len(all_flicker[1]),
                            len(all_flicker[2]),
                            len(all_flicker[3])])

print("lcm_length:",lcm_number)

all_HZ = np.array([np.tile(all_flicker[0],int(lcm_number/len(all_flicker[0]))),
                   np.tile(all_flicker[1],int(lcm_number/len(all_flicker[1]))),
                   np.tile(all_flicker[2],int(lcm_number/len(all_flicker[2]))),
                   np.tile(all_flicker[3],int(lcm_number/len(all_flicker[3])))
                    ])


framerate = mywin.getActualFrameRate()


grey_box = visual.Rect(win=mywin, name='grey_box',units='pix', width=image_width, height=image_width,pos=[0,0+ up_height],
                            fillColor='grey',lineColor='grey',opacity=1)


HZ_block = [visual.Rect(win=mywin, name='HZ12_block',units='pix', width=image_width, height=image_width,pos=[0 ,350+ up_height],fillColor='white',opacity=1),
            visual.Rect(win=mywin, name='HZ15_block',units='pix', width=image_width, height=image_width,pos=[-350,0+ up_height],fillColor='white',opacity=1),
            visual.Rect(win=mywin, name='HZ10_block',units='pix', width=image_width, height=image_width,pos=[350,0+ up_height],fillColor='white',opacity=1),
            visual.Rect(win=mywin, name='HZ8_block',units='pix', width=image_width, height=image_width,pos=[0,-350+ up_height],fillColor='white',opacity=1)]


T.sleep(5)



i = 0 
time = 0
start = T.time()

while(1):


    now = T.time()
    grey_box.draw()


    for ID in range(len(HZ_block)):
        HZ_block[ID].opacity = all_HZ[ID][i]
        HZ_block[ID].draw()

        
    mywin.flip()


    i = i + 1
    if i >= lcm_number:
        i = 0 
        time =  0
        start = T.time() 


    if (time + i) % 100 == 99:
        
        print("time frame rate accuracy: ",(now - start)/((time + i)/fs))   


mywin.flip()  
mywin.close()
core.quit()