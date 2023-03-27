import sys
import pywinauto
import time
import tkinter as tk
from tkinter import simpledialog
from pythonnet import load
from ctypes import *

SHUTTER_CTRL = CDLL("C:\\Users\\dudan\\Desktop\\Work\\Columbia\\Software\\UEMtomaton 2.0\\UEMtomaton\\NanoSEM_Acquisition\\SC10 C++ SDK\\SC10CommandLib_x64.dll")

#print(type(SHUTTER_CTRL))
deviceList = SHUTTER_CTRL.List()
print(deviceList)

pumpHdl = SHUTTER_CTRL.Open()
probeHdl = SHUTTER_CTRL.Open()
