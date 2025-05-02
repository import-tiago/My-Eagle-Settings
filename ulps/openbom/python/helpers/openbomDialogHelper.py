import tkinter, tkinter.messagebox
from views.openbomLicenseRequiredWarningView import OpenBOMLicenseRequiredWarningView

class OpenBOMDialogHelper():

    def InitTk(): 
        root = tkinter.Tk()
        # Gets the requested values of the height and width.
        mouse_x = root.winfo_pointerx()
        mouse_y = root.winfo_pointery()

        root.geometry("+{}+{}".format(int(mouse_x), int(mouse_y)))
        root.withdraw()
        return root

    '''Should show error dialog
    Args:
      param (string): message
    Returns:
      none
    '''
    def showErrorDialog(title, message):
        root = OpenBOMDialogHelper.InitTk()
        tkinter.messagebox.showerror(title, message)
        root.destroy()

    '''Should show info dialog
    Args:
      param (string): message
    Returns:
      none
    '''
    def showInfoDialog(title, message):
        root = OpenBOMDialogHelper.InitTk()
        tkinter.messagebox.showinfo(title, message)
        root.destroy()

    '''Should show waring dialog
    Args:
      param (string): message
    Returns:
      none
    '''
    def showWarningDialog(title, message):
        root = OpenBOMDialogHelper.InitTk()
        tkinter.messagebox.showwarning(title, message)
        root.destroy()

    '''Should display Subscription-require form with link onto OpenBOM Subscription page
    Args:
        title (string): dialog title
        message (string): dialog text
        links (string): links
    Returns:
      none
    '''
    def showLicenseRequiredDialog():
        root = OpenBOMDialogHelper.InitTk()
        dialog = OpenBOMLicenseRequiredWarningView(root)
        dialog.show()

        root.deiconify()
        root.mainloop()
