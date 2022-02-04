from psychopy import visual, core, event # import some libraries from PsychoPy
import numpy as np
import time as T
import random
from pylsl import StreamInfo, StreamOutlet
#create a window ,pos=[800,image_width]
# mywin = visual.Window([1000,1325],pos=[2600,500], monitor="testMonitor", units="pix",color=[-1, -1, -1])
mywin = visual.Window([1650*0.7,1230*0.7],pos=[60*0.7,10] ,monitor="testMonitor", units="pix",color=[-1, -1, -1])
print(mywin.getActualFrameRate())


list_freqs = [11, 12, 13, 14]
num_freqs = len(list_freqs)
fs = 60
up_height = 50
image_width = 80
num_smpls = fs * 60 * 10  ## fs* second* minute

all_HZ = np.zeros((0,num_smpls))

for freq_i in range(num_freqs):
    stim_freq = list_freqs[freq_i]  #in HZ

    tidx = np.arange(1,num_smpls+1)
    # Sin and Cos
    flicker = 0.4*(1+np.sin(2*np.pi*stim_freq*(tidx /fs)))
    all_HZ = np.append(all_HZ, flicker[np.newaxis,:], axis=0)
    
print(np.shape(all_HZ))






framerate = mywin.getActualFrameRate()



grey_box = visual.Rect(win=mywin, name='grey_box',units='pix', width=image_width, height=image_width,pos=[0,0+ up_height],
                            fillColor='grey',lineColor='grey',opacity=1)


HZ_block = [visual.Rect(win=mywin, name='HZ12_block',units='pix', width=image_width, height=image_width,pos=[0 ,325+ up_height],fillColor='white',opacity=1),
            visual.Rect(win=mywin, name='HZ15_block',units='pix', width=image_width, height=image_width,pos=[-325,0+ up_height],fillColor='white',opacity=1),
            visual.Rect(win=mywin, name='HZ10_block',units='pix', width=image_width, height=image_width,pos=[325,0+ up_height],fillColor='white',opacity=1),
            visual.Rect(win=mywin, name='HZ8_block',units='pix', width=image_width, height=image_width,pos=[0,-325+ up_height],fillColor='white',opacity=1)]






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
    if i >= num_smpls:
        i = 0 
        time = 0
        start = T.time()



    if (time + i) % 100 == 99:
        
        print("time frame rate accuracy: ",(now - start)/((time + i)/fs))   


        
mywin.flip()  
mywin.close()
core.quit()