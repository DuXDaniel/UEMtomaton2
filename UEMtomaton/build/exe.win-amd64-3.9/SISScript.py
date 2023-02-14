import sys
import pywinauto
import time
        
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
    hFoundWnd = FocusTheDesiredWnd()

    f = open("SISSettings.txt",'r')
    statLine = f.readLine()
    try:
        filepath = f.readline()
        filebase = f.readline()
        acqTime = f.readline()
        skipAmt = f.readline()
        f.close()
    except:
        f.close()

    count = 0
    while (statLine != "0"):
        hFoundWnd = FocusTheDesiredWnd()
        if(hFoundWnd != 0):
            filename = filepath + filebase + "_" + str(count) + ".tif"

            PressKey('{VK_F2}')

            time.sleep(acqTime)

            quadfile = filename
            PressKey(quadfile)
            PressKey('{VK_RETURN}')

            count = count + 1

            f = open("SISSettings.txt",'r')
            statLine = f.readLine()
            f.close()

            if (statLine != "0"):
                time.sleep(skipAmt)

if __name__ == '__main__':
    main(sys.argv)