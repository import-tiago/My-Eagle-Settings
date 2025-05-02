import re

class OpenBOMAPIError(ValueError):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super(OpenBOMAPIError, self).__init__("{} {}".format(status_code, message))

    def getUserMessage(self):
        match = re.search('"message"\s*:\s*"([^"]*)"', self.message)
        if match:
            return match.group(1)
        else:
            return self.message

class OpenBOMAPIAuthorizationError(OpenBOMAPIError):
    def __init__(self, message):
        super(OpenBOMAPIAuthorizationError, self).__init__(401, message)

class OpenBOMAPILicenseError(OpenBOMAPIError):
    def __init__(self, message):
        super(OpenBOMAPILicenseError, self).__init__(402, message)

class ParameterEmptyExeption(Exception):
    def __init__(self, parameterName):
        super(MissedParameterExeption, self).__init__("Empty parameter: '{}'".format(parameterName))
