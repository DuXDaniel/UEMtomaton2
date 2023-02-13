import math
import time
import sys
import socket
import subprocess
import random
import datetime
import threading
import queue
import os.path as path
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import PhotoImage
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog

def main(argv):
    windowWidget = WidgetGallery()

class WidgetGallery():
    def __init__(self, parent=None):
        self.totPoints = 0
        self.spdlght = 299792458 # m/s
        self.curZero = 0 # As of August 16th, 2019 position 293.527 mm on the delay stage corresponds to 0 ps
        self.mm_to_ps = 1e12 / self.spdlght / 1000 * 2 # accounts for retroreflector
        self.curdelTime = 0 # current delay position in terms of time relative to some fixed position on the delay stage
        self.curDistPoint = 0 # current delay position in space relative to home setting from delay interface
        self.positionFeedback = 0.
        self.delayConnected = 0
        self.butPressMeantime = 0 # indicates whether a button has been pressed while a run is occuring (pause, play, or stop 
        self.cycleNum = 1 # number of cycles in the run
        self.runStat = 0 # indicates the status of a currently running scan. 0 indicates not running. 1 indicates running. 2 indicates a pause. 3 indicates a stop command which will switch to 0.
        self.randomized = 0 # indicates whether timepoints are randomized
        self.curExpArr = []
        self.fullTimeptArr = []
        self.SIS_acq_time = -1 # selective in situ mode acquisition time
        self.SIS_time_between = -1 # selective in situe mode time skipped between saves
        self.SIS_total_time = -1 # total time spent saving the images.
        self.wait = 0.5 # seconds to sleep for threads
        self.timeout = 3600 * 4 # image acquisition timeout ticks (an hour)

        # Cam Queue
        self.camRunnerQueue = queue.Queue()
        self.delValUpCamQueue = queue.Queue()

        # Delay Queue
        self.delayRunnerQueue = queue.Queue()
        self.delValUpQueue = queue.Queue()
        self.delValCommQueue = queue.Queue()

        self.mainWindow = tk.Tk()
        self.mainWindow.title("UEMtomaton")
        icon = PhotoImage(file = './Icons/UEMtomaton_icon_32.png')
        self.mainWindow.protocol("WM_DELETE_WINDOW", self.fullClose)
        self.mainWindow.iconphoto(False, icon)
        self.mainWindow.grid_rowconfigure(0, weight=1)
        self.mainWindow.grid_columnconfigure(0, weight=1)

        self.screen_width = self.mainWindow.winfo_screenwidth()
        self.screen_height = self.mainWindow.winfo_screenheight()

        self.win_width = round(self.screen_width*0.39)
        self.win_height = round(self.screen_height*0.7)
        self.spawnPos_x = round(self.screen_width/2-self.win_width/2)
        self.spawnPos_y = round(self.screen_height/2-self.win_height/2)

        self.mainWindow.geometry(str(self.win_width)+"x"+str(self.win_height)+"+"+str(self.spawnPos_x)+"+"+str(self.spawnPos_y))

        self.titleFontSize = round(self.win_height*0.02)
        self.normFontSize = round(self.win_height*0.01)
        self.titleLabel = ttk.Label(
            self.mainWindow,
            text="UEM Automaton",
            font=("Arial", self.titleFontSize),
            justify="left"
        )

        self.titleLabel.grid(column=0, row=0, padx=5, pady=5, sticky="nw")

        # Creating Notebook

        self.frameSelect = ttk.Notebook(self.mainWindow, width=round(self.win_width*0.99), height=round(self.win_height*0.91))
        self.cameraFrame = ttk.Frame(self.frameSelect)
        self.delayFrame = ttk.Frame(self.frameSelect)
        self.SISFrame = ttk.Frame(self.frameSelect)
        self.settingFrame = ttk.Frame(self.frameSelect)

        self.frameSelect.add(self.cameraFrame, text="Camera Side")
        self.frameSelect.add(self.delayFrame, text="Delay Side")
        self.frameSelect.add(self.SISFrame, text="In-Situ Select")
        self.frameSelect.add(self.settingFrame, text="Settings")

        self.frameSelect.grid(column=0, row=1, padx=5, pady=5, sticky="nw")

        # Settings Frame
        self.camSettingFrame = ttk.Frame(self.settingFrame)
        self.camSettingLabel = ttk.Label(
            self.camSettingFrame,
            text="Camera Settings",
            font=("Arial",self.normFontSize),
            justify="left"
        )
        self.camIPLabel = ttk.Label(
            self.camSettingFrame,
            text="Camera Computer IP: ",
            font=("Arial",self.normFontSize),
            justify="right"
        )
        self.camIPEntry = ttk.Entry(
            self.camSettingFrame,
            width=round(self.win_width*0.023)
        )
        self.cameraScriptLabel = ttk.Label(
            self.camSettingFrame,
            text="Camera Script Location: ",
            font=("Arial",self.normFontSize),
            justify="right"
        )
        self.cameraScriptEntry = ttk.Entry(
            self.camSettingFrame,
            width=round(self.win_width*0.023)
        )
        self.cameraScriptBrowse = ttk.Button(
            self.camSettingFrame,
            text="Browse",
            command=lambda: self.browseCamScript_Click()
        )
        self.SISScriptLabel = ttk.Label(
            self.camSettingFrame,
            text="In-Situ Script Location: ",
            font=("Arial",self.normFontSize),
            justify="right"
        )
        self.SISScriptEntry = ttk.Entry(
            self.camSettingFrame,
            width=round(self.win_width*0.023)
        )
        self.SISScriptBrowse = ttk.Button(
            self.camSettingFrame,
            text="Browse",
            command=lambda: self.browseSISScript_Click()
        )

        self.delaySettingFrame = ttk.Frame(self.settingFrame)
        self.delaySettingLabel = ttk.Label(
            self.delaySettingFrame,
            text="Delay Settings",
            font=("Arial",self.normFontSize),
            justify="left"
        )
        self.delayIPLabel = ttk.Label(
            self.delaySettingFrame,
            text="Delay Computer IP: ",
            font=("Arial",self.normFontSize),
            justify="right"
        )
        self.delayIPEntry = ttk.Entry(
            self.delaySettingFrame,
            width=round(self.win_width*0.023)
        )
        self.timeZeroLabel = ttk.Label(
            self.delaySettingFrame,
            text="Time Zero Position: ",
            font=("Arial",self.normFontSize),
            justify="right"
        )
        self.timeZeroEntry = ttk.Entry(
            self.delaySettingFrame,
            width=round(self.win_width*0.023),
            validate="focusout",
            validatecommand=lambda: self.timeZeroPositionSetting_TextChanged()
        )
        self.delayScriptLabel = ttk.Label(
            self.delaySettingFrame,
            text="Delay Script Location: ",
            font=("Arial",self.normFontSize),
            justify="right"
        )
        self.delayScriptEntry = ttk.Entry(
            self.delaySettingFrame,
            width=round(self.win_width*0.023)
        )
        self.delayScriptBrowse = ttk.Button(
            self.delaySettingFrame,
            text="Browse",
            command=lambda: self.browseDelayScript_Click()
        )

        self.saveLoadFrame = ttk.Frame(self.settingFrame)
        self.loadButton = ttk.Button(
            self.saveLoadFrame,
            text="Load Settings",
            command=lambda: self.loadSettingsButton_Click()
        )
        self.restoreButton = ttk.Button(
            self.saveLoadFrame,
            text="Restore Settings",
            command=lambda: self.DefaultSettingsRestore_Click()
        )
        self.saveButton = ttk.Button(
            self.saveLoadFrame,
            text="Save Settings",
            command=lambda: self.SaveSettingsButton_Click()
        )

        self.camSettingLabel.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.camIPLabel.grid(column=0, row=1, padx=5, pady=5, sticky="e")
        self.camIPEntry.grid(column=1, row=1, padx=5, pady=5, sticky="w")
        self.cameraScriptLabel.grid(column=0, row=2, padx=5, pady=5, sticky="e")
        self.cameraScriptEntry.grid(column=1, row=2, padx=5, pady=5, sticky="w")
        self.cameraScriptBrowse.grid(column=2, row=2, padx=5, pady=5, sticky="w")
        self.SISScriptLabel.grid(column=0, row=3, padx=5, pady=5, sticky="e")
        self.SISScriptEntry.grid(column=1, row=3, padx=5, pady=5, sticky="w")
        self.SISScriptBrowse.grid(column=2, row=3, padx=5, pady=5, sticky="w")

        self.delaySettingLabel.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.delayIPLabel.grid(column=0, row=1, padx=5, pady=5, sticky="e")
        self.delayIPEntry.grid(column=1, row=1, padx=5, pady=5, sticky="w")
        self.timeZeroLabel.grid(column=0, row=2, padx=5, pady=5, sticky="e")
        self.timeZeroEntry.grid(column=1, row=2, padx=5, pady=5, sticky="w")
        self.delayScriptLabel.grid(column=0, row=3, padx=5, pady=5, sticky="e")
        self.delayScriptEntry.grid(column=1, row=3, padx=5, pady=5, sticky="w")
        self.delayScriptBrowse.grid(column=2, row=3, padx=5, pady=5, sticky="w")

        self.loadButton.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.restoreButton.grid(column=1, row=0, padx=5, pady=5, sticky="w")
        self.saveButton.grid(column=2, row=0, padx=5, pady=5, sticky="e")

        self.camSettingFrame.grid(column=0, row=0, padx=5, pady=5, sticky="nw")
        self.delaySettingFrame.grid(column=1, row=0, padx=5, pady=5, sticky="nw")
        self.saveLoadFrame.grid(column=0, row=1, columnspan=2, padx=5, pady=5)

        # SIS Frame
        self.SISDescriptionFrame = ttk.Frame(self.SISFrame)
        self.SISDescriptionLabel = ttk.Label(
            self.SISDescriptionFrame,
            text="This tab is intended for selective acquisition of images in the OneView in situ mode. It is designed to allow the acquisition of images at certain integer intervals of image acquisition times (such as every other, every three, etc.). Using this simple additional feature will begin a script that runs off of the information input below. Be sure to match acquisition times between the camera and UEMtomaton.",
            wraplength=round(self.win_width*0.95),
            justify="left",
            font=("Arial",round(self.normFontSize*1.5))
        )
            
        self.SISFileFrame = ttk.Frame(self.SISFrame)
        self.SISFilepathLabel = ttk.Label(
            self.SISFileFrame,
            text="Filepath: ",
            font=("Arial",round(self.normFontSize*1.5))
        )
        self.SISFilepathEntry = ttk.Entry(
            self.SISFileFrame,
        )
        self.SISFilepathBrowse = ttk.Button(
            self.SISFileFrame,
            text="Browse",
            command=lambda: self.browseSIS_Click()
        )
        self.SISFilebaseLabel = ttk.Label(
            self.SISFileFrame,
            text="Filebase: ",
            font=("Arial",round(self.normFontSize*1.5))
        )
        self.SISFilebaseEntry = ttk.Entry(
            self.SISFileFrame,
        )

        self.SISAcqFrame = ttk.Frame(self.SISFrame)
        self.SISAcqTimeLabel = ttk.Label(
            self.SISAcqFrame,
            text="Acquisition Time (s): ",
            font=("Arial",round(self.normFontSize*1.5))
        )
        self.SISAcqTimeEntry = ttk.Entry(
            self.SISAcqFrame
        )
        self.SISWaitTimeLabel = ttk.Label(
            self.SISAcqFrame,
            text="Wait Time (s): ",
            font=("Arial",round(self.normFontSize*1.5))
        )
        self.SISWaitTimeEntry = ttk.Entry(
            self.SISAcqFrame
        )

        self.SISButtonFrame = ttk.Frame(self.SISFrame)
        self.SISBeginButton = ttk.Button(
            self.SISButtonFrame,
            text="Begin Acquisition",
            command=lambda: self.selectiveInSitu_Click()
        )
        self.SISEndButton = ttk.Button(
            self.SISButtonFrame,
            text="End Acquisition",
            command=lambda: self.selectiveInSituEnd_Click()
        )

        self.SISDescriptionLabel.grid(column=0, row=0, padx=5, pady=5, sticky="w")

        self.SISFilepathLabel.grid(column=0, row=0, padx=5, pady=5, sticky="e")
        self.SISFilepathEntry.grid(column=1, row=0, padx=5, pady=5)
        self.SISFilepathBrowse.grid(column=2, row=0, padx=5, pady=5, sticky="w")
        self.SISFilebaseLabel.grid(column=0, row=1, padx=5, pady=5, sticky="e")
        self.SISFilebaseEntry.grid(column=1, row=1, padx=5, pady=5)

        self.SISAcqTimeLabel.grid(column=0, row=0, padx=5, pady=5, sticky="e")
        self.SISAcqTimeEntry.grid(column=1, row=0, padx=5, pady=5)
        self.SISWaitTimeLabel.grid(column=2, row=0, padx=5, pady=5, sticky="e")
        self.SISWaitTimeEntry.grid(column=3, row=0, padx=5, pady=5)

        self.SISBeginButton.grid(column=0, row=0, padx=5, pady=5, sticky="nesw")
        self.SISEndButton.grid(column=1, row=0, padx=5, pady=5, sticky="nesw")

        self.SISDescriptionFrame.grid(column=0, row=0, padx=5, pady=5, sticky="ne")
        self.SISFileFrame.grid(column=0, row=1, padx=5, pady=5, sticky="nw")
        self.SISAcqFrame.grid(column=0, row=2, padx=5, pady=5, sticky="nw")
        self.SISButtonFrame.grid(column=0, row=3, padx=5, pady=5, sticky="nw")

        # Delay Stage Frame
        self.delayStartButtonFrame = ttk.Frame(self.delayFrame)
        self.delayConnectButton = ttk.Button(
            self.delayStartButtonFrame,
            text="Connect to\n Delay Stage",
            command=lambda: self.delayConnect_Click()
        )
        self.initServerButton = ttk.Button(
            self.delayStartButtonFrame,
            text="Initialize Server",
            command=lambda: self.ServInitButton_Click()
        )

        self.delayEndButtonFrame = ttk.Frame(self.delayFrame)
        self.disconDelayButton = ttk.Button(
            self.delayEndButtonFrame,
            text="Disconnect Server",
            command=lambda: self.DisconServ_Click()
        )

        self.delayPosFrame = ttk.Frame(self.delayFrame)
        self.delayPosLabel = ttk.Label(
            self.delayPosFrame,
            text="Delay Stage Position",
            font=("Arial",self.normFontSize)
        )
        self.delayConnectionLabel = ttk.Label(
            self.delayPosFrame,
            text="Connection Status: ",
            font=("Arial",self.normFontSize)
        )
        self.delayConnectionStatus = ttk.Label(
            self.delayPosFrame,
            text="---",
            font=("Arial",self.normFontSize)
        )
        self.delayPositionTimeLabel = ttk.Label(
            self.delayPosFrame,
            text="Temporal Position: ",
            font=("Arial",self.normFontSize)
        )
        self.delayPositionTimeStatus = ttk.Label(
            self.delayPosFrame,
            text="---",
            font=("Arial",self.normFontSize)
        )
        self.delayPositionSpaceLabel = ttk.Label(
            self.delayPosFrame,
            text="Spatial Position: ",
            font=("Arial",self.normFontSize)
        )
        self.delayPositionSpaceStatus = ttk.Label(
            self.delayPosFrame,
            text="---",
            font=("Arial",self.normFontSize)
        )

        self.delayMessageFrame = ttk.Frame(self.delayFrame)
        self.delayMessageBox = ScrolledText(
            self.delayMessageFrame,
            width=round(self.win_width*0.113)
        )

        self.delayConnectButton.grid(column=0, row=0, padx=5, pady=5, sticky="nesw")
        self.initServerButton.grid(column=0, row=1, padx=5, pady=5, sticky="nesw")
        
        self.disconDelayButton.grid(column=0, row=0, padx=5, pady=5, sticky="nesw")

        self.delayPosLabel.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.delayConnectionLabel.grid(column=0, row=1, padx=5, pady=5, sticky="e")
        self.delayConnectionStatus.grid(column=1, row=1, padx=5, pady=5, sticky="w")
        self.delayPositionTimeLabel.grid(column=0, row=2, padx=5, pady=5, sticky="e")
        self.delayPositionTimeStatus.grid(column=1, row=2, padx=5, pady=5, sticky="w")
        self.delayPositionSpaceLabel.grid(column=0, row=3, padx=5, pady=5, sticky="e")
        self.delayPositionSpaceStatus.grid(column=1, row=3, padx=5, pady=5, sticky="w")

        self.delayMessageBox.grid(column=0, row=0, padx=5, pady=5, sticky="w")

        self.delayStartButtonFrame.grid(column=0, row=0, padx=5, pady=5, sticky="nw")
        self.delayEndButtonFrame.grid(column=1, row=0, padx=5, pady=5, sticky="ne")
        self.delayPosFrame.grid(column=0, row=1, columnspan=2, padx=5, pady=5, sticky="nw")
        self.delayMessageFrame.grid(column=0, row=2, columnspan=2, padx=5, pady=5, sticky="nw")

        # Camera Side Frame
            # Camera Connect Frame
        self.camConnFrame = ttk.Frame(self.cameraFrame)
        self.camConnButton = ttk.Button(
            self.camConnFrame,
            text="Connect to Server",
            command=lambda: self.camConnToDelay_Click()
        )
        self.camDisconnButton = ttk.Button(
            self.camConnFrame,
            text="Disconnect from Server",
            command=lambda: self.DisconCam_Click()
        )
        self.camConnSpacer = ttk.Label(
            self.camConnFrame,
            text="Connection Status:",
            font=("Arial",self.normFontSize)
        )
        self.camConnSpacer2 = ttk.Label(
            self.camConnFrame,
            text="---",
            font=("Arial",self.normFontSize)
        )
        self.camDelPosSpaceLabel = ttk.Label(
            self.camConnFrame,
            text="Delay Stage Position (space): ",
            font=("Arial",self.normFontSize)
        )
        self.camDelPosSpaceStatus = ttk.Label(
            self.camConnFrame,
            text="---",
            font=("Arial",self.normFontSize)
        )
        self.camDelPosTimeLabel = ttk.Label(
            self.camConnFrame,
            text="Delay Stage Position (time): ",
            font=("Arial",self.normFontSize)
        )
        self.camDelPosTimeStatus = ttk.Label(
            self.camConnFrame,
            text="---",
            font=("Arial",self.normFontSize)
        )

        self.camFileFrame = ttk.Frame(self.cameraFrame)
        self.camFilepathLabel = ttk.Label(
            self.camFileFrame,
            text="Filepath: ",
            font=("Arial",self.normFontSize)
        )
        self.camFilepathEntry = ttk.Entry(
            self.camFileFrame
        )
        self.camFilebaseLabel = ttk.Label(
            self.camFileFrame,
            text="Filename Base: ",
            font=("Arial",self.normFontSize)
        )
        self.camFilebaseEntry = ttk.Entry(
            self.camFileFrame
        )
        self.camBrowseButton = ttk.Button(
            self.camFileFrame,
            text="Browse",
            command=lambda: self.BrowseFilePath_Click()
        )
        self.camExtFrame = ttk.Frame(
            self.camFileFrame
        )

        self.camConnButton.grid(column=0, row=0, rowspan=2, padx=5, pady=5, sticky="nesw")
        self.camDisconnButton.grid(column=1, row=0, rowspan=2, padx=5, pady=5, sticky="nesw")
        self.camConnSpacer.grid(column=2, row=0, padx=5, pady=5)
        self.camConnSpacer2.grid(column=2, row=1, padx=5, pady=5)
        self.camDelPosSpaceLabel.grid(column=3, row=0, padx=5, pady=5, sticky="e")
        self.camDelPosSpaceStatus.grid(column=4, row=0, padx=5, pady=5, sticky="w")
        self.camDelPosTimeLabel.grid(column=3, row=1, padx=5, pady=5, sticky="e")
        self.camDelPosTimeStatus.grid(column=4, row=1, padx=5, pady=5, sticky="w")

        self.camFilepathLabel.grid(column=0, row=0, padx=5, pady=5, sticky="e")
        self.camFilepathEntry.grid(column=1, row=0, padx=5, pady=5)
        self.camFilebaseLabel.grid(column=0, row=1, padx=5, pady=5, sticky="e")
        self.camFilebaseEntry.grid(column=1, row=1, padx=5, pady=5)
        self.camBrowseButton.grid(column=2, row=0, padx=5, pady=5, sticky="nesw")
        self.camExtFrame.grid(column=2, row=1, padx=5, pady=5, sticky="w")

        self.camConnFrame.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.camFileFrame.grid(column=0, row=1, padx=5, pady=5, sticky="nw")

            # Experimental Setup Frame

        self.randomizeVar = tk.IntVar(value=0)

        self.makeTimeButton = ttk.Button(
            self.camFileFrame,
            text="Make Timepoints",
            command=lambda: self.MakeTimeButton_Click()
        )
        self.numCycleLabel = ttk.Label(
            self.camFileFrame,
            text="Cycles: ",
            font=("Arial",self.normFontSize)
        )
        self.numCycleEntry = ttk.Entry(
            self.camFileFrame,
            width=round(self.win_width*0.01),
            validate='focusout',
            validatecommand=lambda: self.CycleEntry_TextChanged()
        )
        self.numCycleEntry.insert('0','1')
        self.randomizeCheck = ttk.Checkbutton(
            self.camFileFrame,
            variable=self.randomizeVar,
            offvalue=0,
            onvalue=1,
            command=lambda: self.RandomPoints_CheckedChanged()
        )
        self.randomizeLabel = ttk.Label(
            self.camFileFrame,
            text="Randomize",
            font=("Arial",self.normFontSize)
        )
        self.runScanButton = ttk.Button(
            self.camFileFrame,
            text="Run Scan",
            command=lambda: self.RunScan_Click()
        )

        self.makeTimeButton.grid(column=3, row=0, rowspan=2, padx=5, pady=5, sticky="nesw")
        self.numCycleLabel.grid(column=4, row=0, padx=5, pady=5, sticky="e")
        self.numCycleEntry.grid(column=5, row=0, padx=5, pady=5, sticky="w")
        self.randomizeCheck.grid(column=4, row=1, padx=5, pady=5, sticky="e")
        self.randomizeLabel.grid(column=5, row=1, padx=5, pady=5, sticky="w")
        self.runScanButton.grid(column=6, row=0, rowspan=2, padx=5, pady=5, sticky="nesw")

            # Experiment Status Frame

        self.experimentStatFrame = ttk.Frame(self.cameraFrame)
        self.experTimeRemainLabel = ttk.Label(
            self.experimentStatFrame,
            text="Estimated Time Remaining: ",
            font=("Arial",self.normFontSize)
        )
        self.experTimeRemainStatus = ttk.Label(
            self.experimentStatFrame,
            text="---",
            font=("Arial",self.normFontSize)
        )
        self.experProgBar = ttk.Progressbar(
            self.experimentStatFrame,
            length=round(self.win_width*0.95)
        )
        self.camPauseButton = ttk.Button(
            self.experimentStatFrame,
            text="⏸",
            width=round(self.win_width*0.005),
            command=lambda: self.PauseButton_Click()
        )
        self.timepointTable = ttk.Treeview(
            self.experimentStatFrame,
            height=round(self.win_height*0.58/25),
            column=("Timepoints"),
            show="headings"
        )
        self.timepointTable.heading("Timepoints",text="Timepoints")
        self.timepointTable.column("Timepoints",minwidth=0,width=round(self.win_width*0.15))
        self.stepHistoryTable = ttk.Treeview(
            self.experimentStatFrame,
            columns=("Step","Timepoint","Filename","Status"),
            height=round(self.win_height*0.58/25),
            show="headings"
        )
        self.stepHistoryTable.heading("Step",text="Step")
        self.stepHistoryTable.column("Step",minwidth=0,width=round(self.win_width*0.1))
        self.stepHistoryTable.heading("Timepoint",text="Timepoint")
        self.stepHistoryTable.column("Timepoint",minwidth=0,width=round(self.win_width*0.15))
        self.stepHistoryTable.heading("Filename",text="Filename")
        self.stepHistoryTable.column("Filename",minwidth=0,width=round(self.win_width*0.38))
        self.stepHistoryTable.heading("Status",text="Status")
        self.stepHistoryTable.column("Status",minwidth=0,width=round(self.win_width*0.15))

        self.experTimeRemainLabel.grid(column=1, row=0, padx=5, pady=5, sticky="e")
        self.experTimeRemainStatus.grid(column=2, row=0, padx=5, pady=5, sticky="w")
        self.experProgBar.grid(column=0, row=1, columnspan=3, padx=5, pady=5, sticky="w")
        self.camPauseButton.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.timepointTable.grid(column=0, row=2, padx=5, pady=5, sticky="w")
        self.stepHistoryTable.grid(column=1, row=2, columnspan=2, padx=5, pady=5, sticky="e")

        self.experimentStatFrame.grid(column=0, row=2, columnspan=2, padx=5, pady=5, sticky="w")

            # Cancel Frame

        self.cancelFrame = ttk.Frame(self.cameraFrame)
        self.cancelButton = ttk.Button(
            self.cancelFrame,
            text="⏹",
            width=round(self.win_width*0.005),
            command=lambda: self.StopButton_Click()
        )
        self.camMessageBox = ScrolledText(
            self.cancelFrame,
            height=round(self.win_height*0.001),
            width=round(self.win_width*0.1)
        )

        self.cancelButton.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.camMessageBox.grid(column=1, row=0, padx=5, pady=5, sticky="w")

        self.cancelFrame.grid(column=0, row=3, padx=5, pady=5, sticky="w")

        # Loading Settings
        if (path.exists('UEMtomatonConfig.txt')):
            f = open("UEMtomatonConfig.txt","r")
            curLine = 0
            for line in f:
                if (curLine == 0):
                    self.curZero = float(line)
                    self.timeZeroEntry.delete(0, "end")
                    self.timeZeroEntry.insert(0, line)
                    curLine = 1
                elif (curLine == 1):
                    self.delayIPEntry.delete(0, "end")
                    self.delayIPEntry.insert(0, line)
                    curLine = 2
                elif (curLine == 2):
                    self.cameraScriptEntry.delete(0, "end")
                    self.cameraScriptEntry.insert(0, line)
                    curLine = 3
                elif (curLine == 3):
                    self.SISScriptEntry.delete(0, "end")
                    self.SISScriptEntry.insert(0, line)
                    curLine = 4
                elif (curLine == 4):
                    self.delayScriptEntry.delete(0, "end")
                    self.delayScriptEntry.insert(0, line)
                    curLine = 5
                elif (curLine == 5):
                    self.camIPEntry.delete(0, "end")
                    self.camIPEntry.insert(0, line)
                    curLine = 6
            f.close()
        else:
            self.curZero = 0
            self.timeZeroEntry.delete(0, "end")
            self.timeZeroEntry.insert(0, "0")
            self.delayIPEntry.delete(0, "end")
            self.delayIPEntry.insert(0, "127.0.0.1")
            self.camIPEntry.delete(0, "end")
            self.camIPEntry.insert(0, "127.0.0.1")
            self.cameraScriptEntry.delete(0, "end")
            self.cameraScriptEntry.insert(0, "")
            self.SISScriptEntry.delete(0, "end")
            self.SISScriptEntry.insert(0, "")
            self.delayScriptEntry.delete(0, "end")
            self.delayScriptEntry.insert(0, "")

            upStat = "UEMtomatonConfig.txt not found. Settings set to default values.\r\n"
            self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
            self.camMessageBox.see("end")
        
        self.mainWindow.mainloop()
        return

    def fullClose(self):
        self.cleanupDelay()
        self.cleanupCam()
        self.mainWindow.destroy()

    ### CAMERA CODE HERE--------------------------------------------------------------------------------------------------------------------------------------------
    ''' RunScan_Click
        Begins a scan containing the experimental time point array. Sends a signal to the camera computer that a scan has begun as well.
    '''
    def RunScan_Click(self):
        #####spawnl(P_NOWAIT, "UEMtomatonCameraAcquisition.exe", "UEMtomatonCameraAcquisition.exe", NULL)
        if (path.exists(self.camFilepathEntry.get().strip()) and self.totPoints != 0):
            f = open("AcqStat.txt",'w')
            f.write("1")
            f.close()

            subprocess.Popen(['python',self.cameraScriptEntry.get().strip()])

            self.camMessageBox.insert("end","Initializing run thread.\r\n")
            self.camMessageBox.see("end")

            self.runStat = 1 # set state of run to running

            self.firstPause = 1

            self.totImages = self.totPoints * (self.cycleNum + 1) # The total number of images including the number of times the scan is to be repeated.

            for item in self.stepHistoryTable.get_children():
                self.stepHistoryTable.delete(item)
            
            self.experProgBar['maximum'] = self.totImages
            self.experProgBar['value'] = 0

            self.keepCamRunThread = 1
            self.mainWindow.after(100, self.CameraRunner_DoWork)
            CamRunnerThread(self,self.camRunnerQueue).start()
        else:
            self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+"Invalid experimental parameters.\r\n")
            self.camMessageBox.see("end")

    ''' MakeTimeButton_Click
        Opens the MakeTimepoints.exe program and loads the results into the main program. Uses that data to make the timepoint table, timepoint array, and experimental array.
    '''
    def MakeTimeButton_Click(self):
        # Update the user on making timepoints sub-program.
        upStat = "Started MakeTimepoints applet.\r\n"
        self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.camMessageBox.see("end")

        # Spawns the timepoint maker
        makerApp = TimepointMaker()

        # Grabs the time points from the program.
        upStat = "Grabbing timepoints.\r\n"
        self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.camMessageBox.see("end")

        curRow = 0
        numLines = 0
        totPoints = 0

        for item in self.timepointTable.get_children():
            self.timepointTable.delete(item)
        
        f = open("TimeInputs.txt","r")

        curRow = 0

        curLine = f.readline()

        includeLastLoad = int(curLine)

        for curLine in f:
            curLine = curLine.strip()
            seg = ['','','','','']
            idx = 0
            previdx = 0
            store = 0
            for element in curLine:
                if (element == " "):
                    seg[store] = curLine[previdx:idx]
                    previdx = idx
                    store = store + 1
                idx = idx + 1
            seg[store] = curLine[previdx:-1]

            if (seg[0] != "" and seg[1] != "" and seg[2] != "" and float(seg[2]) != 0):
                valInt = int(math.floor(abs((float(seg[1]) - float(seg[0]))) / float(seg[2])))
         
                addValue = valInt
                if (includeLastLoad == 1):
                    addValue = addValue + 1
                    self.curTimeptArr = np.arange(float(seg[0]),float(seg[1]),float(seg[2]))
                    self.curTimeptArr.append(seg[1])
                else:
                    self.curTimeptArr = np.arange(float(seg[0]),float(seg[1]),float(seg[2]))
                
                self.fullTimeptArr.append(self.curTimeptArr)

                self.totPoints = self.totPoints + addValue

        f.close()
        
        tempTimeptArr = []
        self.expArr = []
        for timeArr in self.fullTimeptArr:
            for timePt in timeArr:
                tempTimeptArr.append(timePt)
        
        self.fullTimeptArr = tempTimeptArr
        
        # Begin assembling the experimental array
        for item in self.timepointTable.get_children():
            self.timepointTable.delete(item)

        for item in self.fullTimeptArr:
            self.expArr.append(item)

        if (self.randomized == 1):
            random.shuffle(self.expArr)
        for a in self.expArr:
            self.timepointTable.insert("",'end',values=(str(a)))

        self.mainWindow.focus()
 
    ''' RandomPoints_CheckedChanged
        Checks if the timepoints should be randomized or not. Adjusts the time array accordingly.
    '''
    def RandomPoints_CheckedChanged(self):
        self.expArr = []
        for item in self.fullTimeptArr:
            self.expArr.append(item)

        for item in self.timepointTable.get_children():
            self.timepointTable.delete(item)

        if (self.randomizeVar.get() == 1):
            self.randomized = 1

            random.shuffle(self.expArr)

            upStat = "Randomized timepoints.\r\n"
            self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
            self.camMessageBox.see("end")
        else:
            self.randomized = 0

            upStat = "Unrandomized timepoints.\r\n"
            self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
            self.camMessageBox.see("end")

        for a in self.expArr:
            self.timepointTable.insert("",'end',values=(str(a)))
 
    ''' DelayComm_DoWork and associated delegate functions. Intended for camera computer
        Will receive the amount of time connected as well as the delay stage readouts.

        Borrows timeTracker_DoWork's delegate UpdateTime-TimeUpdater.
    '''
    def DelayComm_DoWork(self):
        if self.keepDelayCommThread == 1:
            try:
                msg = self.delValUpCamQueue.get_nowait()
                if msg[0] == -1:
                    self.camMessageBox.insert(msg[1],msg[2])
                    self.camConnSpacer2.config(text="---")
                    self.cleanupCam()
                elif msg[0] == 0:
                    self.camConnSpacer2.config(text="Connected")
                elif msg[0] == 1:
                    self.camDelPosTimeStatus.config(text=msg[1])
                    self.camDelPosSpaceStatus.config(text=msg[2])
            except:
                pass

            self.mainWindow.after(100, self.DelayComm_DoWork)
        else:
            self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+"Delay stage communication thread ended.\r\n")
            self.camMessageBox.see("end")
        
    ''' camConnToDelay_Click
        Connects the camera computer to the delay stage server and initiates two background threads
    '''
    def camConnToDelay_Click(self):
        self.delayStat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camCommand_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        upStat = "Searching for connection.\r\n"
        self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.camMessageBox.see("end")

        self.delayStat_client.connect((self.delayIPEntry.get().strip(), 6666))
        upStat = "Delay status connected.\r\n"
        self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.camMessageBox.see("end")
        self.camCommand_client.connect((self.delayIPEntry.get().strip(), 6667))
        upStat = "Camera commands connected.\r\n"
        self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.camMessageBox.see("end")

        upStat = "Starting delay value updater thread.\r\n"
        self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.camMessageBox.see("end")

        self.keepDelayCommThread = 1
        self.mainWindow.after(100, self.DelayComm_DoWork)
        DelValCommFromDelThread(self,self.delValUpCamQueue).start()

    ''' DisconCam_Click
        Disconnects the camera computer from the delay stage and stops the background threads
    '''
    def DisconCam_Click(self):
        self.cleanupCam()
    
    def cleanupCam(self):
        upStat = "Thread stop operation initialized.\r\n"
        self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.camMessageBox.see("end")

        try:
            self.keepScanRunThread = 0
        except:
            upStat = "Attempt to stop camera runner thread failed.\r\n"
            self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
            self.camMessageBox.see("end")

        try:
            self.keepDelayCommThread = 0
        except:
            upStat = "Attempt to close delay value thread failed.\r\n"
            self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
            self.camMessageBox.see("end")

        try:
            self.delayStat_client.shutdown(socket.SHUT_RDWR)
        except:
            upStat = "Attempt to close delay communication socket failed.\r\n"
            self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
            self.camMessageBox.see("end")

        try:
            self.camCommand_client.shutdown(socket.SHUT_RDWR)
        except:
            upStat = "Attempt to close camera runner socket failed.\r\n"
            self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
            self.camMessageBox.see("end")
        
        self.camConnSpacer2.config(text="---")

        upStat = "Socket close operation complete.\r\n"
        self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.camMessageBox.see("end")

    ''' CameraRunner_DoWork and associated delegate functions. Intended for the camera computer.
        self function is the one that handles all initiated scans.
    '''
    def CameraRunner_DoWork(self):
        if self.keepCamRunThread == 1:
            try:
                msg = self.camRunnerQueue.get_nowait()
                if msg[0] == -1:
                    self.runStat = 3
                    self.cleanupCam()
                elif msg[0] == 0:
                    self.camMessageBox.insert(msg[1],msg[2])
                    self.camMessageBox.see("end")
                elif msg[0] == 1:
                    self.stepHistoryTable.insert("",msg[1],values=msg[2])
                elif msg[0] == 2:
                    self.stepHistoryTable.set(self.stepHistoryTable.get_children(msg[1]),3,msg[2])
                elif msg[0] == 3:
                    self.experProgBar['value'] = msg[1]
                elif msg[0] == 4:
                    self.experTimeRemainStatus.config(text=msg[1])
                elif msg[0] == 5:
                    self.experTimeRemainStatus.config(text="Complete")

                    self.experProgBar['maximum'] = 1
                    self.experProgBar['value'] = 0
            except:
                pass

            self.mainWindow.after(100, self.CameraRunner_DoWork)
        else:
            self.camMessageBox.insert('end',str(datetime.datetime.now())+": "+"Camera scan runner thread ended.\r\n")
            self.camMessageBox.see("end")

    ''' PauseButton_Click
        Sets the pause state if another button has not already been pressed.
    '''
    def PauseButton_Click(self):
        if (self.butPressMeantime != 1):
            if (self.pauseButPress == 0):
                self.pauseButPress = 1
                self.butPressMeantime = 1
                self.camPauseButton(text="▶")
            elif (self.pauseButPress == 1):
                self.pauseButPress = 0
                self.butPressMeantime = 0
                self.camPauseButton(text="⏸")

    ''' PlayRun_Click
        Resumes the scan if another button has not already been pressed.
    '''
    def PlayRun_Click(self):
        if (self.butPressMeantime != 1):
            self.runStat = 1
            self.butPressMeantime = 1

    ''' StopButton_Click
        Stops the scan.
    '''
    def StopButton_Click(self):
        self.runStat = 3
        self.butPressMeantime = 1
    
    ''' BrowseFilePath_Click
        Browses for a directory to store DM images in
    '''
    def BrowseFilePath_Click(self):
        imgDirectory = filedialog.askdirectory(title="Select the file path for the images to be saved in")
        self.camFilepathEntry.delete(0, "end")
        self.camFilepathEntry.insert(0, imgDirectory)

    def CycleEntry_TextChanged(self):
        if (self.numCycleEntry.get().strip() == ""):
            self.cycleNum = 1
        else:
            self.cycleNum = int(self.numCycleEntry.get().strip()) # casts the value in numCycleEntry to int
            if (self.cycleNum < 1):
                self.cycleNum = 1
        
        self.numCycleEntry.delete(0, "end")
        self.numCycleEntry.insert(0, str(self.cycleNum)) # sets the value in numCycleEntry to cycleNum. Defensively protects against invalid values by displaying incorrectly typed values as their ASCII to numerical conversion.

    ### DELAY STAGE CODE HERE---------------------------------------------------------------------------------------------------------------------------------------
    def delayConnect_Click(self):
        if (path.exists(self.delayScriptEntry.get().strip())):
            subprocess.Popen(['python',self.DelayScriptEntry.get().strip()])

            self.keepDelValUpdateThread = 1
            self.mainWindow.after(100, self.delayValueUpdater_DoWork)
            DelValUpThread(self, self.delValUpQueue).start()

            self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Delay stage connected.\n")
            self.delayMessageBox.see("end")
            self.delayConnected = 1
        else:
            errDial = tk.Tk()
            errDial.title("Error")
            errLabel = ttk.Label(
                errDial,
                text=self.delayScriptEntry.get().strip() + " not found. Script cannot run."
            )
            errLabel.grid(column=0, row=0, padx=5, pady=5, sticky="nesw")
            self.cleanupDelay()

    def cleanupDelaySockets(self):
        try:
            self.keepScanRunThread = 0
        except:
            self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Failed to end scan runner thread.\r\n")
            self.delayMessageBox.see("end")

        try:
            self.keepDelValUpdateThread = 0
        except:
            self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Failed to end delay value updater thread.\r\n")
            self.delayMessageBox.see("end")

        try:
            self.keepCommDelStatThread = 0
        except:
            self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Failed to end delay communication thread.\r\n")
            self.delayMessageBox.see("end")

        try:
            self.commDelayStat_server.shutdown(socket.SHUT_RDWR)
        except:
            self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Failed to end delay communication server.\r\n")
            self.delayMessageBox.see("end")

        try:
            self.commCamCommand_server.shutdown(socket.SHUT_RDWR)
        except:
            self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Failed to end camera command server.\r\n")
            self.delayMessageBox.see("end")

    def cleanupDelay(self):
        self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Cleaning up delay stage scripts.\n")
        self.delayMessageBox.see("end")
        # Send signal to kill delay stage scripts, sockets, and threads

        self.cleanupDelaySockets()
        self.delayConnectionStatus.config(text="---")

        f = open("connectStatFile.txt","w")
        f.write("2")
        f.close()
        
        self.delayConnected = 0
    
    ''' delayValueUpdater_DoWork and associated delegate functions
        Handles all the work for updating the delay stage value on the delay stage side.
    '''
    def delayValueUpdater_DoWork(self):
        if self.keepDelValUpdateThread == 1:
            try:
                msg = self.delValUpQueue.get_nowait()
                if msg[0] == -1:
                    self.cleanupDelay()
                elif msg[0] == 1:
                    self.delayConnectionStatus.config(text="Connected")
                    self.delayPositionSpaceStatus.config(text=str(self.curDistPoint))
                    self.delayPositionTimeStatus.config(text=str(self.curdelTime))
            except:
                pass
                
            self.mainWindow.after(100, self.delayValueUpdater_DoWork)
        else:
            self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Ended delay value updater thread.\r\n")
            self.delayMessageBox.see("end")

    ''' ScanRunner_DoWork and associated delegate functions
        Handles all the work for organizing the individual steps in a run.
    '''
    def ScanRunner_DoWork(self):
        if self.keepScanRunThread == 1:
            try:
                msg = self.delayRunnerQueue.get_nowait()
                if msg[0] == 1:
                    self.delayMessageBox.insert(msg[0],msg[1])
                    self.delayMessageBox.see("end")
                elif msg[0] == 0:
                    self.cleanupDelay()
            except:
                pass
                
            self.mainWindow.after(1000, self.ScanRunner_DoWork)
        else:
            self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Ended scan runner thread.\r\n")
            self.delayMessageBox.see("end")

    ''' commDelayStat_DoWork
        Passes the delay values to the camera computer.

        UpdateTime-TimeUpdater delegate pair: Used to update the time in the bottom left corner.
    '''
    def commDelayStat_DoWork(self):
        if self.keepCommDelStatThread == 1:
            try:
                msg = self.delValCommQueue.get_nowait()
                if msg[0] == 1:
                    self.mainWindow.after(100, self.commDelayStat_DoWork)
                elif msg[0] == -1:
                    self.cleanupDelay()
            except:
                pass
        else:
            self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Ended delay stat communication thread.\r\n")
            self.delayMessageBox.see("end")
        
    ''' ServInitButton_Click
        Function that will initialize the server. Intended for delay-stage side.

        Uses port 6666 for the delay value communication to the camera computer
        Uses port 6667 for the camera run-status communication to the camera computer 
    '''
    def ServInitButton_Click(self):
        # Update the user on beginning initialization
        upStat = "Initializing server...\r\n"
        self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.delayMessageBox.see("end")

        # standard server startup code -. search Berkeley sockets or c++ sockets for more information
        self.commDelayStat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.commCamCommand_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #self.commDelayStat_server.setblocking(False)
        #self.commCamCommand_server.setblocking(False)

        self.commDelayStat_server.bind((self.camIPEntry.get().strip(),6666))
        self.commCamCommand_server.bind((self.camIPEntry.get().strip(),6667))

        # Update the user on listening for the connection to the delay value client and run client
        upStat = "Listening for incoming connections on ports 6666 and 6667...\r\n"
        self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.delayMessageBox.see("end")

        # Connect to the delay value client
        self.commDelayStat_server.listen(1)
        self.commDelayStat, self.commDelayStat_addr = self.commDelayStat_server.accept()
        upStat = "Delay data transferring through" + str(self.commDelayStat_addr) + ".\r\n"
        self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.delayMessageBox.see("end")

        # Connect to the camera run status client
        self.commCamCommand_server.listen(1)
        self.commCamCommand, self.comCamCommand_addr = self.commCamCommand_server.accept()
        upStat = "Camera data communicating through" + str(self.comCamCommand_addr) + "\r\n"
        self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.delayMessageBox.see("end")
                  
        if (self.delayConnected == 0):
            if (path.exists(self.delayScriptEntry.get().strip())):
                subprocess.Popen(['python',self.delayScriptEntry.get().strip()])

                upStat = "Initializing delay stage value updater thread.\r\n"
                self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
                self.delayMessageBox.see("end")

                self.keepDelValUpdateThread = 1
                self.mainWindow.after(100, self.delayValueUpdater_DoWork)
                DelValUpThread(self, self.delValUpQueue).start()

                self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Delay stage connected.\n")
                self.delayMessageBox.see("end")
                self.delayConnected = 1
            else:
                errDial = tk.Tk()
                errDial.title("Error")
                errLabel = ttk.Label(
                    errDial,
                    text=self.delayScriptEntry.get().strip() + " not found. Script cannot run."
                )
                errLabel.grid(column=0, row=0, padx=5, pady=5, sticky="nesw")
                self.cleanupDelay()
        else:
            self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Delay stage already connected.\r\n")    
            self.delayMessageBox.see("end")   

        upStat = "Initializing delay position communication thread.\r\n"
        self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat) 
        self.delayMessageBox.see("end")

        self.keepCommDelStatThread = 1
        self.mainWindow.after(100, self.commDelayStat_DoWork)
        DelValCommToCamThread(self, self.delValCommQueue).start()
        
        #upStat = "Initializing scan runner thread.\r\n"
        #self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat) 

        #self.keepScanRunThread = 1
        #self.mainWindow.after(1000, self.ScanRunner_DoWork)
        #DelayRunnerThread(self,self.delayRunnerQueue).start()

        #self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+"Ready for scan.\r\n")

    ''' DisconServ_Click
        Close all sockets and execute WSACleanup. Cancel the delay-value communication thread.
    '''
    def DisconServ_Click(self):
        upStat = "Server shutdown initiated.\r\n"
        self.delayMessageBox.insert('end',str(datetime.datetime.now())+": "+upStat)
        self.delayMessageBox.see("end")

        # Requires setting connect text file to "2"
        f = open("connectStatFile.txt","w")
        f.write("2")
        f.close()

        self.delayConnected = 0

        self.cleanupDelay()

    ### SETTINGS CODE HERE------------------------------------------------------------------------------------------------------------------------------------------
    # browseCamScript_Click: Browses for the camera communication script
    def browseCamScript_Click(self):
        scriptDirectory = filedialog.askopenfilename(
            initialdir = "/",
            title="Select the camera script to run"
        )
        self.cameraScriptEntry.delete(0, "end")
        self.cameraScriptEntry.insert(0, scriptDirectory)

    # browseSISScript_Click: Browses for the selective in-situ script
    def browseSISScript_Click(self):
        scriptDirectory = filedialog.askopenfilename(
            initialdir = "/",
            title="Select the selective in-situ script to run"
        )
        self.SISScriptEntry.delete(0, "end")
        self.SISScriptEntry.insert(0, scriptDirectory)

    # browseDelayScript_Click: Browses for the loccation of the delay stage communication script
    def browseDelayScript_Click(self):
        scriptDirectory = filedialog.askopenfilename(
            initialdir = "/",
            title="Select the delay stage control script to run"
        )
        self.delayScriptEntry.delete(0, "end")
        self.delayScriptEntry.insert(0, scriptDirectory)

    # timeZeroPositionSetting_TextChanged: Changes the currently saved time zero
    def timeZeroPositionSetting_TextChanged(self):
        if (not self.timeZeroEntry.get().strip()):
            self.curZero = 0
        else:
            self.curZero = float(self.timeZeroEntry.get().strip()) # casts the value in timeZeroPositionSetting to int
        self.timeZeroEntry.delete(0, "end")
        self.timeZeroEntry.insert(0, str(self.curZero)) # sets the value in timeZeroPositionSetting to curZero. Defensively protects against invalid values by displaying incorrectly typed values as their ASCII to numerical conversion.

    # SaveSettingsButton_Click: Saves the current settings in the running program
    def SaveSettingsButton_Click(self):
        f = open('UEMtomatonConfig.txt', 'w')
        f.write(str(self.curZero) + "\n")
        f.write(self.delayIPEntry.get().strip() + "\n")
        f.write(self.cameraScriptEntry.get().strip() + "\n")
        f.write(self.SISScriptEntry.get().strip() + "\n")
        f.write(self.delayScriptEntry.get().strip() + "\n")
        f.write(self.camIPEntry.get().strip() + "\n")
        f.close()

    # loadSettingsButton_Click: Loads settings from UEMtomatonConfig.txt
    def loadSettingsButton_Click(self):
        curLine = 0

        if (path.exists("UEMtomatonConfig.txt")):
            f = open("UEMtomatonConfig.txt","r")
            for line in f:
                if (curLine == 0):
                    self.curZero = float(line)
                    self.timeZeroEntry.delete(0, "end")
                    self.timeZeroEntry.insert(0, line)
                    curLine = 1
                elif (curLine == 1):
                    self.delayIPEntry.delete(0, "end")
                    self.delayIPEntry.insert(0, line)
                    curLine = 2
                elif (curLine == 2):
                    self.cameraScriptEntry.delete(0, "end")
                    self.cameraScriptEntry.insert(0, line)
                    curLine = 3
                elif (curLine == 3):
                    self.SISScriptEntry.delete(0, "end")
                    self.SISScriptEntry.insert(0, line)
                    curLine = 4
                elif (curLine == 4):
                    self.delayScriptEntry.delete(0, "end")
                    self.delayScriptEntry.insert(0, line)
                    curLine = 5
                elif (curLine == 5):
                    self.camIPEntry.delete(0, "end")
                    self.camIPEntry.insert(0, line)
                    curLine = 6
            f.close()
        else:
            errDial = tk.Tk()
            errDial.title("Error")
            errLabel = ttk.Label(
                errDial,
                text="UEMtomatonConfig.txt not found. Settings unchanged."
            )
            errLabel.grid(column=0, row=0, padx=5, pady=5, sticky="nesw")

    # DefaultSettingsRestore_Click: Restores the default settings
    def DefaultSettingsRestore_Click(self):
        curZero = 0
        self.timeZeroEntry.delete(0, "end")
        self.timeZeroEntry.insert(0, 0)
        
        self.delayIPEntry.delete(0, "end")
        self.delayIPEntry.insert(0, "127.0.0.1")
        
        self.camIPEntry.delete(0, "end")
        self.camIPEntry.insert(0, "127.0.0.1")
        
        self.cameraScriptEntry.delete(0, "end")
        self.cameraScriptEntry.insert(0, "")

        self.SISScriptEntry.delete(0, "end")
        self.SISScriptEntry.insert(0, "")
        
        self.delayScriptEntry.delete(0, "end")
        self.delayScriptEntry.insert(0, "")
    
    ### SELECTIVE IN SITU CODE HERE---------------------------------------------------------------------------------------------------------------------------------
    # browseSIS_Click: Browses for a saving directory for the selective in-situ images to save to
    def browseSIS_Click(self):
        imgDirectory = filedialog.askdirectory(title="Select the image directory")
        self.SISFilepathEntry.config(text=imgDirectory)

    # selectiveInSituEnd_Click: sends a signal to end the selective in-situ script upon click. 
    def selectiveInSituEnd_Click(self):
        f = open('SISSettings.txt', 'w')
        f.write(str(0))
        f.close()

    # selectiveInSitu_Click: begins the selective in-situ script upon click. 
    def selectiveInSitu_Click(self):
        f = open('SISSettings.txt', 'w')
        f.write(str(1) + "\n")
        f.write(self.SISFilepathEntry.get().strip() + "\n")
        f.write(self.SISFilebaseEntry.get().strip() + "\n")
        f.write(str(self.SISAcqTimeEntry) + "\n")
        f.write(str(self.SISWaitTimeEntry))
        f.close()
        # START SIS SCRIPT HERE
        if (path.exists(self.SISScriptEntry.get().strip())):
            subprocess.Popen(['python',self.SISScriptEntry.get().strip()])
            print("hi")
        else:
            errDial = tk.Tk()
            errDial.title("Error")
            errLabel = ttk.Label(
                errDial,
                text=self.SISScriptEntry.get().strip() + " not found. Script cannot run."
            )
            errLabel.grid(column=0, row=0, padx=5, pady=5, sticky="nesw")

