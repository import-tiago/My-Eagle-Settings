from models.BoMProperty import BoMProperty

class BoMItem:
    def __init__(self, id, name, image, level):
        self.sourceId = id
        self.name = name

        self.thumbnail = '{}.png'.format(image)
        self.itemLevel = level
        self.type = "Part"
        self.quantity = 1
        self.properties = None
        self.items = None
        self.refDes = None

    def addRefDes(self, des):
        if (des == None):
            return

        if (self.properties == None):
            self.addProperty("refDes", des)
        else:
            flag = True
            for property in self.properties:
                if property.name == "refDes":
                    flag = False
                    property.value += ", " + des

            if flag:
                self.addProperty("refDes", des)

    def addProperty(self, name, value, propType='string', units=None):
        if not self.properties:
            self.properties = []

        bomProperty = BoMProperty(name, value, propType)
        bomProperty.setUnits(units)

        self.properties.append(bomProperty)

        return bomProperty

    def addItem(self, bomItem):
        if not bomItem:
            return

        if not self.items:
            self.items = []
            self.type = "Assembly"

        #increase qty in element already exist
        exist = next((x for x in self.items if x.sourceId == bomItem.sourceId), None)
        if exist:
            exist.quantity += 1
            exist.addRefDes(bomItem.refDes)
            return
        else:
            bomItem.addRefDes(bomItem.refDes)
            self.items.append(bomItem)
