import tkinter as tk
from tkinter import ttk

from views.openbomBaseView import OpenBOMBaseView


class OpenBOMDialogProgressBar():

    '''Should initialize OpenBOM progressbar
    Args:
      param (string): message
      param (object): thread class
    Returns:
      none
    '''
    def __init__(self, message, thread):
        super().__init__()
        self.root = tk.Tk()
        # Gets the requested values of the height and width.
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()

        self.root.geometry("+{}+{}".format(int(mouse_x), int(mouse_y)))
        # fix OpenBOM icon
        OpenBOMBaseView.fixIconSt(self, self.root)

        #start processing data in parallel thread
        self.thread = thread
        self.thread.start()

        #create progressbar
        self.pb = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.root.title(message)
        self.pb["maximum"] = 100
        self.pb["value"] = 0
        self.pb.grid(row=0, column=0)

        #check for progress update
        self.root.after(1, self.looker, self.thread)
        self.root.mainloop()

    '''Should update progress bar value 
    Args:
      param (object): thread class
    Returns:
      none
    '''
    def looker(self,  thread):
        if thread.val < 100:
            self.pb["value"] = thread.val
        else:
            self.root.destroy()
        self.root.after(1, self.looker, thread)