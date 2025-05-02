import webbrowser
import Util
import openbomConfig
from helpers import openbomLogger
logger = openbomLogger.getLogger('LocateHelper')
from models.BoMType import BoMType
from services.openbomService import OpenBOMAPI

class OpenBOMLocateHelper():

    """Should store credentials for retrieving correct url to BOM/Catalog
    Args:
      param (object): auth object
    Returns:
      none
    """
    @classmethod
    def authorize(cls, data):
        logger.debug("OpenBOMExtractor: %s", data)
        if data.access_token:
            cls.access_token = data.access_token
            cls.refresh_token = data.refresh_token

    """Should retrieve of BOM/Catalog by id
    Args:
      param (string): object type (BOM/Catalog)
      param (string): BOM/Catalog id
    Returns:
      (int) status code. 1 - failed, 0 - success
    """
    @classmethod
    def locateInOpenBOM(cls, type, bomSourceId):
        #int OpenBOM API
        api = OpenBOMAPI(cls.access_token, cls.refresh_token)

        try:
            logger.debug('bomSourceId:"%s"', bomSourceId)
            urls = []
            # search for BOM
            if (type == BoMType.SingleLevelBOM):
                docs = api.getBOMDocuments(openbomConfig.sourceProduct, bomSourceId)
                for bom in docs:
                    bomId = bom.id
                    urls.append(Util.getBoMUrl(bomId, bom.generationParams.bomType))
            elif (type == BoMType.Catalog):
                catalogs = api.getBOMCatalogs(openbomConfig.sourceProduct, bomSourceId)
                for cat in catalogs:
                    bomId = cat.id
                    urls.append(Util.getBoMUrl(bomId, cat.generationParams.bomType))

            # if url exists will open it default browser
            if len(urls) > 0:
                webbrowser.open(urls[0], new=2)
                return 0
        except:
            raise Exception("Application exception")
        
        raise Exception(bomSourceId + " isn't exist on OpenBOM")

    """Should open link by object sourceId
    Args:
      param (string): sourceId
      param (string): object type (BOM/Catalog)
    Returns:
      none
    """
    @classmethod
    def generateItemLink(cls, sourceId, bomType):
        if (sourceId != None):
            webbrowser.open(Util.getBoMUrl(sourceId, bomType), new=2)