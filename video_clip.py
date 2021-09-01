import pickle
from collections import defaultdict

import imageio
import numpy as np
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import csv
import os
import tkinter as tk
import time
import webbrowser
from datetime import datetime, timedelta
from tkinter import HORIZONTAL, CENTER, VERTICAL, RIGHT, FALSE, BOTH, END, N
import tkinter.filedialog as fd
from tkinter.ttk import Progressbar
import cv2 as cv
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import pandas as pd
from absl import app

# imageio.plugins.ffmpeg.download()

# GLOBAL Vars
window = ""
video_file = ""
video_file_name = ""
csv_file = ""
csv_output = ""
coordinates = []
output_video = ""
v_0 = ""
v_1 = ""
p_0 = ""
p_1 = ""


# uploads csv for weather report
def select_csv():
    # open directory to select csv files only
    file_path = fd.askopenfile(mode='r', filetypes=[('csv Files', '*csv')])
    # check if it ws selected
    if file_path is not None:
        # label to display the file name
        global csv_file, csv_output, coordinates, output_video
        csv_file = file_path.name
        split_dir = file_path.name.split('/')
        # file name to display is the final item of the list
        csv_name = split_dir[len(split_dir) - 1]
        csv_output = pd.read_csv(csv_file, header=None, skiprows=[0, 1, 2])
        a = csv_file.split('.csv')
        output_video = a[0]
        coordinates = [int(csv_output.iloc[0, 1]), int(csv_output.iloc[0, 2]),
                       int(csv_output.iloc[0, 3]), int(csv_output.iloc[0, 4]),
                       int(csv_output.iloc[1, 1]), int(csv_output.iloc[1, 2]),
                       int(csv_output.iloc[1, 3]), int(csv_output.iloc[1, 4])]

        tk.Label(window, text=csv_name, padx=50).place(relx=0.7, rely=0.25, anchor=CENTER)
        return file_path.name


# Opens user directory to select mp4 file to analyze
def select_video():
    # open directory to select mp4 files only
    file_path = fd.askopenfile(mode='r', filetypes=[('Video Files', '*avi *mp4'), ('MP4 Files', '*mp4')])
    # check if it ws selected
    if file_path is not None:
        # split directory string into it's folder names (each /)
        split_dir = file_path.name.split('/')
        # file name to display is the final item of the list
        global video_file_name
        video_file_name = split_dir[len(split_dir) - 1]
        # set global variable
        global video_file
        video_file = file_path.name
        # label to display the file name
        tk.Label(window, text=video_file_name, padx=50).place(relx=0.3, rely=0.25, anchor=CENTER)
        return file_path.name


