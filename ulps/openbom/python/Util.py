import os
import argparse
import openbomConfig
from models.BoMType import BoMType
from os.path import (dirname, abspath, join)

rootDir = join(dirname(dirname(abspath(__file__))), "resources")

class Callable:
    def __call__(self):
        pass

'''Should generate url to assembly/library by bomId and object type
Args:
    param (string): bomId
    param (string) object type
Returns:
    (string) OpenBOM url
'''
def getBoMUrl(bomId, bomType=BoMType.MultiLevelBOM):
    viewMode = 'multiple' if (bomType == BoMType.MultiLevelBOM) else 'single'
    bomType = 'inventory' if (bomType == BoMType.Catalog) else 'bom'
    bomUrl = '{}/spreadsheet/{}/{}?viewMode={}'.format(openbomConfig.openBoMUrl, bomType, bomId, viewMode)
    return bomUrl

'''Should convert string to hex
Args:
    param (string): input string
Returns:
    hex value
'''
def toHex(x):
    return "".join([hex(ord(c))[2:].zfill(2) for c in x])

'''Should clean response
Args:
    none
Returns:
    none
'''
def clearRespOutput():
    os.remove(join(rootDir, "resp.tmp"))

'''Should process arguments from handler call and return only required one

Args:
    param (dict): List of required params key/value where key is arg key and value is help description.

 Returns:
    Object: The return value. Example: Object(path='c:/somedir/dir')
'''
def getArgParams(argKeys):
    if not argKeys:
        return None

    # Construct the argument parser
    ap = argparse.ArgumentParser()
    for key in argKeys:
        ap.add_argument('-' + key, '--' + key, required=True, help=argKeys[key])
    params, tmp = ap.parse_known_args()
    return params
