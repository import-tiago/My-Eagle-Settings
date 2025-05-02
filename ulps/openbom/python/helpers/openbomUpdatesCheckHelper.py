import os
import re
import sys
import threading
import requests
from distutils.version import LooseVersion

import Util
from helpers import openbomLogger
from helpers.openbomDialogProgressBar import OpenBOMDialogProgressBar

logger = openbomLogger.getLogger('OpenBOMUpdatesCheckHelper')
from services.openbomService import OpenBOMAPI
from helpers.openbomDialogHelper import OpenBOMDialogHelper
import openbomConfig

# Should download and install update in new thread
class InstallerDownloadThread( threading.Thread ):
    max, val = None, None

    """Initialize class
    Args:
      param (string): plugin url
    Returns:
      none
    """
    def __init__(self, pluginUrl):
        logger.debug('InstallerDownloadThread: init. pluginUrl: %s', pluginUrl)
        super(InstallerDownloadThread, self).__init__( )
        self.val = 0
        self.pluginUrl = pluginUrl

    """Should process plugin (download it from api and run installer)
    Returns:
      none
    """
    def run(self):
        logger.debug('InstallerDownloadThread: run.')
        #default installer name installer.msi/pkg
        fileName = "installer.msi"
        installerPath = os.path.join(Util.rootDir, fileName)
        isWindows = True
        if 'darwin' == sys.platform:
            logger.debug('InstallerDownloadThread: run. Is Mac platform')
            isWindows = False
            fileName = "installer.pkg"
            installerPath = os.path.join(Util.rootDir, fileName)
            if os.path.exists(installerPath):
                os.remove(installerPath)
        
        logger.debug('InstallerDownloadThread: run. installerPath: %s', installerPath)
        logger.debug('InstallerDownloadThread: run. pluginUrl: %s', self.pluginUrl)
        with open(installerPath, "wb") as f:
            response = requests.get(self.pluginUrl, stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    self.val = done
        self.val = 100

        #run installer
        if isWindows:
            logger.debug('InstallerDownloadThread: run. start windows installer')
            os.startfile(installerPath)
        elif sys.platform == 'darwin':
            logger.debug('InstallerDownloadThread: run. start mac installer')
            os.chmod(installerPath, 777)
            os.popen('open ' + installerPath)

        OpenBOMDialogHelper.showWarningDialog("[OpenBOM] Installation: ", "Please close 'Eagle' to continue installation.")

class OpenBOMUpdatesCheckHelper():
    """Should initialize class
   Returns:
     none
   """
    def __init__(self):
        super().__init__()
        logger.debug('OpenBOMUpdatesCheckHelper: init.')

    """Should check for available updates
    Args:
      param (string): scriptsPath (Documents/Eagle/scripts/..)
   Returns:
     return (bool) True/False
   """
    @classmethod
    def checkUpdates(self, scriptsPath):
        logger.debug('OpenBOMUpdatesCheckHelper: checkUpdates. scriptsPath %s', scriptsPath)
        self.scriptPath = os.path.join(scriptsPath, "OpenBOM.scr")
        self.updateScriptPath = os.path.join(scriptsPath, "OpenBOMUpdate.scr")

        try:
            metadata = OpenBOMAPI.getLastAddinMetadata()
            if LooseVersion(openbomConfig.version) < LooseVersion(metadata.version):
                logger.debug('OpenBOMUpdatesCheckHelper: checkUpdates. Update is available')
                self.pluginUrl = metadata.downloadLink
                return True
            else:
                return False
        except Exception as ex:
            logger.error('OpenBOMUpdatesCheckHelper: checkUpdates. Exception: %s', ex)
            return False

    """Should trigger updates install
   Returns:
     None
   """
    @classmethod
    def installUpdates(self):
        logger.debug('OpenBOMUpdatesCheckHelper: installUpdates.')
        try:
            downloadThread = InstallerDownloadThread(self.pluginUrl)
            OpenBOMDialogProgressBar("OpenBOM Update", downloadThread)
        except Exception as ex:
            logger.error('OpenBOMUpdatesCheckHelper: installUpdates. Exception: %s', ex)

    """Should add 'update button' to eagle menu
   Returns:
     None
   """
    @classmethod
    def addUpdateMenu(self):
        logger.debug('OpenBOMUpdatesCheckHelper: showUpdateButton. scriptsPath %s', self.scriptPath)
        if not self.scriptPath:
            return

        try:
            newContent = ""
            with open(self.scriptPath, 'r') as f:
                content = f.read()
                newContent = re.sub("(#)('|[bin/icons/update.png]')", r'\2', content, flags=re.M)
                newContent = re.sub("(RUN openbom checkUpdates;)", r'#\1', newContent, flags=re.M)
                f.close()

            with open(self.updateScriptPath, 'w+') as f:
                f.write(newContent)
                f.close()
        except Exception as ex:
            logger.error('OpenBOMUpdatesCheckHelper: showUpdateButton. Exception %s', ex)

    """Should remove 'update button' to eagle menu
    Returns:
    None
    """
    @classmethod
    def removeUpdateMenu(self):
        try:
            os.remove(self.updateScriptPath)
        except Exception as ex:
            logger.error('OpenBOMUpdatesCheckHelper: removeUpdateMenu. Exception %s', ex)
