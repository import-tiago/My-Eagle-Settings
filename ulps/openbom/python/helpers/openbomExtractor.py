import os

import re
import shutil
import urllib.parse
import Util
from xml.dom import minidom

from exceptions.OpenBOMAPIError import ParameterEmptyExeption
from helpers import openbomLogger, openbomTagsRemover
logger = openbomLogger.getLogger('Extractor')
from helpers.openbomLocateHelper import OpenBOMLocateHelper
from models.BoMType import BoMType
from models.BoMDocument import BoMDocument
from models.BoMItem import BoMItem
from services.openbomService import OpenBOMAPI
from services.openbomSettingsService import OpenBOMSettingsService


class OpenBOMExtractor():
    access_token = None
    refresh_token = None
    criterias = False
    bomName = None

    def __init__(self, doc):
        super().__init__()
        try:
            file = doc.getAttribute("headline")
            self.fileVersion = 0
            self.getBomName(doc)
        except Exception as ex:
            self.fileId = None
            logger.warn("Model initialization error, %s", ex)
            raise Exception("Model initialization error")

        self.thumbnailList = []

    """Should store credentials for requests to API
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

    '''Should call BOM/Catalog creation
    Args:
       param (string): object type (BOM/Catalog)
       param (string): full path to xml object file
    Returns:
       none
    '''
    @classmethod
    def createBOM(cls, bomType, path):
        #int OpenBOM API
        api = OpenBOMAPI(cls.access_token, cls.refresh_token)

        try:
            #retrive path to folder with assembly/catalog images (footprints)
            cls.imageFolderPath = path.replace(".xml", "/")

            # parse xml with assembly/catalog infromation
            document = minidom.parse(path)
            logger.debug('Creating "%s"', bomType)
            documentList = []
            thumbnailList = dict()
            bomData = None
            if BoMType.Catalog == bomType:
                libraries = document.getElementsByTagName("library")
                if not libraries or libraries.length == 0:
                    raise Exception('Eagle do not have libraries')
                for library in libraries:
                    bomExtractor = OpenBOMExtractor(library)
                    bomDocument = bomExtractor.getCatalog(library)
                    documentList.append(bomDocument)

                    if bomExtractor.thumbnailList:
                        thumbnailList[bomExtractor.bomName] = bomExtractor.thumbnailList

                bomData = api.sendCatalog(documentList)

            elif BoMType.SingleLevelBOM == bomType:
                singleboms = document.getElementsByTagName("schematic")
                if not singleboms or singleboms.length == 0:
                    raise Exception("Eagle do not have schematic")
                singlebom = singleboms[0]
                bomExtractor = OpenBOMExtractor(singlebom)
                bomDocument = bomExtractor.getSingleBOM(singlebom)

                if bomExtractor.thumbnailList:
                    thumbnailList[os.path.splitext(bomExtractor.bomName)[0]] = bomExtractor.thumbnailList

                bomData = api.sendBOMDocument(bomDocument)

                if not isinstance(bomData, list):
                    bomData = [bomData]
            else:
                raise Exception('Unsupported BOM type:"' + bomType + '"\nBOM were not created.', 'Unsupported BOM')
                return

            if not bomData:
                raise Exception("Data transfer failed")
                return

            #send thumbnails
            try:
                if thumbnailList:
                    for item in bomData:
                        thumbnails = cls.getThumbnailsByName(thumbnailList, item.name)
                        api.sendThumbnails(item.id, thumbnails)
            except Exception as ex:
                logger.warn("Failed to send images, %s", ex)
                pass

            if len(bomData) == 1:
                OpenBOMLocateHelper.generateItemLink(bomData[0].id, bomType)
            else:
                results = []
                for item in bomData:
                    results.append({"name": item.name, "url": Util.getBoMUrl(item.id, bomType)})
                return results

            try:
                os.remove(path)
                shutil.rmtree(path.replace(".xml", ""))
            except:
                logger.warn("Files not found. Cleanup skipped")
                pass
        except Exeption as ex:
            logger.error("createBOM: %s", ex)
            raise Exception("We were unable to create BOM")

    '''Should generate part from xml
    Args:
       param (string): component (part element in xml object)
       param (int): level of part
    Returns:
       (BoMItem) new part
    '''
    def initBoMDocument(self, bomId, bomName, version, bomType):
        bomDocument = BoMDocument(bomId, bomName, version)
        bomDocument.sourceId = bomId
        bomDocument.createdBy = os.getlogin()
        bomDocument.setGenerationParams(bomType)
        return bomDocument

    def getCatalog(self, component):
        if not component:
            logger.warn('Empty component detected...')
            return

        bomName = self.getBomName(component)
        version = component.getAttribute("version")
        version = re.search(r'Version\s*([\d.]+)', version).group(1)

        bomDocument = self.initBoMDocument(bomName, bomName, version, BoMType.Catalog)
        logger.debug('preparing Catalog. %s', bomName)

        components = component.getElementsByTagName("device")
        if not components or components.length == 0:
            raise Exception('Library do not have components')
        else:
            for comp in components:
                subItem = self.getBoMItemFromComponent(comp, 0)
                bomDocument.addItem(subItem)

        return bomDocument

    def getSingleBOM(self, schematic):
        if not schematic:
            logger.warn('Empty schematic detected...')
            return

        bomName = os.path.splitext(schematic.getAttribute("name"))[0]
        version = schematic.getAttribute("version")
        bomDocument = self.initBoMDocument(bomName, bomName, version, BoMType.SingleLevelBOM)
        logger.debug('preparing SingleLevel BOM. %s', bomName)

        components = schematic.getElementsByTagName("part")
        if not components or components.length == 0:
            raise Exception('BOM do not have components')
        else:
            for comp in components:
                subItem = self.getBoMItemFromComponent(comp, 0)
                bomDocument.addItem(subItem)

        return bomDocument

    '''Should generate part id by partNumber, value and custom properties if they exists
    Args:
       param (string): partNumber
       param (string): value
       param (attributes): list of part's attributes
    Returns:
       (string) unique id of part
    '''
    def getItemId(self, partNumber, value, attributes):
        itemId = partNumber + '_' + value

        # retrieve required grouping criteria
        criteria = self.getGroupCriteria()
        if not criteria:
            return itemId
        try:
            for attribute in attributes:
                name = attribute.getAttribute("name")
                if name in criteria:
                    itemId += '_' + attribute.getAttribute("value")
        except:
            logger.debug('getAttributes. No attributes found')
        finally:
            return itemId

    '''Should generate part from xml
    Args:
       param (string): component (part element in xml object)
       param (int): level of part
    Returns:
       (BoMItem) new part
    '''
    def getBoMItemFromComponent(self, component, currentLevel):
        if not component:
            logger.warn('Empty component detected...')
            return

        bomItemId = component.getAttribute("name")
        packageName = component.getAttribute("package_name")
        description = component.getAttribute("description")
        value = component.getAttribute("value")
        partName = component.getAttribute("part_name")
        hasImage = component.getAttribute("hasImage")
        attributes = component.getElementsByTagName("attribute")

        # create new BOM item
        bomId = self.getItemId(bomItemId, value, attributes)
        bomItem = BoMItem(bomId, bomItemId, packageName, currentLevel)

        print('Creating item. id: ', bomItem.sourceId, ' name: ', bomItem.name)
        logger.debug('Creating item. id:"%s" name:"%s"', bomItem.sourceId, bomItem.name)

        bomItem.addProperty("Part Number", bomItemId)
        bomItem.addProperty("Description", openbomTagsRemover.toTextHtml(description))
        bomItem.addProperty("Package Name", packageName)

        # add custom attributes
        self.getAttributes(bomItem, attributes)
        if (value != None and len(value) > 0):
            bomItem.addProperty("Value", value)

        if (partName != None and len(partName) > 0):
            bomItem.refDes = partName

        # add image if exists
        if (hasImage == "true"):
            # add image
            imageName = urllib.parse.quote_plus(bomItem.thumbnail)

            folder = self.imageFolderPath
            packageLibrary = component.getAttribute("package_library")

            if folder.find("allCatalogs") > 0:
                packageLibraryFolder = urllib.parse.quote(packageLibrary)
                folder = folder.replace("allCatalogs", packageLibraryFolder)

            self.thumbnailList.append(os.path.join(folder, imageName))
        else:
            bomItem.thumbnail = None
        logger.debug('Properties initialized. id:"%s" name:"%s" count:"%s"', bomItem.sourceId, bomItem.name, bomItem.properties.count)
        return bomItem

    '''Should add custom attributes from assembly/catalog xml to a new item
    Args:
       param (object): new bomItem 
       param (attributes): list of part's attributes
    Returns:
       none
    '''
    def getAttributes(self, bomItem, attributes):
        try:
            for attribute in attributes:
                name = attribute.getAttribute("name")
                value = attribute.getAttribute("value")
                bomItem.addProperty(name, value)
        except:
            logger.debug('getAttributes. No attributes found')

    '''Should retrieve group criteria from settings
    Args:
        none
    Returns:
       (Array) List of criteria or False if it not exists
    '''
    @classmethod
    def getGroupCriteria(self):
        if self.criterias:
            return self.criterias
        try:
            settings = OpenBOMSettingsService.readSettings()
            if (not settings.groupByEnabled or settings.groupByEnabled == 0):
                return False

            if (len(settings.groupByCriteria.strip()) == 0):
                return False
            self.criterias = [x.strip() for x in settings.groupByCriteria.split(';')]
            return self.criterias
        except Exception:
            return False

    @classmethod
    def getThumbnailsByName(cls, thumbnailList, name):
        if not thumbnailList:
            raise ParameterEmptyExeption("thumbnailList")
        if not name:
            raise ParameterEmptyExeption("name")
        for key in thumbnailList.keys():
            if key == name:
                return thumbnailList[key]
            x = re.search("^(.+)(-\d+)$", name)
            if x and x.group(1) == key:
                return thumbnailList[key]
        return None

    @classmethod
    def getBomName(self, component):
        if not component:
            raise ParameterEmptyExeption("component")
        bomPath = component.getAttribute("name")
        bomName = component.getAttribute("headline")
        if (bomName == None or len(bomName) == 0):
            bomName = os.path.basename(bomPath)

        self.bomName = bomName
        return self.bomName
