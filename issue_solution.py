import os
import collections
import pickle
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
from collections import defaultdict
from imutils.video import VideoStream
import numpy as np
import cv2
from PIL import Image
import imutils
import time
import csv

count = 0
id_coords = []
id_list = []
id_path = defaultdict(list)
# open pickle file and unpackage the byte stream
with open("C:/Users/h_gho/EHT_YOLOv4/data/ts_001_OUTPUT.pickle", 'rb') as handle:
    tracking = pickle.load(handle)


# print(tracking)
print(len(tracking))
# # # #
no_persons = []
for i in range(len(tracking)):
    if int(tracking[i][1]) not in no_persons:
        no_persons.append(int(tracking[i][1]))
    else:
        continue

print("Number of assigned ids = ", len(no_persons))
print(no_persons)
#

id_path = defaultdict(list)
id_Frames = defaultdict(list)

for i in range(len(tracking)):
    for id in no_persons:
        if id == int(tracking[i][1]) and (not int(tracking[i][1]) in list(id_path[id])):
            id_path[id].append((int(tracking[i][2]), int(tracking[i][3])))
            id_Frames[id].append(tracking[i][0])
        else:
            continue

# print(id_path[98])
# print(id_Frames[98])
# print(id_Frames[98][0])

#
cId = input("Enter The Person's ID Number =  ")
cId = int(cId)
#
# for key, value in id_path.items():
#     if key == cId:
#
#         x_pixel = [pt[0] for pt in value]
#         y_pixel = [pt[1] for pt in value]
#
#         x = [element * 1 for element in x_pixel]  # put scaling factor instead of 1
#         y = [element * 1 for element in y_pixel]  # put scaling factor instead of 1
#
#     ###########################################################
#         # create a figure with two subplots
#         fig, (ax1, ax2) = plt.subplots(2,1)
#
#         # intialize two line objects (one in each axes)
#         line1, = ax1.plot([], [], lw=2)
#         line2, = ax2.plot([], [], lw=2, color='r')
#
#         ax1.set_ylim(min(x)-10, max(x)+10)
#         ax1.set_xlim(0, len(x))
#         # ax1.grid()
#
#         ax2.set_ylim(min(y) - 10, max(y) + 10)
#         ax2.set_xlim(0, len(y))
#         # ax2.grid()
#
#         # initialize the data arrays
#         xdata, y1data, y2data = [], [], []
#         def run(i):
#             xdata.append(i)
#             y1data.append(x[i])
#             y2data.append(y[i])
#
#             # update the data of both line objects
#             line1.set_data(xdata, y1data)
#             line2.set_data(xdata, y2data)
#
#             return line1, line2,
#
#         ani = animation.FuncAnimation(fig, run, blit=True, interval=20)
#     plt.show()


# print(id_path[cId])
print("No of frames which this ID was present :  ", len(id_Frames[cId]))
print("and the frames which this ID was present are :  ", id_Frames[cId])
# plt.plot(id_Frames[cId])
# plt.show()


video_path = "C:/Users/h_gho/EHT_YOLOv4/data/ts_001.mp4"
# cv2.namedWindow('Frame', cv2.WINDOW_NORMAL)
cap = cv2.VideoCapture(video_path)

# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video  file")

i = 0
frameNo = 0
startFrame = id_Frames[cId][0]
print("First frame of this ID is :  ",startFrame)
while (cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:
        frameNo += 1
        # print(frameNo)
        overlay = frame.copy()
        cv2.imshow('Frame', frame)
        if frameNo >= startFrame and frameNo in id_Frames[cId]:
            if i < len(id_path[cId]):
                center_coordinates = (id_path[cId][i])
                # Radius of circle
                radius = 10
                # color in BGR
                color = (45, 255, 255)
                # filled circle
                thickness = -1
                cv2.circle(overlay, center_coordinates, radius, color, thickness)
                cv2.addWeighted(overlay, 0.5, frame, 1-0.5,
                                0, frame)
                thickness = 1
                frame = cv2.circle(frame, center_coordinates, radius, (0,0,255), thickness)

            i += 1
            cv2.imshow('Frame', frame)

    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
