import os
import Util
from helpers import openbomLogger
logger = openbomLogger.getLogger('SettingsService')
from services.openbomService import OpenBOMAPI


class OpenBOMSettingsService():
    SETTINGS_PATH = os.path.join(Util.rootDir, "settings.ini")

    '''Should store setting to SETTINGS_PATH file in json
   Args:
       param (object): Settings object
    Returns:
       none
   '''
    def saveSettings(resp):
        logger.debug('OpenBOMSettingsService: saveSettings')
        f = open(OpenBOMSettingsService.SETTINGS_PATH, "w+")
        f.write(OpenBOMAPI.toJson(resp))
        f.close()

    '''Should retrieve setting to settings file and convert it to object
    Args:
       none
    Returns:
       int: settings object
    '''
    def readSettings():
        data = ''
        try:
            logger.debug('OpenBOMSettingsService: readSettings')
            f = open(OpenBOMSettingsService.SETTINGS_PATH, "r")
            data = f.read()
            f.close()
        except Exception as ex:
            logger.error("Error: Incorrect settings file")

        if len(data) == 0:
            data =  '{"settings": "settings"}'
        return OpenBOMAPI.fromJson(data)

    '''Should update key/value in settings
    Args:
        param (string): Settings property key
        param (string): Settings property value
    Returns:
       none
    '''
    def updateSettingValue(key, value):
        logger.debug('OpenBOMSettingsService: updateSettingValue key:"%s". value:"%s"', key, value)
        settings = OpenBOMSettingsService.readSettings()
        setattr(settings, key, value)
        OpenBOMSettingsService.saveSettings(settings);