def extract_clips():
    # Get coordinates of person of interest
    count = 0
    id_coords = []
    id_list = []
    id_path = defaultdict(list)
    # open pickle file and unpackage the byte stream
    with open(output_video + ".pickle", 'rb') as handle:
        tracking = pickle.load(handle)
    # get list of all ids tracked
    for item in tracking:
        if item[0] not in id_list:
            id_list.append(item[0])
    # for each coordinate, associate the item to the correct id from the list
    for item in tracking:
        for ped in id_list:
            if ped == item[0] and (not item[1] in list(id_path[id])):
                X = item[1][0]
                Y = item[1][1]
                # Limit the amount of computation, by only taking orthogonality of lines within the min and max
                # values
                global coordinates
                if (min(coordinates[0], coordinates[1], coordinates[2], coordinates[3]) <= item[1][0] <= max(
                        coordinates[0], coordinates[1], coordinates[2], coordinates[3])) \
                        and (min(coordinates[4], coordinates[5], coordinates[6], coordinates[7]) <= item[1][1]
                             <= max(coordinates[4], coordinates[5], coordinates[6], coordinates[7])):
                    c = (int(X) - coordinates[1]) * (coordinates[6] - coordinates[5])
                    d = (int(Y) - coordinates[5]) * (coordinates[2] - coordinates[1])
                    side1 = c - d
                    m = (int(X) - coordinates[0]) * (coordinates[7] - coordinates[4])
                    n = (int(Y) - coordinates[4]) * (coordinates[3] - coordinates[0])
                    side2 = m - n
                    # if the id's position is between the tracking region,
                    # then there will be one positive and one negative orthogonal statement
                    if (side1 >= 0 and side2 <= 0) or (side2 >= 0 and side1 <= 0):
                        a = (int(X) - coordinates[0]) * (coordinates[5] - coordinates[4])
                        b = (int(Y) - coordinates[4]) * (coordinates[1] - coordinates[0])
                        enter1 = a - b
                        q = (int(X) - coordinates[3]) * (coordinates[6] - coordinates[7])
                        p = (int(Y) - coordinates[7]) * (coordinates[2] - coordinates[3])
                        enter2 = q - p
                        if (enter1 >= 0 and enter2 <= 0) or (enter2 >= 0 and enter1 <= 0):
                            id_path[ped].append(item[1])
            else:
                continue

    counter = 0
    j = 0
    test_list = []
    xs = []
    ys = []
    # number of coordinates given for id numberr 5 (18336)
    print("total length of id 5 coords: ", len(id_path[5]))
    # get the x and y values for id_path 5
    for key, value in id_path.items():
        if key == 5:
            xs = [x[0] for x in value]
            ys = [x[1] for x in value]
            j += 1
    coord_list = test_list
    print("Length = ", len(test_list))
    print("j = ", j)
    print("len x = ", len(xs))
    print("len y = ", len(ys))

    input_video = str(video_file)
    # get file directory but file name
    split_dir = input_video.split('/')
    output = '/'.join(split_dir[0:len(split_dir) - 1])
    sub_clip = output + '/id3_clip.mp4'

    # pedestrian id frames
    input_cap = cv.VideoCapture(input_video)
    fps = input_cap.get(cv.CAP_PROP_FPS)
    start = int(csv_output.iloc[4, 2])
    final = int(csv_output.iloc[4, 3])
    print(str(start) + " - " + str(final))
    ffmpeg_extract_subclip(input_video, start / fps, final / fps, targetname=sub_clip)
    input_cap.release()

    # Read the video frame, then write the file and display it in the window
    cap = cv.VideoCapture(sub_clip)
    fps = cap.get(cv.CAP_PROP_FPS)
    print("fps = ", fps)
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    zoomed_in = output + '/rectdrawn.mp4'
    # print(id_path[3])
    fourcc = cv.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv.VideoWriter(zoomed_in, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            # OLD ZOOMING Functionality
            # crop_frame = frame[int(min(coordinates[4:len(coordinates)])):int(max(coordinates[4:len(coordinates)])),
            #              int(min(coordinates[0:4])):int(max(coordinates[0:4]))]
            # # write the cropped frame
            # resize = cv.resize(crop_frame, (320, 240))

            # Black boxes around the tracking region
            # left side
            cv.rectangle(frame, (0, 0), (int(min(coordinates[0:4])), height), (0, 0, 0), -1)
            # right side
            cv.rectangle(frame, (int(max(coordinates[0:4])), 0), (width, height), (0, 0, 0), -1)
            # Top side
            cv.rectangle(frame, (0, 0), (width, int(min(coordinates[4:len(coordinates)]))), (0, 0, 0), -1)
            # Bottom side
            cv.rectangle(frame, (0, int(max(coordinates[4:len(coordinates)]))), (width, height), (0, 0, 0), -1)
            # draw unique points of the trajectory
            for item in coord_list:
                # Center coordinates
                center_coordinates = (item[0], item[1])
                # Radius of circle
                radius = 2
                # Blue color in BGR
                color = (255, 0, 0)
                # Line thickness of 2 px
                thickness = 1
                # Draw a circle with blue line borders of thickness of 2 px
                cv.circle(frame, center_coordinates, radius, color, thickness)
            counter += 1
            out.write(frame)
        else:
            break
    print("Video cropping completed")
    print("counter = ", counter)
    # Release reader wand writer after parsing all frames
    cap.release()
    out.release()
    # cv.destroyAllWindows()


def get_clips():
    global window
    window = tk.Toplevel()
    window.title('Video Highlights')
    win_width = 640
    height = 480
    geometry = str(win_width) + "x" + str(height)
    window.geometry(geometry)
    window.resizable(False, False)
    # First row labels for selecting files
    tk.Label(window, text='Upload video output in mp4 format ',
             font=('Helvetica', 11, 'bold')).place(relx=0.3, rely=0.15, anchor=CENTER)
    select_output = tk.Label(window, text='Upload csv output ',
                             font=('Helvetica', 11, 'bold')).place(relx=0.7, rely=0.15, anchor=CENTER)
    # Second row buttons to open directory
    tk.Button(window, text='Choose video',
              command=lambda: select_video()).place(relx=0.3, rely=0.2, anchor=CENTER)
    tk.Button(window, text='Choose .csv',
              command=lambda: select_csv()).place(relx=0.7, rely=0.2, anchor=CENTER)
    tk.Button(window, text='Extract clips',
              command=lambda: extract_clips()).place(relx=0.5, rely=0.3, anchor=CENTER)

    # User inputs values that would be important to examine (clips of specific speeds or percentile groups of persons
    speed_label = tk.Label(window, text="What speeds are important? (in m/s)", font=('Helvetica', 11, 'bold'))
    speed_label.place(relx=0.5, rely=0.4, anchor=CENTER)
    global v_0, v_1
    v_0 = tk.StringVar()
    v_1 = tk.StringVar()
    v0 = tk.Entry(window, width=8, textvariable=v_0)
    v0.place(relx=0.4, rely=0.5, anchor=CENTER)
    tk.Label(window, text="to").place(relx=0.5, rely=0.5, anchor=CENTER)
    v1 = tk.Entry(window, width=8, textvariable=v_1)
    v1.place(relx=0.6, rely=0.5, anchor=CENTER)
    speed_label = tk.Label(window, text="What percentiles are important?", font=('Helvetica', 11, 'bold'))
    speed_label.place(relx=0.5, rely=0.55, anchor=CENTER)
    global p_0, p_1
    p_0 = tk.StringVar()
    p_1 = tk.StringVar()
    p0 = tk.Entry(window, width=8, textvariable=p_0)
    p0.place(relx=0.4, rely=0.6, anchor=CENTER)
    tk.Label(window, text="to").place(relx=0.5, rely=0.6, anchor=CENTER)
    p1 = tk.Entry(window, width=8, textvariable=p_1)
    p1.place(relx=0.6, rely=0.6, anchor=CENTER)