##### ASYNCHRONOUS THREADS------------------------------------------------------------------------------------------------------------------------------------------
### DELAY ASYNC THREADS---------------------------------------------------------------------------------------------------------------------------------------------
# DELAY VALUE UPDATER --> Requires repeated GUI updates
class DelValUpThread(threading.Thread):
    def __init__(self, root, queue):
        super().__init__()
        self.root = root
        self.queue = queue

    def run(self):
        f = open("connectStatFile.txt","w")
        f.write("1")
        f.close()
        while (self.root.keepDelValUpdateThread == 1):
            if (path.exists("positionFile.txt")):
                upStat = [1]
                f = open("positionFile.txt","r")
                line = f.readline()
                f.close()
                try:
                    self.root.positionFeedback = float(line)
                except:
                    self.root.positionFeedback = 0.
            else:
                upStat = [-1]

            self.root.curdelTime = (self.root.positionFeedback - self.root.curZero) * self.root.mm_to_ps
            self.root.curDistPoint = self.root.positionFeedback

            if (self.root.delayConnected == 0 and upStat[0] == 1):
                upStat = [-1]

            self.queue.put(upStat)
            time.sleep(self.root.wait)

# DELAY VALUE COMMUNICATOR --> Exit GUI message
class DelValCommToCamThread(threading.Thread):
    def __init__(self, root, queue):
        super().__init__()
        self.root = root
        self.queue = queue

    def run(self):
        while (self.root.keepCommDelStatThread == 1):
            if (path.exists("connectStatFile.txt")):
                f = open("connectStatFile.txt","r")
                line = f.readline().strip()
                if (line != "2"):
                    dc_buffer = str(self.root.curDistPoint) + "|" + str(self.root.curdelTime) + "#" + str(self.root.curDistPoint) + "|" + str(self.root.curdelTime) + "#"
                    try:
                        self.root.commDelayStat.send(dc_buffer.encode())
                        upStat = [1]
                    except:
                        upStat = [-1]
                    
                    dc_buffer = ""
                else:
                    upStat = [-1]

            self.queue.put(upStat)
            time.sleep(self.root.wait)

