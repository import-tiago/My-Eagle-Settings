import os
import sys
import glob
import shutil

# add packages to the system path to be able to load requests module
__workingFolder__ = os.path.dirname(os.path.abspath(__file__))
__libsFolder__ = os.path.join(os.path.dirname(__workingFolder__), 'packages')
print(__libsFolder__)
if __libsFolder__ not in sys.path:
    sys.path.insert(0, __libsFolder__)

sys.path.insert(0, __workingFolder__)
__tkinterFolder__ = os.path.join(os.path.dirname(__libsFolder__), 'tk')
#if __tkinterFolder__ not in sys.path:
sys.path.insert(0, __tkinterFolder__)


import Util


import openbomConfig
from helpers import openbomLogger
logger = openbomLogger.getLogger('Hanlder')
from helpers.openbomDialogHelper import OpenBOMDialogHelper
from helpers.openbomUpdatesCheckHelper import OpenBOMUpdatesCheckHelper
from helpers.openbomAuthHelper import OpenBOMAuthHelper
from helpers.openbomExtractor import OpenBOMExtractor
from helpers.openbomLocateHelper import OpenBOMLocateHelper
from services.openbomRespService import OpenBOMRespService
from services.openbomSettingsService import OpenBOMSettingsService
from views.openbomLoginWarningView import OpenBOMLoginWarningView
from views.openbomSettingsView import OpenBOMSettingView
from views.openbomCatalogView import OpenBOMCatalogView
from services.openbomService import OpenBOMAPI

from tkinter import *
from helpers import *
from models.BoMType import BoMType
from exceptions import OpenBOMAPIError

