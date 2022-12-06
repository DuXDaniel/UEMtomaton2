import sys
import pywinauto
import time
        
def PressKey(keypress):
    ###### Press on keyboard the passed request
    pywinauto.keyboard.send_keys(keypress)
    time.sleep(0.1)

def FocusTheDesiredWnd():
    searchApp = pywinauto.application.Application()
    try:
        searchApp.connect(title_re=r'.*DigitalMicrograph.*')
        
        restoreApp = searchApp.top_window()
        restoreApp.minimize()
        restoreApp.restore()
        restoreApp.set_focus()
        return restoreApp
    except:
        return 0

def main(argv):
    hFoundWnd = FocusTheDesiredWnd()
    if(hFoundWnd != 0):

        PressKey('{VK_F10}') # alt key to enter alt menu on DM
        for i in range(6): # 6 keypresses to the right
            PressKey('{VK_RIGHT}')
        for  i in range(4): # 2 keypresses down
            PressKey('{VK_DOWN}')
        PressKey('{VK_RETURN}') # enter key to start DM script

if __name__ == '__main__':
    main(sys.argv)