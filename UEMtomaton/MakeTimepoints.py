import math
import time
import sys
import json
import socket
import os.path as path
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import PhotoImage
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog

def main(argv):
    windowWidget = WidgetGallery()

class WidgetGallery():

    def __init__(self, parent=None):
        self.mainWindow = tk.Tk()
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

        curRow = 0

        f.write(str(self.includeLast.get()))

        for line in self.timeTree.get_children():
            f.write("\n")
            for value in self.timeTree.item(line)['values']:
                f.write(str(value) + " ")

            f.write(str(curRow))
            curRow = curRow + 1

        f.close()

    def loadTimepoints_Click(self):
        for item in self.timeTree.get_children():
            self.timeTree.delete(item)

        openTimeDialog = filedialog.askopenfilename()
        
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

        self.mainWindow.destroy()

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
