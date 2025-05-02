import os
import time

import Util
from services.openbomService import OpenBOMAPI


class OpenBOMRespService():
    RESP_PATH = os.path.join(Util.rootDir, "resp.tmp")

    '''Should check that accesstoken is not expired
        default expiration time is 24 hours
   Args:
       none
    Returns:
       none
   '''
    @classmethod
    def isRespExpired(cls):
        # receive time of creation accesstoken
        file_mod_time = os.stat(cls.RESP_PATH).st_mtime
        # time in hours since last modification of file
        last_time = (time.time() - file_mod_time) / 360

        if last_time > 24:
            return True
        else:
            return False

    '''Should return (save to file) error response
   Args:
       param (object): Error message
    Returns:
       none
   '''
    @classmethod
    def printRespError(cls, resp):
        f = open(cls.RESP_PATH, "w+")
        f.write(OpenBOMAPI.toJson(resp))
        f.close()

    '''Should return (save to file) auth response
   Args:
       param (object): auth object
    Returns:
       none
   '''
    @classmethod
    def printResp(cls, resp):
        f = open(cls.RESP_PATH, "w+")
        f.write(Util.toHex(OpenBOMAPI.toJson(resp)))
        f.close()

    '''Should retrieve auth object
   Args:
       none
    Returns:
       none
   '''
    @classmethod
    def readResp(cls):
        # check if access token is expired
        if cls.isRespExpired():
            raise Exception("Error: Access Token expired")

        # retrieve auth object
        f = open(cls.RESP_PATH, "r")
        data = f.read()
        f.close()
        try:
            str = bytes.fromhex(data).decode('utf-8')
            return OpenBOMAPI.fromJson(str)
        except Exception as ex:
            raise Exception("Error: Incorrect access token")

    '''Should remove old auth information
   Args:
       none
    Returns:
       none
   '''
    @classmethod
    def clearResp(cls):
        if os.path.isfile(cls.RESP_PATH):
            os.remove(cls.RESP_PATH)