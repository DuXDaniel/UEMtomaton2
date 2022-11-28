import sys
import time
import threading
from pythonnet import load
load("netfx")
import clr
clr.AddReference(r'C:\Windows\Microsoft.NET\assembly\GAC_64\Newport.XPS.CommandInterface\v4.0_2.2.1.0__9a267756cf640dcf\Newport.XPS.CommandInterface.dll')
# The CLR module provide functions for interacting with the underlying
# .NET runtime
# Add reference to assembly and import names from namespace
# clr.AddReferenceToFile("") 
from CommandInterfaceXPS import *

# Create XPS interface with myXPS = XPS()

class XPSObj(object):
    checkLoop = 0

    def XPS_Open (self, address, port):
        # Create XPS interface
        self.myXPS = XPS()
        print(self.myXPS)
        # Open a socket
        timeout = 1000
        result = self.myXPS.OpenInstrument(address, port, timeout)
        if result == 0:
            print("Open ", address, ":", port, " => Successful")
            f = open('/connectStatFile.txt', 'w')
            f.write('1')
            f.close()
        else:
            print("Open ", address, ":", port, " => failure ", result)

    def XPS_Close(self,myXPS):
        self.myXPS.CloseInstrument()
        f = open('connectStatFile.txt', 'w')
        f.write('0')
        f.close()

    def processMovementFile(self):
        f = open('movementCommFile.txt','r')
        posMov = float(f.readline())
        compStat = int(f.readline())
        f.close()

        return posMov, compStat

    def indicateCompletedMovement(self):
        f = open('movementCommFile.txt','w')
        f.write(str(posMov) + "\n")
        f.write('1')
        f.close()

    def checkDisconnectOrder(self):
        f = open('connectStatFile.txt','r')
        checker = int(f.readline())
        f.close()
        return checker

    def signalPosition(self): # async
        while(self.myXPS.IsDeviceConnected() and self.checkLoop != 2):
            f = open('positionFile.txt','w')
            posRef = [0.]
            res, pos = self.myXPS.GroupPositionCurrentGet('Group1',posRef,1)
            f.write(str(pos[0]))
            f.close()
            time.sleep(1) # pause every 100 ms, don't need the crazy granularity

    def orderLoop(self): #async
        while(self.myXPS.IsDeviceConnected() and self.checkLoop != 2):
            posMov, compStat = self.processMovementFile()
            if (compStat == 0):
                self.myXPS.GroupMoveAbsolute('Group1',posMov,1)
                res, stat = self.myXPS.GroupStatusGet('Group1')
                while (stat != 12): # status of 12 indicates waiting after completed movement
                    res, stat = self.myXPS.GroupStatusGet('Group1')
                    time.sleep(2)
                self.indicateCompletedMovement()
            time.sleep(1) # pause every 100 ms, don't need the crazy granularity

    def initOrderLoop(self):
        self._orderLoop_thread = threading.Thread(target=self.orderLoop, args=())
        self._orderLoop_thread.daemon = True
        self._orderLoop_thread.start()

    def initSignalPos(self):
        self._signalPosition_thread = threading.Thread(target=self.signalPosition, args=())
        self._signalPosition_thread.daemon = True
        self._signalPosition_thread.start()

def main(argv):
    controlXPS = XPSObj()
    controlXPS.XPS_Open("192.168.254.254", 5001)
    controlXPS.initOrderLoop()
    controlXPS.initSignalPos()

    # loop that holds the process and prevents it from autocompleting
    while (checkLoop != 2):
        checkLoop = controlXPS.checkDisconnectOrder()
        controlXPS.checkLoop = checkLoop
        if (checkLoop == 2):
            controlXPS.checkLoop = 2
            time.sleep(3)
            controlXPS.XPS_Close()
        time.sleep(1)

if __name__ == '__main__':
    main(sys.argv)