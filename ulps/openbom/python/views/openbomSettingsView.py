try:
    import Util
    from PIL import Image as PImage, ImageTk
    from tkinter import *
    from tkinter.ttk import *
    import tkinter.messagebox as tm
    from os.path import (dirname, join)

    import openbomConfig
    from helpers.openbomToolTipHelper import OpenBOMToolTip
    from services.openbomRespService import OpenBOMRespService
    from services.openbomSettingsService import OpenBOMSettingsService
    from views.openbomBaseView import OpenBOMBaseView
    from helpers import openbomLogger
    logger = openbomLogger.getLogger('SettingsView')
except ImportError as ex:
    logger.error('OpenBOMSettingView: import %s failed. ', ex.name)
    raise ImportError('OpenBOMSettingView: import '+ ex.name +' failed.')


class OpenBOMSettingView(OpenBOMBaseView):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.username = None
        self.password = None

    '''Should render settings window
    Args:
       none
    Returns:
       none
    '''
    def show(self):
        self.root.title("[OpenBOM] Settings")
        self.root.configure(background="#ececec", padx=20, pady=15)

        # retrieve login/password from settings
        username = ""
        password = ""
        try:
            userSettings = OpenBOMRespService.readResp()
            username = userSettings.login
            password = userSettings.psw
        except Exception:
            print("Missed auth data")
            logger.error('OpenBOMSettingView: show(). Missed auth data. ')

        # retrieve group criteria
        self.groupByEnabled = IntVar()
        self.loggingEnabled = IntVar()
        groupByCriteria = ""
        try:
            settings = OpenBOMSettingsService.readSettings()
            self.groupByEnabled.set(settings.groupByEnabled)
            self.loggingEnabled.set(settings.loggingEnabled)
            groupByCriteria = settings.groupByCriteria 
        except Exception as e:
            print("Missed settings data: " + str(e))
            logger.error('OpenBOMSettingView: show(). Missed settings data. ')

        # render inputs
        self.label_apiUrl = Label(self, text="OpenBOM URL")
        self.label_apiUrl.grid(row=0, column=0, columnspan=2, sticky=W, pady=(5, 0), padx=0)

        self.version = Label(self, text='v ' + openbomConfig.version)
        self.version.grid(row=0, column=2, columnspan=2, sticky=E, pady=(5, 0), padx=0)

        self.entry_apiUrl = Entry(self)
        self.entry_apiUrl.insert(0, openbomConfig.openBoMUrl)
        self.entry_apiUrl.configure(state='readonly')
        self.entry_apiUrl.grid(row=1, column=0, columnspan=4, sticky=W+E, pady=0, padx=0)

        self.label_username = Label(self, text="User name")
        self.label_username.grid(row=2, column=0, columnspan=2, sticky=W, pady=(5, 0), padx=0)
        self.entry_username = Entry(self)
        self.entry_username.insert(0, username)
        self.entry_username.grid(row=3, column=0, columnspan=4, sticky=W+E, pady=0, padx=0)

        self.label_password = Label(self, text="Password")
        self.label_password.grid(row=4, column=0, columnspan=2, sticky=W, pady=(5, 0), padx=0)
        self.entry_password = Entry(self, show="*")
        self.entry_password.insert(0, password)
        self.entry_password.grid(row=5, column=0, columnspan=4, sticky=W+E, pady=(0, 5), padx=0)

        # render recovery links
        self.link1 = Label(self, text="Create account", cursor="hand2", foreground="blue", underline=0)
        self.link1.bind("<Button-1>", lambda e: self.callback(openbomConfig.openBoMRegistrationUrl))
        self.link1.grid(row=6, column=0, columnspan=2, sticky="w")

        self.link2 = Label(self, text="Forgot password?",  cursor="hand2", foreground="blue", underline=0)
        self.link2.bind("<Button-1>", lambda e: self.callback(openbomConfig.openBoMRecoveryUrl))
        self.link2.grid(row=6, column=2, columnspan=2, sticky="e")

        self.renderGroupItemsPanel(self.groupByEnabled, groupByCriteria)

        self.labelLogging = Label(self, text="Enable logging:")
        self.labelLogging.grid(row=8, column=0, columnspan=1, sticky=W, pady=(10, 0), padx=(25, 0))
        self.logging_checkBox = Checkbutton(self, text="", variable=self.loggingEnabled)
        self.logging_checkBox.grid(row=8, column=0, columnspan=1, sticky=W, pady=(10, 0), padx=(0, 0))

        OpenBOMToolTip(self.labelLogging, '''Enable logging will cause additinal information to be written to files 
which OpenBOM Support team can use to help resolve issues.''')

        self.okBtn = Button(self, text="OK", command=self.OkClicked)
        self.okBtn.grid(row=9, column=0, columnspan=2, sticky=W, pady=(10, 0), padx=0)

        self.closeBtn = Button(self, text="Close", command=self.root.destroy)
        self.closeBtn.grid(row=9, column=2, columnspan=2, sticky=E, pady=(10, 0), padx=0)

        #fix windows position
        self.setWindowSize(265, 460)
        #fix app icon
        self.fixIcon()
        self.pack()

    '''Should render group items panel (input with clear button and tooltip)
    Args:
       none
    Returns:
       none
    '''
    def renderGroupItemsPanel(self, groupByEnabled, groupByCriteria):
        self.groupByEnabled = groupByEnabled
        self.label_groupBy = Label(self, text="Group BOM Items by:")
        self.label_groupBy.grid(row=7, column=0, columnspan=1, sticky=W, pady=(10, 0), padx=(25, 0))
        self.groupByCheckBox = Checkbutton(self, text="", variable=self.groupByEnabled)
        self.groupByCheckBox.grid(row=7, column=0, columnspan=1, sticky=W, pady=(10, 0), padx=(0, 0))

        self.entry_groupBy = Entry(self)
        self.entry_groupBy.insert(0, groupByCriteria)
        self.entry_groupBy.grid(row=7, column=1, columnspan=2, sticky=W+E, pady=(10, 0), padx=(5, 0))

        # add tooltip for group parts input
        OpenBOMToolTip(self.label_groupBy, "Specify columns to group parts. Use ';' character as delimiter")
        OpenBOMToolTip(self.entry_groupBy, "Voltage;Capacity;Manufacture")

        try:
            self.button_groupByClear = Button(self, text="X", command=self.groupByClearClicked, width=2)
            self.button_groupByClear.grid(row=7, column=3, columnspan=1, sticky=W+E, pady=(10, 0), padx=(3, 3))

        except Exception as e:
            print(e)

    '''Should save settings and verify that login/password is not empty
    Args:
       none
    Returns:
       none
    '''
    def OkClicked(self):
        self.saveSettings()

        self.username = self.entry_username.get()
        self.password = self.entry_password.get()

        if len(self.username) > 0 and len(self.password) > 0:
            self.root.destroy()
        else:
            tm.showerror("Login error", "Login/Password was missed")

    '''Should clear groupBy input
    Args:
       none
    Returns:
       none
    '''
    def groupByClearClicked(self):
        self.entry_groupBy.delete(0, 'end')

    '''Should save groupBy settings
    Args:
       none
    Returns:
       none
    '''
    def saveSettings(self):
        groupByEnabled = 1
        if not self.groupByEnabled.get():
            groupByEnabled = 0

        loggingEnabled = 1
        if not self.loggingEnabled.get():
            openbomLogger.setLogLevel(openbomLogger.DEFAULT)
            loggingEnabled = 0
        else:
            openbomLogger.setLogLevel(openbomLogger.DEBUG)

        OpenBOMSettingsService.updateSettingValue("groupByEnabled", groupByEnabled)
        OpenBOMSettingsService.updateSettingValue("loggingEnabled", loggingEnabled)
        OpenBOMSettingsService.updateSettingValue("groupByCriteria", self.entry_groupBy.get())
