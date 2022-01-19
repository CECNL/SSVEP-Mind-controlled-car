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

ser = serial.Serial("COM5", 9600, timeout = 1)


flying = True
# myTello = tello.Tello()
debugging = True
queue_len = 3
intervel_time = 0.5
threahold = [1.34, 1.3, 1.4, 1.3, 1.3, 1.4]

""" notch filter """
power_line_frequency = 60  # Target of the notch filter which is the power line frequency
Q = 30.0 # Quality factors
b, a = iirnotch(power_line_frequency, Q, fs=500)
zi_notch = np.repeat(lfilter_zi(b, a)[np.newaxis,:], 9, axis=0)

""" --------------------------"""




q = [queue.Queue(maxsize=queue_len),
     queue.Queue(maxsize=queue_len),
     queue.Queue(maxsize=queue_len),
     queue.Queue(maxsize=queue_len),
     queue.Queue(maxsize=queue_len),
     queue.Queue(maxsize=queue_len)
     ]


def multiplyList(myList):
    # Multiply elements one by one
    result = 1
    for x in myList:
        result = result * x
    return result


# create a new inlet to read from the stream
print("looking for an EEG stream...")
streams = resolve_stream('type', 'EEG')
inlet = StreamInlet(streams[0], max_buflen=1000)
data = np.zeros((13, 0))

# start time
start_seconds = time.time()
# game loop
while True:

    # 控制玩家
    chunk, timestamps = inlet.pull_chunk()
    
    tmp_second = time.time() - start_seconds
    if timestamps:
        chunk = np.array(chunk).T[19:]  

        #### notch filter  #################
        # chunk, zi_notch = lfilter(b, a, chunk, zi=zi_notch)  # notch filtering
        ###################################

        data = np.append(data, chunk[:, :], axis=1)
        data = data[:, -1000:]




        if data.shape[1] == 1000:


            # """ 判斷是不是咬牙 """
            # if(len(indexes(np.array(data[0,...]), thres=30 / max(data[0,...]), min_dist=2)) >= 220):
            #     print(len(indexes(np.array(data[0,...]), thres=30 / max(data[0,...]), min_dist=2)))
            #     if (flying):
            #         print('降落中')
            #         # myTello.land()
            #         flying = False
            #     else:
            #         print('起飛中')
            #         # myTello.takeoff()
            #         flying = True

            #     time.sleep(2)
            #     data = np.zeros((13, 0))
            #     continue

            if(flying):
                """ 四種刺激 分別 8.57, 11, 12, 13, 14, 15 """
                y = fbcca_realtime(data, [11, 12, 13, 14 ,8.57 ,15], 500, num_harms=3, num_fbs=5)
                """ 對data做 normalize 以1為平均"""
                y = y / np.mean(y)

                """0.5秒判斷一次"""
                if tmp_second > intervel_time:
                    start_seconds = time.time()

                    """更新queue"""
                    if q[0].qsize() < queue_len:
                        q[0].put(y[0])
                        q[1].put(y[1])
                        q[2].put(y[2])
                        q[3].put(y[3])
                        q[4].put(y[4])
                        q[5].put(y[5])

                    else:
                        _ = q[0].get()
                        _ = q[1].get()
                        _ = q[2].get()
                        _ = q[3].get()
                        _ = q[4].get()
                        _ = q[5].get()

                        q[0].put(y[0])
                        q[1].put(y[1])
                        q[2].put(y[2])
                        q[3].put(y[3])
                        q[4].put(y[4])
                        q[5].put(y[5])
                    """生出統計過後的結果"""
                    direction = [multiplyList(list(q[0].queue)),
                                 multiplyList(list(q[1].queue)),
                                 multiplyList(list(q[2].queue)),
                                 multiplyList(list(q[3].queue)),
                                 multiplyList(list(q[4].queue)),
                                 multiplyList(list(q[5].queue))
                                 ]

                    print(direction[:4])
                    """大於域值就輸出指令"""
                    # 要改[:6]
                    if np.amax(direction[:4]) >= threahold[np.argmax(direction[:4])]:
                        if np.argmax(direction[:4]) == 0:
                            """指令:前"""
                            # myTello.forward(10)
                            ser.write(b'1')
                            time.sleep(0.1)
                            print('前')
                        elif np.argmax(direction[:4]) == 1:
                            """指令:左"""
                            ser.write(b'3')
                            time.sleep(0.1)
                            # myTello.left(10)
                            print('左')
                        elif np.argmax(direction[:4]) == 2:
                            """指令:右"""
                            ser.write(b'4')
                            time.sleep(0.1)
                            # myTello.right(10)
                            print('右')
                        elif np.argmax(direction[:4]) == 3:
                            """指令:後"""
                            ser.write(b'2')
                            time.sleep(0.1)
                            # myTello.back(10)
                            print("後")
                        # elif np.argmax(direction) == 4:
                        #     """指令:上"""
                        #     # myTello.up(30)
                        #     print('上')
                        # elif np.argmax(direction) == 5:
                        #     """指令:下"""
                        #     # myTello.down(30)
                        #     print('下')
                    else:
                        """指令:do nothing"""
                        ser.write(b'0')
                        time.sleep(0.1)
    #                     playerX_change = 0
    #                     playerY_change = 0


