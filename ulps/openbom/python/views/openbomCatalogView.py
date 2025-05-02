try:
    import Util
    import webbrowser
    from tkinter import *
    from tkinter.ttk import *
    from tkinter.font import Font
    from PIL import Image as PImage, ImageTk
    from os.path import (dirname, join)

    from views.openbomBaseView import OpenBOMBaseView
    from helpers import openbomLogger
    logger = openbomLogger.getLogger('CatalogView')
except ImportError as ex:
    logger.error('OpenBOMCatalogView: import %s failed. ', ex.name)
    raise ImportError('OpenBOMCatalogView: import '+ ex.name +' failed.')


class OpenBOMCatalogView(OpenBOMBaseView):
    def __init__(self, root):
        super().__init__(root)
        self.root = root

    '''Should render catalog window
    Args:
       none
    Returns:
       none
    '''

    def show(self, listCatalog):
        self.root.title("[OpenBOM] Import")
        self.root.configure(background="#ececec", padx=15, pady=15)
        self.datalist = listCatalog

        load = PImage.open(join(Util.rootDir, "openbomLogo.jpg"))
        render = ImageTk.PhotoImage(load)
        self.icon = Label(self, image=render)
        self.icon.image = render
        self.icon.grid(columnspan=3, row=0, sticky=N, pady=(0, 10), padx=(0, 0), in_=self)

        f0 = Font(size=10)
        f1 = Font(underline=1, size=10)
        l = Label(self, text="The following Catalogs were created or updated", font=f0, width=15)
        l.grid(row=1, sticky=NSEW, pady=(0, 10), padx=(0, 0), in_=self)

        canvas = Canvas(self)
        canvas.configure(height=200)
        scroll_y = Scrollbar(self, orient="vertical", command=canvas.yview)
        frame = Frame(canvas)

        for i,catalog in enumerate(listCatalog):
            l = Label(frame, text=catalog["name"], foreground="blue", font=f1)
            l.bind("<Button-1>", lambda event, url=catalog["url"]: webbrowser.open(url, new=2))
            l.pack(anchor=W)

        # put the frame in the canvas
        canvas.create_window(0, 0, anchor='nw', window=frame)
        # make sure everything is displayed before configuring the scrollregion
        canvas.update_idletasks()

        canvas.configure(scrollregion=canvas.bbox('all'),
                         yscrollcommand=scroll_y.set)

        canvas.grid(row=2, sticky=NSEW)
        scroll_y.grid(column=2, row=2, sticky=NS)

        self.closeBtn = Button(self, text="Close", command=self.root.destroy)
        self.closeBtn.grid(columnspan=3, row=3, sticky=SE, pady=(30, 0), padx=0)

        self.setWindowSize(460, 400)
        #fix app icon
        self.fixIcon()
        self.pack()
