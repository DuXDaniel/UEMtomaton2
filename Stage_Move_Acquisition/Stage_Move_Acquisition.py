import math
import time
import sys
import socket
import subprocess
import random
import datetime
import threading
import queue
import pywinauto
import os.path as path
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import PhotoImage
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from tkinter import simpledialog
        
def PressKey(keypress):
    ###### Press on keyboard the passed request
    pywinauto.keyboard.send_keys(keypress,pause=0.05)
    time.sleep(0.1)

def MoveMouse(x,y):
    pywinauto.mouse.move((x,y))
    time.sleep(0.1)

def ClickMouse():
    pywinauto.mouse.click()
    time.sleep(0.1)

def FocusTheDesiredWnd():
    searchApp = pywinauto.application.Application()
    try:
        searchApp.connect(title_re=r'.*xT microscope Control.*')
        
        restoreApp = searchApp.top_window()
        restoreApp.minimize()
        restoreApp.restore()
        restoreApp.set_focus()
        return restoreApp
    except:
        return 0

def main(argv):
    mainWindow = tk.Tk()
    # the input dialog
    ################## make input for x range, y range, z range, tilt, rot, steps, linear, meshed
    ################## include inputs for acquisition time (snapshot vs full acquisition)
    ################## filepath, filename

    filepathLabel = ttk.Label(
        mainWindow,
        text="Delay Computer IP: ",
        justify="right"
    )
    filePathEntry = ttk.Entry(
        mainWindow
    )
    filepathBrowse = ttk.Button(
        mainWindow,
        text="Browse",
        command=lambda: browsePath_Click()
    )
    filebaseLabel = ttk.Label(
        mainWindow,
        text="Delay Computer IP: ",
        justify="right"
    )
    filebaseEntry = ttk.Entry(
        mainWindow
    )
    saveButton = ttk.Button(
        mainWindow,
        text="Save Values",
        command=lambda: saveButton_Click()
    )
    loadButton = ttk.Button(
        mainWindow,
        text="Load Values",
        command=lambda: loadButton_Click()
    )

    xLabel = ttk.Label(
        mainWindow,
        text="Delay Computer IP: ",
        justify="right"
    )
    xStartEntry = ttk.Entry(
        mainWindow
    )
    xEndEntry = ttk.Entry(
        mainWindow
    )
    xStepEntry = ttk.Entry(
        mainWindow
    )
    
    yLabel = ttk.Label(
        mainWindow,
        text="Delay Computer IP: ",
        justify="right"
    )
    yStartEntry = ttk.Entry(
        mainWindow
    )
    yEndEntry = ttk.Entry(
        mainWindow
    )
    yStepEntry = ttk.Entry(
        mainWindow
    )

    zLabel = ttk.Label(
        mainWindow,
        text="Delay Computer IP: ",
        justify="right"
    )
    zStartEntry = ttk.Entry(
        mainWindow
    )
    zEndEntry = ttk.Entry(
        mainWindow
    )
    zStepEntry = ttk.Entry(
        mainWindow
    )

    tiltLabel = ttk.Label(
        mainWindow,
        text="Delay Computer IP: ",
        justify="right"
    )
    tiltStartEntry = ttk.Entry(
        mainWindow
    )
    tiltEndEntry = ttk.Entry(
        mainWindow
    )
    tiltStepEntry = ttk.Entry(
        mainWindow
    )

    rotLabel = ttk.Label(
        mainWindow,
        text="Delay Computer IP: ",
        justify="right"
    )
    rotStartEntry = ttk.Entry(
        mainWindow
    )
    rotEndEntry = ttk.Entry(
        mainWindow
    )
    rotStepEntry = ttk.Entry(
        mainWindow
    )

    linearRadio = ttk.Radiobutton(
        mainWindow,
        text="Linear",
        command=lambda: linearRadio_Switch()
    )
    meshedRadio = ttk.Radiobutton(
        mainWindow,
        text="Meshed",
        command=lambda: meshRadio_Switch()
    )

    snapshotRadio = ttk.Radiobutton(
        mainWindow,
        text="Snap",
        command=lambda: snapRadio_Switch()
    )
    fullAcqRadio = ttk.Radiobutton(
        mainWindow,
        text="Full",
        command=lambda: fullAcqRadio_Switch()
    )

    initButton = ttk.Button(
        mainWindow,
        text="Start",
        command=lambda: runScan()
    )

    experProgBar = ttk.Progressbar(
        mainWindow
    )
    estTimeLabel = ttk.Label(
        mainWindow,
        text="Estimated Time Remaining:"
    )
    estTimeVal = ttk.Label(
        mainWindow,
        text="---"
    )

    filepathLabel.grid(column=0, row=0, rowspan=1, padx=5, pady=5, sticky="nswe")
    filePathEntry.grid(column=1, row=0, rowspan=1, padx=5, pady=5, sticky="nswe")
    filepathBrowse.grid(column=2, row=0, rowspan=1, padx=5, pady=5, sticky="nswe")
    filebaseLabel.grid(column=0, row=1, rowspan=1, padx=5, pady=5, sticky="nswe")
    filebaseEntry.grid(column=1, row=1, rowspan=1, padx=5, pady=5, sticky="nswe")

    xLabel.grid(column=0, row=2, rowspan=1, padx=5, pady=5, sticky="nswe")
    xStartEntry.grid(column=1, row=2, rowspan=1, padx=5, pady=5, sticky="nswe")
    xEndEntry.grid(column=2, row=2, rowspan=1, padx=5, pady=5, sticky="nswe")
    xStepEntry.grid(column=3, row=2, rowspan=1, padx=5, pady=5, sticky="nswe")

    yLabel.grid(column=0, row=3, rowspan=1, padx=5, pady=5, sticky="nswe")
    yStartEntry.grid(column=1, row=3, rowspan=1, padx=5, pady=5, sticky="nswe")
    yEndEntry.grid(column=2, row=3, rowspan=1, padx=5, pady=5, sticky="nswe")
    yStepEntry.grid(column=3, row=3, rowspan=1, padx=5, pady=5, sticky="nswe")
    
    zLabel.grid(column=0, row=4, rowspan=1, padx=5, pady=5, sticky="nswe")
    zStartEntry.grid(column=1, row=4, rowspan=1, padx=5, pady=5, sticky="nswe")
    zEndEntry.grid(column=2, row=4, rowspan=1, padx=5, pady=5, sticky="nswe")
    zStepEntry.grid(column=3, row=4, rowspan=1, padx=5, pady=5, sticky="nswe")

    tiltLabel.grid(column=0, row=5, rowspan=1, padx=5, pady=5, sticky="nswe")
    tiltStartEntry.grid(column=1, row=5, rowspan=1, padx=5, pady=5, sticky="nswe")
    tiltEndEntry.grid(column=2, row=5, rowspan=1, padx=5, pady=5, sticky="nswe")
    tiltStepEntry.grid(column=3, row=5, rowspan=1, padx=5, pady=5, sticky="nswe")
    
    rotLabel.grid(column=0, row=6, rowspan=1, padx=5, pady=5, sticky="nswe")
    rotStartEntry.grid(column=1, row=6, rowspan=1, padx=5, pady=5, sticky="nswe")
    rotEndEntry.grid(column=2, row=6, rowspan=1, padx=5, pady=5, sticky="nswe")
    rotStepEntry.grid(column=3, row=6, rowspan=1, padx=5, pady=5, sticky="nswe")

    linearRadio.grid(column=1, row=7, padx=5, pady=5, sticky="nswe")
    meshedRadio.grid(column=2, row=7, padx=5, pady=5, sticky="nswe")

    snapshotRadio.grid(column=1, row=8, padx=5, pady=5, sticky="nswe")
    fullAcqRadio.grid(column=2, row=8, padx=5, pady=5, sticky="nswe")

    initButton.grid(column=1, row=9, columnspan=2, padx=5, pady=5, sticky="nswe")

    experProgBar.grid(column=0, row=10, columnspan=4, padx=5, pady=5, sticky="nswe")
    estTimeLabel.grid(column=1, row=11, columnspan=1, padx=5, pady=5, sticky="nswe")
    estTimeVal.grid(column=2, row=11, columnspan=1, padx=5, pady=5, sticky="nswe")

    mainWindow.mainloop()

