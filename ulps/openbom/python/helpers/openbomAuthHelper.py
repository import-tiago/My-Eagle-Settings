from helpers import openbomLogger
logger = openbomLogger.getLogger('AuthHelper')
import openbomConfig
from helpers.openbomDialogHelper import OpenBOMDialogHelper
from services.openbomRespService import OpenBOMRespService
from services.openbomService import OpenBOMAPI
from exceptions.OpenBOMAPIError import (OpenBOMAPIError, OpenBOMAPILicenseError)

class OpenBOMAuthHelper():

    '''Should retrieve acccess token from openbom api
   Args:
       param (string): username
       param (string): password
    Returns:
       (bool) true/false status of operation
   '''
    @classmethod
    def retrieveAccessToken(cls, login, password):
        if login and password:
            try:
                OpenBOMRespService.clearResp()

                try:
                    logger.debug('oAuthForm: try to login as non MFA:%s')
                    access_token = OpenBOMAPI.getAccessToken(login, password)
                    logger.debug('oAuthForm: authorized as non MFA:%s', access_token)
                    setattr(access_token, 'login', login)
                    setattr(access_token, 'psw', password)
                    OpenBOMRespService.printResp(access_token)
                    return True
                except OpenBOMAPILicenseError as ex:
                    logger.error('oAuthForm: catch license error. %s', ex)
                    OpenBOMDialogHelper.showLicenseRequiredDialog()
                    return False
                except Exception as ex:
                    logger.error('oAuthForm: non MFA authentication error. %s', ex)

                logger.debug('oAuthForm: try to login as MFA:%s')
                session_token = OpenBOMAPI.getSessionToken(login, password)
                access_token = OpenBOMAPI.MFAauthorize(session_token)
                logger.debug('oAuthForm: authorized as MFA:%s', access_token)
                setattr(access_token, 'refresh_token', "")
                setattr(access_token, 'scope', "profile openid email")
                setattr(access_token, 'login', login)
                setattr(access_token, 'psw', password)
                OpenBOMRespService.printResp(access_token)
                return True
            except OpenBOMAPILicenseError as ex:
                logger.error('oAuthForm: catch license error. %s', ex)
                OpenBOMDialogHelper.showLicenseRequiredDialog()
                return False
            except OpenBOMAPIError as ex:
                logger.error('oAuthForm: catch api error. %s', ex)
                OpenBOMDialogHelper.showErrorDialog("[OpenBOM] Authorization error", ex.getUserMessage())
                return False
            except Exception as ex:
                logger.error('oAuthForm: catch error. %s', ex)
                OpenBOMDialogHelper.showErrorDialog("[OpenBOM] Authorization common error", ex.getUserMessage())
                return False
        OpenBOMDialogHelper.showWarningDialog("Login error", "Login/Password was missed")
        return False
