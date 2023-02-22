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
    searchApp = pywinauto.application.Application()
    searchApp.connect(title_re=r'.*Snipping.*', found_index = 0)
    
    restoreApp = searchApp.top_window()
    restoreApp.minimize()
    restoreApp.restore()
    restoreApp.set_focus()
    return restoreApp

if __name__ == '__main__':
    main(sys.argv)