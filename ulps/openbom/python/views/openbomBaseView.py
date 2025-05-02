import ctypes
import webbrowser
from tkinter import *
from sys import platform
from os.path import (dirname, join)
import Util


class OpenBOMBaseView(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root

        # fix bg color at MacOs
        self.canv = Canvas(self, background='#ececec')
        self.canv.place(x=-5, y=-5, width=600, height=600)

    '''Should fix windows size and place it near cursor
    Args:
       param (int): window height
       param (int): window width
    Returns:
       none
    '''
    def setWindowSize(self, height, width):
        mouse_x = self.root.winfo_pointerx()
        mouse_y = self.root.winfo_pointery()
        self.root.resizable(0, 0)

        #widthXheight+leftAlign+topAlign
        self.root.geometry("+{}+{}".format(int(mouse_x - (width/2)), int(mouse_y - (height/3))))
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

    '''Should fix icon in taskbar
    Returns:
       none
    '''
    def fixIcon(self):
        self.fixIconSt(self.root)

    '''Should fix icon in taskbar
    Returns:
       none
    '''

    def fixIconSt(self, root):
        imagesDir = join(dirname(Util.rootDir), "resources")
        myappIcon = 'openbom.eagle.extractor.icon'

        #in case of windows update icon to openBOM.ico
        if platform == "win32":
            root.iconbitmap(default = join(imagesDir, "openBoM.ico"))
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappIcon)


    '''Should open links in default browser
   Returns:
      none
   '''
    def callback(self, url):
        webbrowser.open_new(url)