# SCAN RUNNER COMMUNICATOR --> Requires repeated GUI updates
class DelayRunnerThread(threading.Thread):
    def __init__(self, root, queue):
        super().__init__()
        self.root = root
        self.queue = queue

    def run(self):
        while (self.root.keepScanRunThread == 1):
            upStat = [1,'end',str(datetime.datetime.now())+": "+"Awaiting incoming data.\n"]
            self.queue.put(upStat)
            try:
                camComm_buffer = self.root.commCamCommand.recv(128).decode()
            except:
                upStat = [0]
                self.queue.put(upStat)

            if (camComm_buffer[0] == '1'):
                rundel = 1
            else:
                rundel = 0

            if (rundel == 1):
                delaydata = camComm_buffer[1:]

                camComm_buffer = ''

                self.root.curDistPoint = float(delaydata) / self.root.mm_to_ps + self.root.curZero

                upStat = [1,'end',str(datetime.datetime.now())+": "+"Data received and moving delay stage to position " + delaydata + "\n"]
                self.queue.put(upStat)

                f = open('movementCommFile.txt','w')
                f.write(self.root.curDistPoint + "\n")
                f.write("0")
                f.close()

                while (completionValue != 1):
                    if (path.exists("movementCommFile.txt")):
                        f = open("movementCommFile.txt","r")
                        f.readline()
                        completionStatus = f.readline()
                        completionValue = int(completionStatus)

                    time.sleep(5)

                camComm_buffer[0] = '1'

                try:
                    self.root.commCamCommand.send(camComm_buffer.encode())
                except:
                    upStat = [0]
                    self.queue.put(upStat)
                
                cc_buffer = ''

            time.sleep(self.root.wait)

