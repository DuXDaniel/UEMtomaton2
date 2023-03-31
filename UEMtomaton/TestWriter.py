import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog
import time

mainWindow = tk.Tk()

#ROOT.withdraw()
# the input dialog
#USER_INP = float(simpledialog.askstring(title="Acquisition Time", prompt="Acquisition time:"))


stepHistoryTable = ttk.Treeview(
    mainWindow,
    columns=("Step","Timepoint","Filename","Status"),
    height=round(600),
    show="headings"
)
stepHistoryTable.heading("Step",text="Step")
stepHistoryTable.column("Step",minwidth=0,width=round(150))
stepHistoryTable.heading("Timepoint",text="Timepoint")
stepHistoryTable.column("Timepoint",minwidth=0,width=round(150))
stepHistoryTable.heading("Filename",text="Filename")
stepHistoryTable.column("Filename",minwidth=0,width=round(150))
stepHistoryTable.heading("Status",text="Status")
stepHistoryTable.column("Status",minwidth=0,width=round(150))

stepHistoryTable.grid(column=0, row=0, columnspan=1, padx=5, pady=5, sticky="e")

stepHistoryTable.insert("",'end',values=["blahblahblah","asdf","asdf","asdf"])
childVals = stepHistoryTable.get_children()[0]
childVals2 = stepHistoryTable.item(childVals)['values']
childVals2[3] = 'C:/asdf/asdf/asdf/asdf/t345/nergnowerihg/34t/gra/fbn/adfs'
childVals2[3] = childVals2[3].replace('/','\\')
print(childVals2)
childVals2[2] = 'asdfasdf'
#stepHistoryTable.delete(childVals)
#childVals[3] = "asdf"
#stepHistoryTable.insert("",'end',values=["blahblahblah","asdf2","asdf2","asdf2"])
stepHistoryTable.item(childVals, values=childVals2)

mainWindow.mainloop()