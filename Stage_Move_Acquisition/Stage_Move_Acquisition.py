import math
import time
import sys
sys.coinit_flags = 2  # COINIT_APARTMENTTHREADED
import socket
import subprocess
import random
import datetime
import threading
import queue
import pywinauto
import json
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
            text='Linear (takes max)',
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
        self.statLabel = ttk.Label(
            self.mainWindow,
            text="Status"
        )
        self.statText = ttk.Label(
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
        self.estTimeLabel.grid(column=0, row=11, columnspan=1, padx=5, pady=5, sticky="nswe")
        self.estTimeVal.grid(column=1, row=11, columnspan=1, padx=5, pady=5, sticky="nswe")
        self.statLabel.grid(column=2, row=11, columnspan=1, padx=5, pady=5, sticky="nswe")
        self.statText.grid(column=3, row=11, columnspan=1, padx=5, pady=5, sticky="nswe")

        self.mainWindow.mainloop()
        
    def PressKey(self,keypress):
        ###### Press on keyboard the passed request
        pywinauto.keyboard.send_keys(keypress,pause=0.05)
        time.sleep(0.1)

    def MoveMouse(self,x,y):
        pywinauto.mouse.move(coords=(x,y))
        time.sleep(0.1)

    def ClickMouse(self,x,y):
        pywinauto.mouse.click(coords=(x,y))
        time.sleep(0.1)

    def FocusTheDesiredWnd(self):
        searchApp = pywinauto.application.Application()
        try:
            searchApp.connect(title_re=r'.*Word.*')
            #searchApp.connect(title_re=r'.*xT microscope Control.*')
            
            restoreApp = searchApp.top_window()
            restoreApp.minimize()
            restoreApp.restore()
            restoreApp.set_focus()
            return restoreApp
        except:
            return 0
            
    def FocusSnip(self):
        searchApp = pywinauto.application.Application()
        try:
            searchApp.connect(title_re=r'.*Snipping.*')
            
            restoreApp = searchApp.top_window()
            restoreApp.minimize()
            restoreApp.restore()
            restoreApp.set_focus()
            return restoreApp
        except:
            return 0

    def browsePath_Click(self):
        imgDirectory = filedialog.askdirectory(title="Select the file path for the images to be saved in")
        self.filepathEntry.delete(0, "end")
        self.filepathEntry.insert(0, imgDirectory)

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
        filepath = self.filepathEntry.get().strip()
        filebase = self.filebaseEntry.get().strip()
        x_start = float(self.xStartEntry.get().strip())
        x_end = float(self.xEndEntry.get().strip())
        x_steps = int(self.xStepEntry.get().strip())
        y_start = float(self.yStartEntry.get().strip())
        y_end = float(self.yEndEntry.get().strip())
        y_steps = int(self.yStepEntry.get().strip())
        z_start = float(self.zStartEntry.get().strip())
        z_end = float(self.zEndEntry.get().strip())
        z_steps = int(self.zStepEntry.get().strip())
        tilt_start = float(self.tiltStartEntry.get().strip())
        tilt_end = float(self.tiltEndEntry.get().strip())
        tilt_steps = int(self.tiltStepEntry.get().strip())
        rot_start = float(self.rotStartEntry.get().strip())
        rot_end = float(self.rotEndEntry.get().strip())
        rot_steps = int(self.rotStepEntry.get().strip())
        dist_method = self.distributeVar.get()
        acq_style = self.acqParamVar.get()

        self.statText.config(text="Building points")

        if (dist_method == 1):
            stepCount = max([x_steps, y_steps, z_steps, tilt_steps, rot_steps])
            x_range = np.linspace(x_start,x_end,stepCount)
            y_range = np.linspace(y_start,y_end,stepCount)
            z_range = np.linspace(z_start,z_end,stepCount)
            tilt_range = np.linspace(tilt_start,tilt_end,stepCount)
            rot_range = np.linspace(rot_start,rot_end,stepCount)
        elif (dist_method == 0):
            x_init_range = np.linspace(x_start,x_end,x_steps)
            y_init_range = np.linspace(y_start,y_end,y_steps)
            z_init_range = np.linspace(z_start,z_end,z_steps)
            tilt_init_range = np.linspace(tilt_start,tilt_end,tilt_steps)
            rot_init_range = np.linspace(rot_start,rot_end,rot_steps)
            x_mesh, y_mesh, z_mesh, tilt_mesh, rot_mesh = np.meshgrid(x_init_range, y_init_range, z_init_range, tilt_init_range, rot_init_range)
            
            x_range = x_mesh.flatten()
            y_range = y_mesh.flatten()
            z_range = z_mesh.flatten()
            tilt_range = tilt_mesh.flatten()
            rot_range = rot_mesh.flatten()
            stepCount = len(x_range)
 
        points_taken = {
            "x_range": x_range.tolist(),
            "y_range": y_range.tolist(),
            "z_range": z_range.tolist(),
            "tilt_range": tilt_range.tolist(),
            "rot_range": rot_range.tolist()
        }

        json_object = json.dumps(points_taken)

        with open(filepath + "\\" + filebase + "_acq_points.json", "w") as outfile:
            outfile.write(json_object)

        hFoundWnd = self.FocusTheDesiredWnd()

        steps = np.arange(stepCount)

        last_x = -5000
        last_y = -5000
        last_z = -5000
        last_tilt = -5000
        last_rot = -5000

        cumulTime = 0

        self.experProgBar['maximum'] = len(steps)-1

        for curStep in steps:
            st = time.time()
            # Moving stage
            self.statText.config(text="Moving stage")
            hFoundWnd = self.FocusTheDesiredWnd()
            if(hFoundWnd != 0):
                self.ClickMouse(1584+15,52+15)
                if (x_range[curStep] != last_x):  
                    self.ClickMouse(1648+58,183+12)
                    self.PressKey('+{VK_HOME}')
                    self.PressKey(str(x_range[curStep]))
                    last_x = x_range[curStep]
                if (y_range[curStep] != last_y):
                    self.ClickMouse(1648+58,215+12)
                    self.PressKey('+{VK_HOME}')
                    self.PressKey(str(y_range[curStep]))
                    last_y = y_range[curStep]
                if (z_range[curStep] != last_z):
                    self.ClickMouse(1648+58,246+12)
                    self.PressKey('+{VK_HOME}')
                    self.PressKey(str(z_range[curStep]))
                    last_z = z_range[curStep]
                if (tilt_range[curStep] != last_tilt):
                    self.ClickMouse(1648+58,278+12)
                    self.PressKey('+{VK_HOME}')
                    self.PressKey(str(tilt_range[curStep]))
                    last_tilt = tilt_range[curStep]
                if (rot_range[curStep] != last_rot):
                    self.ClickMouse(1648+58,309+12)
                    self.PressKey('+{VK_HOME}')
                    self.PressKey(str(rot_range[curStep]))
                    last_rot = rot_range[curStep]
                
                self.ClickMouse(1757+50,145+12)
            else:
                print("Cannot find microscope control. Exiting.")
                break

            self.mainWindow.focus_force()
            time.sleep(10)
            self.statText.config(text="Acquiring")

            # Saving
            hFoundWnd = self.FocusTheDesiredWnd()
            if(hFoundWnd != 0):
                filename = filepath.replace('/','\\') + "\\" + filebase + "_" + str(curStep) + ".tif"

                if (acq_style == 1):
                    self.PressKey('{VK_F4}')
                    time.sleep(3)
                elif (acq_style == 0):
                    self.PressKey('{VK_F2}')
                    time.sleep(60)

                quadfile = filename
                self.PressKey(quadfile)
                self.PressKey('{VK_RETURN}')

            else:
                print("Cannot find microscope control. Exiting.")
                break

            # Saving screenshot (must use Snipping Tool because Paint is not installed?????????? FEI?????)
            self.FocusSnip()
            self.PressKey('^n')
            time.sleep(1)
            pywinauto.mouse.press(coords=(0,0))
            time.sleep(0.5)
            pywinauto.mouse.release(coords=(1920,1200))
            self.MoveMouse(500,500)
            time.sleep(1)
            self.PressKey('^s')
            ss_filename = filepath.replace('/','\\') + "\\" + filebase + "_" + str(curStep) + "_ss.png"
            self.PressKey(ss_filename)
            self.PressKey('{VK_RETURN}')

            et = time.time()
            cumulTime = cumulTime + et - st
            avgPerImg = cumulTime/(curStep+1)
            estTimeRemain = avgPerImg*(len(steps)-(curStep+1))
            self.estTimeVal.config(text=str(estTimeRemain) + " s")
            self.experProgBar['value'] = curStep

        self.statText.config(text="Finished")
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
        self.xStepEntry.delete(0, "end")
        self.xStepEntry.insert(0, f.readline())
        self.yStartEntry.delete(0, "end")
        self.yStartEntry.insert(0, f.readline())
        self.yEndEntry.delete(0, "end")
        self.yEndEntry.insert(0, f.readline())
        self.yStepEntry.delete(0, "end")
        self.yStepEntry.insert(0, f.readline())
        self.zStartEntry.delete(0, "end")
        self.zStartEntry.insert(0, f.readline())
        self.zEndEntry.delete(0, "end")
        self.zEndEntry.insert(0, f.readline())
        self.zStepEntry.delete(0, "end")
        self.zStepEntry.insert(0, f.readline())
        self.tiltStartEntry.delete(0, "end")
        self.tiltStartEntry.insert(0, f.readline())
        self.tiltEndEntry.delete(0, "end")
        self.tiltEndEntry.insert(0, f.readline())
        self.tiltStepEntry.delete(0, "end")
        self.tiltStepEntry.insert(0, f.readline())
        self.rotStartEntry.delete(0, "end")
        self.rotStartEntry.insert(0, f.readline())
        self.rotEndEntry.delete(0, "end")
        self.rotEndEntry.insert(0, f.readline())
        self.rotStepEntry.delete(0, "end")
        self.rotStepEntry.insert(0, f.readline())
        self.distributeVar.set(int(f.readline()))
        self.acqParamVar.set(int(f.readline()))
        f.close()
        return

if __name__ == '__main__':
    main(sys.argv)