### CAMERA ASYNC THREADS--------------------------------------------------------------------------------------------------------------------------------------------
# DELAY VALUE COMMUNICATOR --> Requries repeated GUI updates
class DelValCommFromDelThread(threading.Thread):
    def __init__(self, root, queue):
        super().__init__()
        self.root = root
        self.queue = queue

    def run(self):
        while (self.root.keepDelayCommThread == 1):
            try:
                sendval = "-1"
                self.root.delayStat_client.send(sendval.encode())
                upStat = [0]
                self.queue.put(upStat)
            except:
                upStat = [-1,'end',str(datetime.datetime.now())+": "+"Delay stage communication failed, cleaning up.\r\n"]
                self.queue.put(upStat)

            try:
                delrecv_buffer = self.root.delayStat_client.recv(128).decode()
            except:
                upStat = [-1,'end',str(datetime.datetime.now())+": "+"Delay stage communication failed, cleaning up.\r\n"]
                self.queue.put(upStat)

            tracker = 0
            curChar = delrecv_buffer[tracker]
            while (curChar != "#"):
                tracker = tracker + 1
                curChar = delrecv_buffer[tracker]

            initDataIndex = tracker + 1
            tracker = tracker + 1
            curChar = delrecv_buffer[tracker]
            sizeDelayPos = 0
            sizeDelayTime = 0

            while (curChar != '|'):
                sizeDelayPos = sizeDelayPos + 1
                tracker = tracker + 1
                curChar = delrecv_buffer[tracker]

            tracker = tracker + 1
            curChar = delrecv_buffer[tracker]

            while (curChar != '#'):
                sizeDelayTime = sizeDelayTime + 1
                tracker = tracker + 1
                curChar = delrecv_buffer[tracker]

            posdata = delrecv_buffer[initDataIndex:initDataIndex + sizeDelayPos]
            timdata = delrecv_buffer[initDataIndex + sizeDelayPos + 1:initDataIndex + sizeDelayPos + 1 + sizeDelayTime]

            upStat = [1,timdata,posdata]
            self.queue.put(upStat)

            delrecv_buffer = ""
            
            time.sleep(self.root.wait)

