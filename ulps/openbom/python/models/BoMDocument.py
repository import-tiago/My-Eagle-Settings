import openbomConfig
from helpers import openbomLogger
logger = openbomLogger.getLogger('BoMDocument')
from models.BoMGenerationParams import BoMGenerationParams

class BoMDocument:
    def __init__(self, id, name, version):
        self.extractorVersion = "1.0 beta"
        self.sourceProduct = openbomConfig.sourceProduct
        self.sourceProductVersion = version

        self.generationParams = None

        self.sourceId = id
        self.name = name
        self.configurationName = None

        self.created = ""
        self.createdBy = ""

        self.items = []

    def setGenerationParams(self, bomType):
        self.generationParams = BoMGenerationParams(bomType)

    def addItem(self, bomItem):
        if not bomItem:
            logger.warn('BoMDocument:Empty item cannot be include in teh BOM')
            return

        #increase qty in element already exist
        exist = next((x for x in self.items if x.sourceId == bomItem.sourceId), None)
        if exist:
            exist.quantity += 1
            exist.addRefDes(bomItem.refDes)
        else:
            bomItem.addRefDes(bomItem.refDes)
            self.items.append(bomItem)