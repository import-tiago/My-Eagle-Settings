class BoMProperty:
    def __init__(self, name, value, propType):
        self.sourcePropertyId = name
        self.name = name
        self.value = value
        self.type = propType

    def setUnits(self, units):
        if units:
            self.displayName = '{} ({})'.format(self.name, units)