#CAM RUNNER COMMUNICATOR --> Requires repeated GUI updates
class CamRunnerThread(threading.Thread):
    def __init__(self, root, queue):
        super().__init__()
        self.root = root
        self.queue = queue
        
        self.curStep = 0 # current step in the entire image set, including repeats
        self.curScan = 0 # current scan
        self.curScanStep = 0 # current step in the scan, not including previous scans
        self.cumulTime = 0

        self.curDelay = 0
        self.toCounter = 0
    
    def ULGWriter(self, Filename, val1, val2, val3, val4, val5, val6, val7, val8, val9):
        curtime = datetime.datetime.now()
        row = int(val8)

        if (row == 1):
            f = open(Filename,"w")

            f.write("[Info Directory\t]\t" + val1 + "\n")
            f.write("[Base Name ]\t" + val2 + "\n")
            f.write("[Date\t]\t" + str(curtime))
            f.write("[Number of Steps\t]\t" + val4 + "\n" + "[Number of Scans\t]\t" + val5 + "\n")
            f.write("\t\n")
            f.write("[Column Descriptions\t]:\tStep,Delay,Scan,Scan Step,File Name,Time\n")
            f.write("\n")
            f.write("\t\n")
            f.write(",,,,,\n")
            f.write(val8 + "," + val6 + "," + val7 + "," + val9 + "," + val3 + "," + str(curtime) + "\n")

            f.close()
        else:
            f = open(Filename,mode='a')

            f.write(val8 + "," + val6 + "," + val7 + "," + val9 + "," + val3 + "," + str(curtime) + "\n")

            f.close()

    def AcqCommWriter(self, Filename, val1, val2, val3, val4, val5, val6):
        f = open(Filename,"w")

        f.write(val1 + "/\n\0")
        f.write(val2 + "\n\0")
        f.write(val3 + "\n\0")
        f.write(val4 + "\n\0")
        f.write(val5 + "\n\0")
        f.write(val6)

        f.close()
    
    def AcqCommStat(self, Filename, curStat):
        f = open(Filename,"w")

        f.write(curStat)
        f.close()

    def run(self):
        while (self.curStep < self.root.totImages and self.root.keepCamRunThread == 1):
            timeInit = time.time()
            try:
                sendVal = "-1"
                self.root.delayStat_client.send(sendVal.encode())
                self.root.camCommand_client.send(sendVal.encode())
            except:
                upStat = [0,'end',str(datetime.datetime.now())+": "+"Network error.\r\n"]
                self.queue.put(upStat)
                self.root.runStat = 3
                upStat = [-1]
                self.queue.put(upStat)

            self.root.butPressMeantime = 0
            camComm_buffer = ''

            timeTrack = time.time()

            addTime = timeTrack - timeInit
            self.cumulTime = self.cumulTime + addTime

            if (self.root.runStat == 1): # Moving delay stage step and preparing for acquisition
                timeInit = time.time()
                if (self.root.firstPause == 0):
                    self.root.firstPause = 1

                    upStat = [0,'end',str(datetime.datetime.now())+": "+"Resumed on step " + str(self.curStep + 1) + ".\r\n"]
                    self.queue.put(upStat)

                if (self.root.totPoints <= 0):
                    self.root.runStat = 3
                    upStat = [0,'end',str(datetime.datetime.now())+": "+"Invalid experimental parameters.\r\n"]
                    self.queue.put(upStat)
                else:
                    curTimePoint = self.root.curExpArr[self.curScanStep]
                    curDistPoint = curTimePoint / self.root.mm_to_ps + self.root.curZero

                    stepString = str(self.curScanStep + 1)
                    timeString = str(curTimePoint)
                    posString = str(curDistPoint)
                    statString = "Moving delay stage...\r\n"

                    upStat = [1,'end',(stepString,timeString,posString,statString)]
                    self.queue.put(upStat)

                    timeVal = str(self.root.curExpArr[self.curScanStep])

                    camComm_buffer = '1'

                    for a in range(1,timeVal.length()+1):
                        camComm_buffer[a] = timeVal[a - 1]

                    camComm_buffer[timeVal.length() + 1] = '|'
                    camComm_buffer[timeVal.length() + 2] = '\0'

                    try:
                        self.root.camCommand_client.send(camComm_buffer.encode())
                    except:
                        upStat = [-1]
                        self.queue.put(upStat)
                    
                    statString = "Acquiring...\r\n"
                    upStat = [2,'end',statString]

                    try:
                        camComm_buffer = self.root.camCommand_client.recv(1024).decode()
                    except:
                        upStat = [-1]
                        self.queue.put(upStat)

                    camComm_buffer = ''

                    recvSignal = 0

                    if (self.root.butPressMeantime == 0):
                        self.root.runStat = 4
                    else:
                        if (self.root.runStat != 3):########################################
                            self.root.runStat = 2

                timeTrack = time.time()

                addTime = timeTrack - timeInit
                self.cumulTime = self.cumulTime + addTime
            elif (self.root.runStat == 2): # Pause signal detected
                # Pause signal, to wait for resume button. Allows current step to complete. Blocking only occurs once here.
                if (self.root.firstPause == 1):
                    upStat = [0,'end',str(datetime.datetime.now())+": "+"Paused on step " + str(self.curStep + 1) + ".\r\n"]
                    self.queue.put(upStat)
                    self.root.firstPause = 0
            elif (self.root.runStat == 3): # Stop signal detected
                # Stop signal, stops and clears everything.
                self.curStep = self.root.totImages
                
                self.AcqCommStat("AcqStat.txt",'-1')
                upStat = [0,'end',str(datetime.datetime.now())+": "+"Stopped on step " + str(self.curStep + 1) + ".\r\n"]
                self.queue.put(upStat)
            elif (self.root.runStat == 4): # Acquisition step before returning to movement step
                timeInit = time.time()
                time.sleep(self.root.wait/10)
                # write all the camera communication files and wait for acquisition before moving on
                
                # ADJUST FOR DECIMAL DELAYS, WITH LIMITER TO A SINGLE DECIMAL PLACE
                self.curDelay = self.root.curTimePoint
                self.curPos = self.root.curDistPoint
                if (self.curDelay % 1 != 0):
                    self.curDelay = round(self.curDelay * 10)
                    self.delayText = "d" + str(int(self.curDelay))
                else:
                    delayText = str(int(self.curDelay))

                curFileName = self.root.camFilebaseEntry.get().strip() + "_" + str(self.curScan) + "_" + str(self.curScanStep + 1) + "_" + delayText
                curFileTot = self.root.camFilepathEntry.get().strip() + curFileName
                ulgFileName = self.root.camFilepathEntry.get().strip() + self.root.camFilebaseEntry.get().strip() + ".ulg"
                
                upStat = [0,'end',str(datetime.datetime.now())+": "+"Updating DM communication for step " + str(self.curStep + 1) + ".\r\n"]
                self.queue.put(upStat)
                # UPDATE CAMERA COMMUNICATION DOCUMENT
                self.AcqCommWriter("AcquisitionSettings.txt", self.root.camFilepathEntry.get().strip(), self.root.camFilebaseEntry.get().strip(), str(self.curScanStep + 1), delayText, str(self.curScan), str(self.curPos))

                upStat = [0,'end',str(datetime.datetime.now())+": "+"Updating ULG file for step " + str(self.curStep + 1) + ".\r\n"]
                self.queue.put(upStat)

                # UPDATE ULG
                self.ULGWriter(ulgFileName, self.root.camFilepathEntry.get().strip(), self.root.camFilebaseEntry.get().strip(), curFileName, str(self.totPoints), str(self.cycleNum), str(self.curScan), str(self.curScanStep + 1), str(self.curStep + 1), str(self.curDelay))

                upStat = [0,'end',str(datetime.datetime.now())+": "+"Waiting to see image name " + curFileTot + " for step " + str(self.curStep + 1) + ".\r\n"]
                self.queue.put(upStat)
                
                self.AcqCommStat("AcqStat.txt",'0')
                f = open("AcqStat.txt",'r')
                statLine = f.readline()
                f.close()
                while (statLine == '0'):
                    f = open("AcqStat.txt",'r')
                    statLine = f.readline()
                    f.close()
                    time.sleep(self.root.wait/2)

                if (statLine == "1"):
                    upStat = [2,'end','Acquired']
                    self.queue.put(upStat)
                    if (self.root.butPressMeantime == 0):
                        self.root.runStat = 1
                    elif (self.root.pauseButPress == 1):
                        if (self.root.runStat != 3):###############################################
                            self.root.runStat = 2
                else:
                    self.root.runStat = 3
                    upStat = [2,'end','Error']
                    self.queue.put(upStat)

                toCounter = 0

                recvSignal = 1

                upStat = [3,self.curStep + 1]
                self.queue.put(upStat)

                self.curStep = self.curStep + 1

                self.curScanStep = self.curStep % self.root.totPoints # current step in the scan

                if ((self.curStep + 1) > self.root.totPoints):
                    self.curScan = (self.curStep - self.curScanStep) / self.root.totPoints # declares the current scan number (begins at zero and increments upwards)

                timeTrack = time.time()

                addTime = timeTrack - timeInit
                self.cumulTime = self.cumulTime + addTime
                timePer = self.cumulTime / (self.curStep + 1)

                timeLeft = round(timePer * (self.root.totPoints*(self.root.cycleNum+1) - self.curStep))
                upStat = [4,str(int(timeLeft)) + " sec"]
                self.queue.put(upStat)

            camComm_buffer = ''

            time.sleep(self.root.wait*2)

        camComm_buffer = '0'

        try:
            self.camCommand_client.send(camComm_buffer.encode())
        except:
            upStat = [-1]
            self.queue.put(upStat)

        camComm_buffer = ''

        upStat = [0,'end',str(datetime.datetime.now())+": "+"Scan complete.\r\n"]
        self.queue.put(upStat)

        upStat = [5]
        self.queue.put(upStat)

