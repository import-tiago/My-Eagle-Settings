try:
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.messagebox as tm
    from PIL import Image as PImage, ImageTk
    from os.path import (dirname, join)

    import Util
    import openbomConfig
    from views.openbomBaseView import OpenBOMBaseView
    from helpers import openbomLogger
    logger = openbomLogger.getLogger('LoginWarningView')
except ImportError as ex:
    logger.error('OpenBOMLoginWarningView: import %s failed. ', ex.name)
    raise ImportError('OpenBOMLoginWarningView: import ' + ex.name + ' failed.')


class OpenBOMLoginWarningView(OpenBOMBaseView):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.openSettings = False

    '''Should render login window
    Args:
      none
    Returns:
       none
    '''
    def show(self):
        self.root.title("Autodesk Eagle OpenBOM Extractor")
        self.root.configure(background="#ececec", padx=10, pady=15)
        # set OpenBOM logo
        load = PImage.open(join(Util.rootDir, "warning.jpg"))
        render = ImageTk.PhotoImage(load)

        self.icon = Label(self, image=render)
        self.icon.image = render
        self.icon.place(x=0, y=0)

        # create auth fields
        self.label = Label(self, text="You are not signed in. Please check credentials in Settings.")
        self.label.configure(background='#ececec')
        self.label.grid(row=0, column=0, sticky='we', columnspan=2, padx=(45, 25), pady=(10, 0))

        # add form buttons
        self.logbtn = Button(self, text="Go to Settings", command=self._login_btn_clicked)
        self.logbtn.grid(row=1, column=0, sticky="w", pady=(30, 0))

        self.closebtn = Button(self, text="Close", command=self.root.destroy)
        self.closebtn.grid(row=1, column=1, sticky="se", pady=(30, 0))

        self.setWindowSize(230, 250)

        self.fixIcon()
        self.pack()

    '''Should store login and password for authorization
    Args:
        none
    Returns:
       none
    '''
    def _login_btn_clicked(self):
        self.openSettings = True
        self.root.destroy()
