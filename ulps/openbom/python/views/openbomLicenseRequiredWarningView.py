try:
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.messagebox as tm
    from tkinter.font import Font
    from PIL import Image as PImage, ImageTk
    from os.path import (dirname, join)
    from sys import platform

    import Util
    import openbomConfig
    from views.openbomBaseView import OpenBOMBaseView
    from helpers import openbomLogger
    logger = openbomLogger.getLogger('WarningWithLinksView')
except ImportError as ex:
    from helpers import openbomLogger
    logger = openbomLogger.getLogger('WarningWithLinksView')
    logger.error('OpenBOMLicenseRequiredWarningView: import %s failed. ', ex.name)
    raise ImportError('OpenBOMLicenseRequiredWarningView: import ' + ex.name + ' failed.')


class OpenBOMLicenseRequiredWarningView(OpenBOMBaseView):
    def __init__(self, root):
        root = root
        super().__init__(root)
        self.root = root

    '''Should render warning window with list of links
    Args:
        title: dialog title
        message: dialog text
        urls: list of links
    Returns:
       none
    '''
    def show(self):
        title = "[OpenBOM]: License Required"
        self.root.title(title)
        self.root.configure(background="#ececec", padx=10, pady=15)

        load = PImage.open(join(Util.rootDir, "warning.jpg"))
        render = ImageTk.PhotoImage(load)

        self.icon = Label(self, image=render)
        self.icon.image = render
        self.icon.place(x=0, y=10)

        message = '''CAD Integrations require an OpenBOM Professional User Subscription (or above)
or an active Trial subscription.
                             
For more information and to purchase an OpenBOM subscription please visit'''

        self.label = Label(self, text=message)

        self.label.grid(row=0, column=0, sticky='we', columnspan=2, padx=(45, 25), pady=(10, 0))

        fontsize = 12
        if platform == "win32":
            fontsize = 10
        linkfont = Font(underline=1, size=fontsize)
        
        self.link = Label(self, text=openbomConfig.openBoMSubscriptionUrl, cursor="hand2", foreground="blue", font=linkfont)
        self.link.bind("<Button-1>", lambda e: self.callback(openbomConfig.openBoMSubscriptionUrl))
        self.link.grid(row=1, column=0, sticky='w', columnspan=2, padx=(45, 25), pady=(0, 0))

        message = "Please click the \"Get Trial\" button below to activate your free trial license."
        self.label = Label(self, text=message)

        self.label.grid(row=2, column=0, sticky='we', columnspan=2, padx=(45, 25), pady=(10, 0))
        
        self.gettrialbtn = Button(self, text="Get Trial", command=lambda: self.callback("{}/trial-sign-up".format(openbomConfig.openBoMUrl)))
        self.closebtn = Button(self, text="Close", command=self.root.destroy)
        self.gettrialbtn.grid(row=3, column=0, sticky="sw", pady=(30, 0))
        self.closebtn.grid(row=3, column=1, sticky="se", pady=(30, 0))

        self.fixIcon()
        self.pack()