### TimepointMaker applet that spawns when requesting to make timepoints
class TimepointMaker():

    def __init__(self, parent=None):
        self.mainWindow = tk.Toplevel()
        self.mainWindow.title("Make Timepoints")
        icon = PhotoImage(file = './Icons/UEMtamaton_icon_32.png')
        self.mainWindow.grid_rowconfigure(0, weight=1)
        self.mainWindow.grid_columnconfigure(0, weight=1)

        self.screen_width = self.mainWindow.winfo_screenwidth()
        self.screen_height = self.mainWindow.winfo_screenheight()

        self.win_width = 525
        self.win_height = 600
        self.spawnPos_x = round(self.screen_width/2-self.win_width/2)
        self.spawnPos_y = round(self.screen_height/2-self.win_height/2)

        self.mainWindow.geometry(str(self.win_width)+"x"+str(self.win_height)+"+"+str(self.spawnPos_x)+"+"+str(self.spawnPos_y))
        
        #### INITIALIZING
        self.includeLast = tk.IntVar(value=0)

        self.saveButton = ttk.Button(
            self.mainWindow,
            text="Save Timepoints",
            command=lambda: self.saveTimepoints_Click()
        )
        self.loadButton = ttk.Button(
            self.mainWindow,
            text="Load Timepoints",
            command=lambda: self.loadTimepoints_Click()
        )
        self.buttonPad = ttk.Label(
            self.mainWindow,
            text=""
        )
        self.buttonPad2 = ttk.Label(
            self.mainWindow,
            text=""
        )
        self.checkLast = ttk.Checkbutton(
            self.mainWindow,
            variable=self.includeLast, 
            onvalue=1, 
            offvalue=0
        )
        self.checkLabel = ttk.Label(
            self.mainWindow,
            text="Include Last Timepoint"
        )
        self.prestoButton = ttk.Button(
            self.mainWindow,
            text="Presto!",
            command=lambda: self.completeButton_Click()
        )
        self.timeTree = ttk.Treeview(
            self.mainWindow,
            columns=("Start","End", "Separation", "Points"),
            show="headings",
            selectmode="browse",
            height=23
        )
        self.timeTree.heading("Start",text="Start")
        self.timeTree.column("Start",minwidth=0,width=120)
        self.timeTree.heading("End",text="End")
        self.timeTree.column("End",minwidth=0,width=120)
        self.timeTree.heading("Separation",text="Separation")
        self.timeTree.column("Separation",minwidth=0,width=120)
        self.timeTree.heading("Points",text="Points")
        self.timeTree.column("Points",minwidth=0,width=120)
        
        self.addButton = ttk.Button(
            self.mainWindow,
            text="Add Row",
            command=lambda: self.addRow()
        )
        self.deleteButton = ttk.Button(
            self.mainWindow,
            text="Delete Row",
            command=lambda: self.deleteRow()
        )
        self.moveUpButton = ttk.Button(
            self.mainWindow,
            text="Move Up",
            command=lambda: self.moveUp()
        )
        self.moveDownButton = ttk.Button(
            self.mainWindow,
            text="Move Down",
            command=lambda: self.moveDown()
        )
        
        #self.buttonPad.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        #self.buttonPad2.grid(column=0, row=1, padx=5, pady=5, sticky="w")
        self.saveButton.grid(column=0, row=0, rowspan=2, padx=5, pady=5, sticky="nesw")
        self.loadButton.grid(column=1, row=0, rowspan=2, padx=5, pady=5, sticky="nesw")
        self.checkLast.grid(column=2, row=0, rowspan=2, padx=5, pady=5, sticky="e")
        self.checkLabel.grid(column=3, row=0, rowspan=2, padx=5, pady=5, sticky="w")
        self.prestoButton.grid(column=4, row=0, rowspan=2, padx=5, pady=5, sticky="nesw")
        self.timeTree.grid(column=0, row=2, columnspan=5, padx=5, pady=5, sticky="w")
        self.addButton.grid(column=0, row=3, rowspan=2, padx=5, pady=5, sticky="nesw")
        self.deleteButton.grid(column=1, row=3, rowspan=2, padx=5, pady=5, sticky="nesw")
        self.moveUpButton.grid(column=2, row=3, rowspan=2, padx=5, pady=5, sticky="nesw")
        self.moveDownButton.grid(column=3, row=3, rowspan=2, padx=5, pady=5, sticky="nesw")
        
        self.mainWindow.mainloop()

    def destroyWindow(self,event):
        self.entryWindow.destroy()

    def destroyButtonClick(self):
        self.entryWindow.destroy()

    def addRow(self):
        treeSelection = self.timeTree.focus()

        self.entryWindow = tk.Toplevel()
        self.entryVar1 = tk.StringVar()
        self.entryVar2 = tk.StringVar()
        self.entryVar3 = tk.StringVar()
        self.entryLabel1 = ttk.Label(
            self.entryWindow,
            text="Start point"
        )
        self.entryLabel2 = ttk.Label(
            self.entryWindow,
            text="End point"
        )
        self.entryLabel3 = ttk.Label(
            self.entryWindow,
            text="Separation"
        )
        self.entry1 = ttk.Entry(
            self.entryWindow,
            textvariable=self.entryVar1
        )
        self.entry2 = ttk.Entry(
            self.entryWindow,
            textvariable=self.entryVar2
        )
        self.entry3 = ttk.Entry(
            self.entryWindow,
            textvariable=self.entryVar3
        )
        self.entry1.bind("<Return>", self.destroyWindow)
        self.entry2.bind("<Return>", self.destroyWindow)
        self.entry3.bind("<Return>", self.destroyWindow)
        self.entryButton = ttk.Button(
            self.entryWindow,
            text="Submit",
            command=lambda: self.destroyButtonClick()
        )
        self.entryButton.bind("<Return>", self.destroyWindow)

        self.entryLabel1.grid(column=0, row=0, padx=5, pady=5)
        self.entry1.grid(column=0, row=1, padx=5, pady=5)
        self.entryLabel2.grid(column=0, row=2, padx=5, pady=5)
        self.entry2.grid(column=0, row=3, padx=5, pady=5)
        self.entryLabel3.grid(column=0, row=4, padx=5, pady=5)
        self.entry3.grid(column=0, row=5, padx=5, pady=5)
        self.entryButton.grid(column=0, row=6, padx=5, pady=5)

        self.entryWindow.focus_force()
        self.entry1.focus()

        self.entryWindow.wait_window()

        entries = [self.entryVar1.get(), self.entryVar2.get(), self.entryVar3.get(), '']

        if (self.entryVar1.get() != "" and self.entryVar2.get() != "" and self.entryVar3.get() != "" and float(self.entryVar3.get()) != 0):
            valInt = int(math.floor(abs((float(self.entryVar2.get()) - float(self.entryVar1.get()))) / float(self.entryVar3.get())))

            addValue = valInt
            if (self.includeLast.get() == 1):
                addValue = valInt + 1
            
            self.timeTree.insert('','end',values=(self.entryVar1.get(),self.entryVar2.get(),self.entryVar3.get(),str(addValue)))
        else:
            self.timeTree.insert('','end',values=(self.entryVar1.get(),self.entryVar2.get(),self.entryVar3.get(),""))

    def saveTimepoints_Click(self):
        f = filedialog.asksaveasfile(mode="w", defaultextension=".txt")

        self.mainWindow.focus()

        curRow = 0

        f.write(str(self.includeLast.get()))

        for line in self.timeTree.get_children():
            f.write("\n")
            for value in self.timeTree.item(line)['values']:
                f.write(str(value) + " ")

            f.write(str(curRow))
            curRow = curRow + 1

        f.close()

        self.mainWindow.focus()

    def loadTimepoints_Click(self):
        for item in self.timeTree.get_children():
            self.timeTree.delete(item)

        openTimeDialog = filedialog.askopenfilename()
        self.mainWindow.focus()
        
        f = open(openTimeDialog)

        curRow = 0

        curLine = f.readline()

        includeLastLoad = int(curLine)

        if (includeLastLoad == 1):
            self.includeLast = tk.IntVar(value=1)
        else:
            self.includeLast = tk.IntVar(value=0)
            
        curLine = f.readline()

        while (curLine != ""):
            seg = ['','','','','']
            idx = 0
            previdx = 0
            store = 0
            for element in curLine:
                if (element == " "):
                    seg[store] = curLine[previdx:idx]
                    previdx = idx
                    store = store + 1
                idx = idx + 1
            seg[store] = curLine[previdx:-1]

            if (seg[0] != "" and seg[1] != "" and seg[2] != "" and float(seg[2]) != 0):
                valInt = int(math.floor(abs((float(seg[1]) - float(seg[0]))) / float(seg[2])))

                addValue = valInt
                if (self.includeLast.get() == 1):
                    addValue = valInt + 1
                self.timeTree.insert("",'end',values=(seg[0], seg[1], seg[2], str(addValue)))
            else:
                self.timeTree.insert("",'end',values=(seg[0], seg[1], seg[2], ''))

            curRow = curRow + 1
            
            curLine = f.readline()

        f.close()

        self.mainWindow.focus()

    def completeButton_Click(self):
        curRow = 0

        f = open('TimeInputs.txt','w')

        f.write(str(self.includeLast.get()))

        for line in self.timeTree.get_children():
            f.write("\n")
            for value in self.timeTree.item(line)['values']:
                f.write(str(value) + " ")

            f.write(str(curRow))
            curRow = curRow + 1

        f.close()

        print("Saved times and returning.\n")

        self.mainWindow.quit()
        self.mainWindow.destroy()
        print("Window destroyed.\n")

    def deleteRow(self):
        selected = self.timeTree.focus()
        index = self.timeTree.index(selected)
        rowChild = self.timeTree.get_children()[index]
        self.timeTree.delete(rowChild)

    def moveUp(self):
        selected = self.timeTree.focus()
        index = self.timeTree.index(selected)
        rowChild = self.timeTree.get_children()[index]

        if (index >= 1):
            self.timeTree.insert("", index - 1, values=self.timeTree.item(rowChild)['values'])
            newRow = self.timeTree.get_children()[index - 1]
            self.timeTree.delete(self.timeTree.get_children()[index+1])
            self.timeTree.focus(newRow)
            self.timeTree.selection_set(newRow)

    def moveDown(self):
        selected = self.timeTree.focus()
        index = self.timeTree.index(selected)
        rowChild = self.timeTree.get_children()[index]
        
        numRows = len(self.timeTree.get_children())

        if (index <= numRows-2):
            self.timeTree.insert("", index + 2, values=self.timeTree.item(rowChild)['values'])
            newRow = self.timeTree.get_children()[index + 2]
            self.timeTree.delete(self.timeTree.get_children()[index])
            self.timeTree.focus(newRow)
            self.timeTree.selection_set(newRow)

if __name__ == '__main__':
    main(sys.argv)
