from tkinter import *
from sys import platform

class OpenBOMToolTip(object):

    def __init__(self, widget, text):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.text = text
        self.widget.bind("<Enter>", self.onEnter)
        self.widget.bind("<Leave>", self.onLeave)

    """Should show tooltip
    Args:
      param (string): tooltip text
    Returns:
      none
    """
    def showtip(self):

        # check if tooltip window exists and text is not empty
        if self.tipwindow or not self.text:
            return

        # calculate coordinates of input and shift tooltip for 27px left and for 10px from top of input
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 10
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_geometry("+%d+%d" % (x, y))

        #try to render tooltip
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass

        fontsize = 12
        if platform == "win32":
            fontsize = 10
            tw.wm_overrideredirect(1)
            tw.attributes("-topmost", True)

        #add text to tooltip
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#fff", relief=SOLID, borderwidth=1,
                      font=("tahoma", fontsize, "normal"))
        label.pack(ipadx=1)
        tw.lift()

    """Should hide tooltip
    Args:
      none
    Returns:
      none
    """
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    def onEnter(self, event=None):
        self.showtip()

    def onLeave(self, event=None):
        self.hidetip()
