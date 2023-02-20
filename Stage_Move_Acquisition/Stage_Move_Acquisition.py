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

def main(argv):
    stageMover = Stage_Mover()

class Stage_Mover():
    def __init__(self, parent=None):
        self.mainWindow = tk.Tk()

        self.filepathLabel = ttk.Label(
            self.mainWindow,
            text="Filepath: ",
            justify="right"
        )
        self.filepathEntry = ttk.Entry(
            self.mainWindow
        )
        self.filepathBrowse = ttk.Button(
            self.mainWindow,
            text="Browse",
            command=lambda: self.browsePath_Click()
        )
        self.filebaseLabel = ttk.Label(
            self.mainWindow,
            text="Filebase: ",
            justify="right"
        )
        self.filebaseEntry = ttk.Entry(
            self.mainWindow
        )
        self.saveButton = ttk.Button(
            self.mainWindow,
            text="Save Values",
            command=lambda: self.saveButton_Click()
        )
        self.loadButton = ttk.Button(
            self.mainWindow,
            text="Load Values",
            command=lambda: self.loadButton_Click()
        )

        self.xLabel = ttk.Label(
            self.mainWindow,
            text="x Movement: ",
            justify="right"
        )
        self.xStartEntry = ttk.Entry(
            self.mainWindow
        )
        self.xEndEntry = ttk.Entry(
            self.mainWindow
        )
        self.xStepEntry = ttk.Entry(
            self.mainWindow
        )
        
        self.yLabel = ttk.Label(
            self.mainWindow,
            text="y Movement: ",
            justify="right"
        )
        self.yStartEntry = ttk.Entry(
            self.mainWindow
        )
        self.yEndEntry = ttk.Entry(
            self.mainWindow
        )
        self.yStepEntry = ttk.Entry(
            self.mainWindow
        )

        self.zLabel = ttk.Label(
            self.mainWindow,
            text="z Movement: ",
            justify="right"
        )
        self.zStartEntry = ttk.Entry(
            self.mainWindow
        )
        self.zEndEntry = ttk.Entry(
            self.mainWindow
        )
        self.zStepEntry = ttk.Entry(
            self.mainWindow
        )

        self.tiltLabel = ttk.Label(
            self.mainWindow,
            text="Tilt Movement: ",
            justify="right"
        )
        self.tiltStartEntry = ttk.Entry(
            self.mainWindow
        )
        self.tiltEndEntry = ttk.Entry(
            self.mainWindow
        )
        self.tiltStepEntry = ttk.Entry(
            self.mainWindow
        )

        self.rotLabel = ttk.Label(
            self.mainWindow,
            text="Rot Movement: ",
            justify="right"
        )
        self.rotStartEntry = ttk.Entry(
            self.mainWindow
        )
        self.rotEndEntry = ttk.Entry(
            self.mainWindow
        )
        self.rotStepEntry = ttk.Entry(
            self.mainWindow
        )

        self.distributeVar = tk.IntVar(value=1)
        self.linearCheck = tk.Checkbutton(
            self.mainWindow,
            variable=self.distributeVar,
            offvalue=0,
            onvalue=1,
            text='Linear',
            command=lambda: self.linearRadio_Switch()
        )
        self.meshedCheck = tk.Checkbutton(
            self.mainWindow,
            variable=self.distributeVar,
            offvalue=1,
            onvalue=0,
            text='Meshed',
            command=lambda: self.meshRadio_Switch()
        )

        self.acqParamVar = tk.IntVar(value=1)
        self.snapshotCheck = tk.Checkbutton(
            self.mainWindow,
            variable=self.acqParamVar,
            offvalue=0,
            onvalue=1,
            text='Snapshot',
            command=lambda: self.snapRadio_Switch()
        )
        self.fullAcqCheck = tk.Checkbutton(
            self.mainWindow,
            variable=self.acqParamVar,
            offvalue=1,
            onvalue=0,
            text='Full Acquisition',
            command=lambda: self.fullAcqRadio_Switch()
        )

        self.initButton = ttk.Button(
            self.mainWindow,
            text="Start",
            command=lambda: self.runScan()
        )

        self.experProgBar = ttk.Progressbar(
            self.mainWindow
        )
        self.estTimeLabel = ttk.Label(
            self.mainWindow,
            text="Estimated Time Remaining:"
        )
        self.estTimeVal = ttk.Label(
            self.mainWindow,
            text="---"
        )

        self.filepathLabel.grid(column=0, row=0, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.filepathEntry.grid(column=1, row=0, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.filepathBrowse.grid(column=2, row=0, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.filebaseLabel.grid(column=0, row=1, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.filebaseEntry.grid(column=1, row=1, rowspan=1, padx=5, pady=5, sticky="nswe")

        self.saveButton.grid(column=2, row=1, columnspan=1, padx=5, pady=5, sticky="nswe")
        self.loadButton.grid(column=3, row=1, columnspan=1, padx=5, pady=5, sticky="nswe")

        self.xLabel.grid(column=0, row=2, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.xStartEntry.grid(column=1, row=2, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.xEndEntry.grid(column=2, row=2, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.xStepEntry.grid(column=3, row=2, rowspan=1, padx=5, pady=5, sticky="nswe")

        self.yLabel.grid(column=0, row=3, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.yStartEntry.grid(column=1, row=3, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.yEndEntry.grid(column=2, row=3, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.yStepEntry.grid(column=3, row=3, rowspan=1, padx=5, pady=5, sticky="nswe")
        
        self.zLabel.grid(column=0, row=4, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.zStartEntry.grid(column=1, row=4, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.zEndEntry.grid(column=2, row=4, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.zStepEntry.grid(column=3, row=4, rowspan=1, padx=5, pady=5, sticky="nswe")

        self.tiltLabel.grid(column=0, row=5, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.tiltStartEntry.grid(column=1, row=5, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.tiltEndEntry.grid(column=2, row=5, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.tiltStepEntry.grid(column=3, row=5, rowspan=1, padx=5, pady=5, sticky="nswe")
        
        self.rotLabel.grid(column=0, row=6, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.rotStartEntry.grid(column=1, row=6, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.rotEndEntry.grid(column=2, row=6, rowspan=1, padx=5, pady=5, sticky="nswe")
        self.rotStepEntry.grid(column=3, row=6, rowspan=1, padx=5, pady=5, sticky="nswe")

        self.linearCheck.grid(column=1, row=7, padx=5, pady=5, sticky="nswe")
        self.meshedCheck.grid(column=2, row=7, padx=5, pady=5, sticky="nswe")

        self.snapshotCheck.grid(column=1, row=8, padx=5, pady=5, sticky="nswe")
        self.fullAcqCheck.grid(column=2, row=8, padx=5, pady=5, sticky="nswe")

        self.initButton.grid(column=1, row=9, columnspan=2, padx=5, pady=5, sticky="nswe")

        self.experProgBar.grid(column=0, row=10, columnspan=4, padx=5, pady=5, sticky="nswe")
        self.estTimeLabel.grid(column=1, row=11, columnspan=1, padx=5, pady=5, sticky="nswe")
        self.estTimeVal.grid(column=2, row=11, columnspan=1, padx=5, pady=5, sticky="nswe")

        self.mainWindow.mainloop()
        
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

    def browsePath_Click(self):
        try:
            self.imgDirectory = filedialog.askdirectory(title="Select the file path for the images to be saved in")
            self.filepathEntry.delete(0, "end")
            self.filepathEntry.insert(0, self.imgDirectory)
        except:
            pass
        return

    def linearRadio_Switch(self):
        self.distributeVar.set(value=0)
        self.linearCheck.select()
        self.meshedCheck.deselect()
        return

    def meshRadio_Switch(self):
        self.distributeVar.set(value=1)
        self.meshedCheck.select()
        self.linearCheck.deselect()
        return

    def snapRadio_Switch(self):
        self.acqParamVar.set(value=0)
        self.snapshotCheck.select()
        self.fullAcqCheck.deselect()
        return

    def fullAcqRadio_Switch(self):
        self.acqParamVar.set(value=1)
        self.fullAcqCheck.select()
        self.snapshotCheck.deselect()
        return

    def runScan(self):
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

        hFoundWnd = self.FocusTheDesiredWnd()

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

    def saveButton_Click(self):
        f = filedialog.asksaveasfile(mode="w", defaultextension=".txt")
        f.write(self.filepathEntry.get().strip() + "\n")
        f.write(self.filebaseEntry.get().strip() + "\n")
        f.write(self.xStartEntry.get().strip() + "\n")
        f.write(self.xEndEntry.get().strip() + "\n")
        f.write(self.xStepEntry.get().strip() + "\n")
        f.write(self.yStartEntry.get().strip() + "\n")
        f.write(self.yEndEntry.get().strip() + "\n")
        f.write(self.yStepEntry.get().strip() + "\n")
        f.write(self.zStartEntry.get().strip() + "\n")
        f.write(self.zEndEntry.get().strip() + "\n")
        f.write(self.zStepEntry.get().strip() + "\n")
        f.write(self.tiltStartEntry.get().strip() + "\n")
        f.write(self.tiltEndEntry.get().strip() + "\n")
        f.write(self.tiltStepEntry.get().strip() + "\n")
        f.write(self.rotStartEntry.get().strip() + "\n")
        f.write(self.rotEndEntry.get().strip() + "\n")
        f.write(self.rotStepEntry.get().strip() + "\n")
        f.write(str(self.distributeVar.get()) + "\n")
        f.write(str(self.acqParamVar.get()))
        return

    def loadButton_Click(self):
        loadfile = filedialog.askopenfilename()
        f = open(loadfile,'r')
        self.filepathEntry.delete(0, "end")
        self.filepathEntry.insert(0, f.readline())
        self.filebaseEntry.delete(0, "end")
        self.filebaseEntry.insert(0, f.readline())
        self.xStartEntry.delete(0, "end")
        self.xStartEntry.insert(0, f.readline())
        self.xEndEntry.delete(0, "end")
        self.xEndEntry.insert(0, f.readline())
        
        f.close()
        return

if __name__ == '__main__':
    main(sys.argv)