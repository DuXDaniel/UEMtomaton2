import sys
import pywinauto
import time
import tkinter as tk
from tkinter import simpledialog
from pythonnet import load
from ctypes import *

SHUTTER_CTRL = CDLL("./NanoSEM_Acquisition/SC10 C++ SDK/SC10CommandLib_x64.dll")
        
def PressKey(keypress):
    ###### Press on keyboard the passed request
    pywinauto.keyboard.send_keys(keypress,pause=0.05)
    time.sleep(0.01)

def FocusTheDesiredWnd():
    searchApp = pywinauto.application.Application()
    try:
        searchApp.connect(title_re=r'.*xT microscope Control.*', found_index = 0)
        
        restoreApp = searchApp.top_window()
        restoreApp.minimize()
        restoreApp.restore()
        restoreApp.set_focus()
        return restoreApp
    except:
        return 0

def main(argv):
    ROOT = tk.Tk()

    ROOT.withdraw()
    # the input dialog
    USER_INP = float(simpledialog.askstring(title="Acquisition Time", prompt="Acquisition time:"))

    hFoundWnd = FocusTheDesiredWnd()

    f = open("AcqStat.txt",'r')
    statLine = f.readline()
    f.close()

    re_align_time = 600 # seconds before realigning the photoelectrons

    timeout = 60 # seconds to attempt window focusing before a timeout command is sent

    timeout_start = 0
    timeout_cond = 0

    st = time.time()
    prev_statLine = "1"
    while (statLine != "-1"):
        f = open("AcqStat.txt",'r')
        statLine = f.readline()
        f.close()

        if (statLine == "0"):
            if (prev_statLine == "2"):
                st = time.time()
            hFoundWnd = FocusTheDesiredWnd()
            if(hFoundWnd != 0):
                timeout_cond = 0
                f = open("AcquisitionSettings.txt",'r')
                filepath = f.readline()
                filebase = f.readline()
                curScanStep = f.readline()
                curDelay = f.readline()
                curScan = f.readline()
                curPos = f.readline()
                f.close()

                base_filename = filepath + "\\" + filebase + "_" + curScan + "_" + curScanStep + "_" + curDelay

                # Background
                PressKey('{VK_F2}')

                time.sleep(USER_INP + 3)

                quadfile = base_filename + "_bg.tif"
                PressKey(quadfile)
                PressKey('{VK_RETURN}')
                time.sleep(1)

                # Photoelectrons
                # Add shutter open comnmand to probe
                PressKey('{VK_F2}')

                time.sleep(USER_INP + 3)

                quadfile = base_filename + "_pr.tif"
                PressKey(quadfile)
                PressKey('{VK_RETURN}')
                time.sleep(1)

                # Pump-Probe
                # Add shutter open comnmand to pump
                PressKey('{VK_F2}')

                time.sleep(USER_INP + 3)

                quadfile = base_filename + "_pp.tif"
                PressKey(quadfile)
                PressKey('{VK_RETURN}')
                time.sleep(1)

                # Pump
                # Add shutter close command to probe
                PressKey('{VK_F2}')

                time.sleep(USER_INP + 3)

                quadfile = base_filename + "_pu.tif"
                PressKey(quadfile)
                PressKey('{VK_RETURN}')
                # Add shutter close command to pump

                et = time.time()

                if (et-st > re_align_time):
                    f = open("AcqStat.txt",'w')
                    f.write("2")
                    f.close()
                    prev_statLine = "2"
                else:
                    f = open("AcqStat.txt",'w')
                    f.write("1")
                    f.close()
                    prev_statLine = "1"
            else:
                if (timeout_cond == 0):
                    timeout_cond = 1
                    timeout_start = time.time()
                    print('Timer has begun on timeout.')

                if (time.time() - timeout_start > timeout):
                    print('Failed to find microscope window.')
                    f = open("AcqStat.txt",'w')
                    f.write("-1")
                    f.close()
                    statLine = "-1"

        time.sleep(0.5)

if __name__ == '__main__':
    main(sys.argv)