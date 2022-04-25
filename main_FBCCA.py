import pdb
import numpy as np
import matplotlib.pyplot as plt
from pylsl import StreamInfo, StreamOutlet, resolve_stream, StreamInlet
import threading
from scipy.signal import iirnotch, filtfilt, cheb1ord, cheby1, lfilter, firwin,lfilter_zi,convolve, butter
import queue
import time
from fbcca import fbcca_realtime
from sklearn.cross_decomposition import CCA
from scipy.stats import pearsonr
from scipy import signal
from sys import exit
import random
import math
import pandas as pd
# from peakutils.peak import indexes
import matplotlib.pyplot as plt
# from easytello import tello
import serial
import time

# this is for connecting the car
ser = serial.Serial("COM5", 9600, timeout = 1)




# calculate the correlatons of 3 intervals and multiply them to decide the most likely direction
queue_len = 3
# interval between different time window 
intervel_time = 0.5
#thresholds for four directions - forward, left, right, backward respectively
threahold = [1.35, 1.25, 1.2, 1.1]





# store cca result
q = [queue.Queue(maxsize=queue_len),
     queue.Queue(maxsize=queue_len),
     queue.Queue(maxsize=queue_len),
     queue.Queue(maxsize=queue_len)]


def multiplyList(myList):
    '''product of all elements in the list'''
    result = 1
    for x in myList:
        result = result * x
    return result


''' create a new inlet to read from the stream'''
print("looking for an EEG stream...")
streams = resolve_stream('type', 'EEG')
inlet = StreamInlet(streams[0], max_buflen=1000)
data = np.zeros((8, 0))

# start time
start_seconds = time.time()
# game loop
while True:
    # keep pulling data from eeg headset
    chunk, timestamps = inlet.pull_chunk()
    
    tmp_second = time.time() - start_seconds
    if timestamps:
        chunk = np.array(chunk).T[24:]  



        data = np.append(data, chunk[:, :], axis=1) # append eeg data
        data = data[:, -1250:]#2.5sec,sampling rate=500Hz

        if data.shape[1] == 1250:#This will be true after at least 1250 samples are collected,
            #  and will be false when the inlet hasn't collected enough data


            """ four stimulus frequencies 11, 12, 13, 14 """
            y = fbcca_realtime(data, [11, 12, 13, 14 ], 500, num_harms=3, num_fbs=5)
            """ normalize the correlation to unit mean """
            y = y / np.mean(y)

            """update the queue every 0.5sec. 
            The queue stores the correlatoins of 3 overlapping windows. 
            The windows are 2.5-sec long with 0.5 sec stride."""
            if tmp_second > intervel_time:
                start_seconds = time.time()

                if q[0].qsize() < queue_len:# queue not full
                    q[0].put(y[0])
                    q[1].put(y[1])
                    q[2].put(y[2])
                    q[3].put(y[3])
                    

                else:# full queue
                    _ = q[0].get()
                    _ = q[1].get()
                    _ = q[2].get()
                    _ = q[3].get()
                    

                    q[0].put(y[0])
                    q[1].put(y[1])
                    q[2].put(y[2])
                    q[3].put(y[3])
                    
                """multiply the 3 correlations in each direction"""
                direction = [multiplyList(list(q[0].queue)),
                                multiplyList(list(q[1].queue)),
                                multiplyList(list(q[2].queue)),
                                multiplyList(list(q[3].queue))
                                ]

                print(direction[:4])
                """send command if the correaltion product of the most-likely direction
                exceeds the predefined threshold. Otherwise, stop the car."""
                if np.amax(direction[:4]) >= threahold[np.argmax(direction[:4])]:
                    if np.argmax(direction[:4]) == 0:
                        """send command 'forward' """
                        # myTello.forward(10)
                        ser.write(b'1')
                        time.sleep(0.1)
                        print('forward')
                    elif np.argmax(direction[:4]) == 1:
                        """send command 'left' """
                        ser.write(b'3')
                        time.sleep(0.1)
                        # myTello.left(10)
                        print('left')
                    elif np.argmax(direction[:4]) == 2:
                        """send command 'right' """
                        ser.write(b'4')
                        time.sleep(0.1)
                        # myTello.right(10)
                        print('right')
                    elif np.argmax(direction[:4]) == 3:
                        """send command 'backward' """
                        ser.write(b'2')
                        time.sleep(0.1)
                        # myTello.back(10)
                        print("backward")

                else:
                    """send command 'stop' """
                    ser.write(b'0')
                    time.sleep(0.1)



