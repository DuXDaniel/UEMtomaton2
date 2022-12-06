import tkinter as tk
from tkinter import simpledialog

ROOT = tk.Tk()

ROOT.withdraw()
# the input dialog
USER_INP = float(simpledialog.askstring(title="Acquisition Time", prompt="Acquisition time:"))