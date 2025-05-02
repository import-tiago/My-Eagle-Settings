import os
import Util
from services.openbomService import OpenBOMAPI

class OpenBOMRespHelper():
    RESP_PATH = os.path.join(Util.rootDir, "resp.tmp")

    @classmethod
    def printRespError(cls, resp):
        f = open(cls.RESP_PATH, "w+")
        f.write(OpenBOMAPI.toJson(resp))
        f.close()

    @classmethod
    def printResp(cls, resp):
        f = open(cls.RESP_PATH, "w+")
        f.write(Util.toHex(OpenBOMAPI.toJson(resp)))
        f.close()

    @classmethod
    def readResp(cls):
        f = open(cls.RESP_PATH, "r")
        data = f.read()
        f.close()
        try:
            str = bytes.fromhex(data).decode('utf-8')
            return OpenBOMAPI.fromJson(str)
        except Exception as ex:
            raise Exception("Error: Incorrect access token")