class Actions():
    def __init__(self):
        logger.debug('Actions: __init__. ')

    '''Should authorize via access code if it's not expired otherwise call login form
    Args:
        param (string): Full path to new folder.
     Returns:
        int: 0 on successful authorization
    '''
    def authorize(self, action="login"):
        try:
            accessToken = OpenBOMRespService.readResp()
            OpenBOMExtractor.authorize(accessToken)
            OpenBOMLocateHelper.authorize(accessToken)
            return True
        except Exception:
            if action == "login":
                return self.showLoginWarningForm()
            else:
                return self.showSettingForm()

    '''Should display login form and receive auth token
    Args:
        none
     Returns:
        bool: True on successful login
    '''
    def showLoginWarningForm(self):
        try:
            root = Tk()
            loginForm = OpenBOMLoginWarningView(root)
            loginForm.show()
            root.mainloop()
            if loginForm.openSettings:
                return self.showSettingForm()
            else:
                return False
        except:
            return False

    '''Should display settings form
    Args:
        none
     Returns:
        bool: True on successful login
    '''
    def showSettingForm(self):
        try:
            root = Tk()
            settingForm = OpenBOMSettingView(root)
            settingForm.show()
            root.mainloop()
            if settingForm.username and settingForm.password:
                OpenBOMAuthHelper.retrieveAccessToken(settingForm.username, settingForm.password)
                return self.authorize("settings")
            return False
        except:
            return False

    '''Should create new folder on all OS
    Args:
        param (string): Full path to new folder.
     Returns:
        int: 0 on successful cache clear
    '''
    def makeDir(self):
        params = Util.getArgParams({'path': 'folder path'})
        logger.debug('Actions: mkdir. path %s', params.path)
        os.mkdir(params.path)

    ''' Check authorization '''
    def checkAuth(self):
        logger.debug('Actions: checkAuth.')
        if not self.authorize():
            logger.debug('Auth failed')
            # non zero result code will notify about failed authentication
            raise Exception("Auth failed")

    '''Should parse and send BOM to OpenBOM API
    Args:
        param (string): BOM Name
    Returns:
        string: OpenBOM BOM url
    '''
    def sendBOM(self):
        params = Util.getArgParams({'name': 'BOM name (file name of BOM xml)'})
        logger.debug('Actions: sendBOM. bomName %s', params.name)
        if not self.authorize():
            return -1

        try:
            OpenBOMExtractor.createBOM(BoMType.SingleLevelBOM, params.name)
            message = "BOM was imported to OpenBOM successfully. \nIt will be open in browser in few seconds."
            OpenBOMDialogHelper.showInfoDialog("[OpenBOM] Import BOM", message)
        except:
            message = "BOM import was failed. \nPlease contact support."
            OpenBOMDialogHelper.showWarningDialog("[OpenBOM] Locate: {}".format(params.name), message)

    '''Should parse and send Catalog to OpenBOM API
    Args:
        param (string): Catalog Name
    Returns:
        string: OpenBOM Catalog url
    '''
    def sendCatalog(self):
        params = Util.getArgParams({'name': 'Catalog name (file name of Catalog xml)'})
        logger.debug('Actions: sendCatalog. bomName %s', params.name)
        if not self.authorize():
            return -1

        try:
            OpenBOMExtractor.createBOM(BoMType.Catalog, params.name)
            message = "Catalog was imported to OpenBOM successfully. \nIt will be open in browser in few seconds."
            OpenBOMDialogHelper.showInfoDialog("[OpenBOM] Import Catalog", message)
        except:
            message = "Catalog import was failed. \nPlease contact support."
            OpenBOMDialogHelper.showWarningDialog("[OpenBOM] Import Catalog: {}".format(params.name), message)

    '''Should receive link for BOM from OpenBOM by BOM name
    Args:
        param (string): BOM Name
    Returns:
        string: OpenBOM BOM url
    '''
    def locateBOM(self):
        params = Util.getArgParams({'name': 'BOM name (file name of BOM xml)'})
        logger.debug('Actions: locateBOM. bomName %s', params.name)
        if not self.authorize():
            return -1

        try:
            return OpenBOMLocateHelper.locateInOpenBOM(BoMType.SingleLevelBOM, params.name)
        except:
            message = "'{}' Bill of Materials not found in OpenBOM. \nPlease create a BOM.".format(params.name)
            OpenBOMDialogHelper.showWarningDialog("[OpenBOM] Locate: {}".format(params.name), message)

    '''Should receive link for Catalog from OpenBOM by BOM name
    Args:
        param (string): Catalog Name
    Returns:
        string: OpenBOM Catalog url
    '''
    def locateCatalog(self):
        params = Util.getArgParams({'name': 'Catalog name (file name of BOM xml)'})
        logger.debug('Actions: locateCatalog. catalogName %s', params.name)
        if not self.authorize():
            return -1

        try:
            return OpenBOMLocateHelper.locateInOpenBOM(BoMType.Catalog, params.name)
        except:
            message = "'{}' Catalog not found in OpenBOM. \nPlease create a Catalog.".format(params.name)
            OpenBOMDialogHelper.showWarningDialog("[OpenBOM] Locate: {}".format(params.name), message)

    def sendMultiCatalog(self):
        params = Util.getArgParams({'name': 'BOM name (file name of BOM xml)'})
        logger.debug('Actions: listCatalog. bomName %s', params.name)
        if not self.authorize():
            return -1

        try:
            results = OpenBOMExtractor.createBOM(BoMType.Catalog, params.name)

            if results:
                root = Tk()
                catalogForm = OpenBOMCatalogView(root)
                catalogForm.show(results)
                root.mainloop()
        except:
            message = "Catalog import was failed. \nPlease contact support."
            OpenBOMDialogHelper.showWarningDialog("[OpenBOM] Import Catalog: {}".format(params.name), message)

    '''Should check for updates and add update button to eagle menu if update exists
    Args:
        param (string): scriptsPath
    Returns:
        none
    '''
    def checkUpdates(self):
        params = Util.getArgParams({'scriptsPath': 'Path to script files'})
        logger.debug('Actions: checkUpdates. scriptsPath %s', params.scriptsPath)
        updatesChecker = OpenBOMUpdatesCheckHelper()

        if updatesChecker.checkUpdates(params.scriptsPath):
            updatesChecker.addUpdateMenu()
        else:
            updatesChecker.removeUpdateMenu()

    '''Should download update and run it
    Returns:
        none
    '''
    def updateAddin(self):
        logger.debug('Actions: updateAddin.')
        updatesChecker = OpenBOMUpdatesCheckHelper()

        if updatesChecker.checkUpdates(""):
            updatesChecker.installUpdates()

    '''Should clear cache for OpenBOM Extension
    Returns:
        int: 0 on successful cache clear
    '''
    def clearCache(self):
        logger.debug('Actions: clearCache.')
        Util.clearRespOutput()

    '''Should fix missed menu icons via copy them to correct Eagle folder
    Args:
        param (string): OpenBOM Add-in resources path
        param (string): Eagle resources path
    Returns:
        int: 0 on successful resources sync
    '''
    def fixResources(self):
        try:
            params = Util.getArgParams({'openbomResources': 'OpenBOM resources folder', 'eagleResources': 'Eagle resources folder'})
            logger.debug('Actions: locateCatalog. openbomResources: %s , eagleResources: %s', params.openbomResources, params.eagleResources)
            for file in glob.glob(params.openbomResources):
                shutil.copy(file, params.eagleResources)
            return 0
        except:
            return 1

'''Should handle action requests and process it
Args:
    param (string): OpenBOM handler action name
    param (*): Other skipped params
Returns:
    int: 0 on successful processing
'''
try:
    settings = OpenBOMSettingsService.readSettings()
    try :
        openbomConfig.openBoMUrl = settings.openBoMUrl
    except Exception:
        print("Use default api url")

    try :
        if (settings.loggingEnabled == 1):
            print('Logging enabled')
            openbomLogger.setLogLevel(openbomLogger.DEBUG)
    except Exception:
        print("Logging disabled")

    parameters = Util.getArgParams({'action': 'action'})
    # Call action by its name
    actions = Actions()
    response = getattr(actions, parameters.action)()
except OpenBOMAPIError as ex:
    logger.error('oAuthForm: catch api error. %s', ex)
    OpenBOMDialogHelper.showErrorDialog("[OpenBOM] Error", "Error: " + ex.getUserMessage())
    sys.exit(1)
except Exception as ex:
    logger.error('oAuthForm: catch error. %s', ex)
    OpenBOMDialogHelper.showErrorDialog("[OpenBOM] Error", "Error: " + ex.getUserMessage())
    sys.exit(1)

if response == 1 or response == -1:
    sys.exit(response)
sys.exit(0)