def browsePath_Click(self):
    imgDirectory = filedialog.askdirectory(title="Select the file path for the images to be saved in")
    filepathEntry.delete(0, "end")
    filepathEntry.insert(0, imgDirectory)

def linearRadio_Switch():
    return

def meshRadio_Switch():
    return

def snapRadio_Switch():
    return

def fullAcqRadio_Switch():
    return

def runScan():
    hFoundWnd = FocusTheDesiredWnd()

    f = open("rangetest.txt",'r')
    filepath = f.readline()
    filebase = f.readline()
    x_start = f.readline()
    x_end = f.readline()
    x_steps = f.readline()
    y_start = f.readline()
    y_end = f.readline()
    y_steps = f.readline()
    z_start = f.readline()
    z_end = f.readline()
    z_steps = f.readline()
    tilt_start = f.readline()
    tilt_end = f.readline()
    tilt_steps = f.readline()
    rot_start = f.readline()
    rot_end = f.readline()
    rot_steps = f.readline()
    dist_method = f.readline()
    acq_style = f.readline()
    f.close()

    ############# make next section about establishing the number of required steps

    ############# iterate through steps
    while (curStat == "1"):

        if (statLine == "0"):
            hFoundWnd = FocusTheDesiredWnd()
            if(hFoundWnd != 0):


                filename = filepath + "\\" + filebase + "_" + curScan + "_" + curScanStep + "_" + curDelay + ".tif"

                PressKey('{VK_F2}')

                time.sleep(USER_INP + 5)

                quadfile = filename
                PressKey(quadfile)
                PressKey('{VK_RETURN}')

            else:
                print("Cannot find microscope control. Exiting.")
                curStat = 0


        time.sleep(0.5)
    return

def saveButton_Click():
    return

def loadButton_Click():
    return

if __name__ == '__main__':
    main(sys.argv)