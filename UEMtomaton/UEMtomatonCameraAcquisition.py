import sys
import pywinauto
import time
import tkinter as tk
from tkinter import simpledialog
        
def PressKey(keypress):
    ###### Press on keyboard the passed request
    pywinauto.keyboard.send_keys(keypress,pause=0.05)
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
    ROOT = tk.Tk()

    ROOT.withdraw()
    # the input dialog
    USER_INP = float(simpledialog.askstring(title="Acquisition Time", prompt="Acquisition time:"))

    hFoundWnd = FocusTheDesiredWnd()

    f = open("AcqStat.txt",'r')
    statLine = f.readLine()
    f.close()
    while (statLine != "-1"):
        f = open("AcqStat.txt",'r')
        statLine = f.readLine()
        f.close()
        
        if (statLine == "0"):
            hFoundWnd = FocusTheDesiredWnd()
            if(hFoundWnd != 0):
                f = open("AcquisitionSettings.txt",'r')
                filepath = f.readline()
                filebase = f.readline()
                curScanStep = f.readline()
                curDelay = f.readline()
                curScan = f.readline()
                curPos = f.readline()
                f.close()

                filename = filepath + filebase + "_" + curScan + "_" + curScanStep + "_" + curDelay + ".tif"

                PressKey('{VK_F2}')

                time.sleep(USER_INP + 5)

                quadfile = filename
                PressKey(quadfile)
                PressKey('{VK_RETURN}')

                f = open("AcqStat.txt",'w')
                f.write("1")
                f.close()
            else:
                f = open("AcqStat.txt",'w')
                f.write("-1")
                f.close()
                statLine = "-1"

        time.sleep(0.5)

if __name__ == '__main__':
    main(sys.argv)