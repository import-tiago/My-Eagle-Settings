import json

class BoMStructure:
    def __init__(self):
        self.bomdocument = None
        self.inventorydocument = None

    def addBoM(self, bomDocument):
        if not self.bomdocument:
            self.bomdocument = []
        self.bomdocument.append(bomDocument)

    def addPartCatalog(self, bomDocument):
        if not self.inventorydocument:
            self.inventorydocument = []
        self.inventorydocument.append(bomDocument)

    def toJSON(self):
        #return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=False)