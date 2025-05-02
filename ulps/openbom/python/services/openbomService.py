try:
    import os
    import getpass
    import sys
    import json
    import requests
    import openbomConfig
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import secrets
    import pkce
    import socket
    import threading
    import webbrowser
    import time
    import urllib.parse as urlparse
    from urllib.parse import parse_qs
    from models.Object import Object
    from models.BoMStructure import BoMStructure
    from helpers.openbomDialogHelper import OpenBOMDialogHelper
    from helpers import openbomLogger
    logger = openbomLogger.getLogger('OpenBOMService')
    from exceptions.OpenBOMAPIError import (OpenBOMAPIError, OpenBOMAPIAuthorizationError, OpenBOMAPILicenseError)
except ImportError as ex:
    from helpers import openbomLogger
    logger = openbomLogger.getLogger('OpenBOMService')
    logger.error('OpenBOMAPI: import %s failed. ', ex.name)
    raise ImportError('OpenBOMAPI: import requests failed.')

__getSessionURL__ = "api/v1/authn"

class MFAhandler(BaseHTTPRequestHandler):

    access_token_available = threading.Event()

    #auxilary params
    initialState = None
    codeVerifier = None
    tokenRequestUri = None
    accessToken = None
    accessTokenResponseObject = None
    port = None

    def do_GET(self):
        request_path = self.path
        parsed = urlparse.urlparse(request_path)
        dict_req = parse_qs(parsed.query)
        if (dict_req and 'code' in dict_req and 'state' in dict_req) :
            code = dict_req['code'][0]
            state = dict_req['state'][0]
            if (MFAhandler.initialState == dict_req['state'][0]) :
                # code exchange at the Token Endpoint
                redirectUri = "http://localhost:{0}".format(str(MFAhandler.port))
                headers = {'Content-type': 'application/json', 'Accept': '*/*'}
                dict_body = {'code': code,'redirect_uri': redirectUri,'code_verifier': MFAhandler.codeVerifier}
                r = requests.post(MFAhandler.tokenRequestUri, data=json.dumps(dict_body), headers=headers)
                at_json = r.json()
                if (at_json and 'access_token' in at_json) :
                    MFAhandler.accessTokenResponseObject = OpenBOMAPI.processHTTPResponse(r)
                    MFAhandler.accessToken = at_json['access_token']
                    MFAhandler.access_token_available.set()

        self.send_response_only(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        message = "<html><head><meta http-equiv='refresh'></head><body>OpenBOM authentication finished. Please return to the Eagle application.</body></html>"
        self.wfile.write(bytes(message, "utf8"))

class OpenBOMAPI:
    @classmethod
    def fromJson(cls, data):
        if not data:  # check for None
            return None
        if not data.strip():  # check for empty string
            return None

        return json.loads(data, object_hook=lambda d: Object(**d))

    @classmethod
    def toJson(cls, data):
        return json.dumps(data, default=lambda o: o.__dict__, sort_keys=False)

    @classmethod
    def getApiUrl(cls):
        return openbomConfig.openBoMUrl.replace("https://bom", "https://api")

    @classmethod
    def processHTTPResponse(cls, response):
        status_code = response.status_code
        logger.debug('OpenBOMAPI: status_code:"%s". text:"%s"', status_code, response.text)
        if requests.codes.unauthorized == status_code:
            if ( __getSessionURL__ in response.url ) :
                raise OpenBOMAPIError(response.status_code, "The credentials provided were invalid.")
            else :
                raise OpenBOMAPIAuthorizationError(response.text)
        elif requests.codes.ok != status_code and requests.codes.created != status_code:
            if "Access Denied" in response.text and "requires license" in response.text:
                raise OpenBOMAPILicenseError(response.text)
            else:
                raise OpenBOMAPIError(response.status_code, response.text)

        return cls.fromJson(response.text)

    @classmethod
    def getAccessToken(cls, login, password):
        baseUrl = cls.getApiUrl()
        url = "{}/v1/oauth/token".format(baseUrl)
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        data = {'grant_type': 'password', 'username': login, 'password': password}
        logger.debug('requests POST:%s', url)
        response = requests.post(url, headers=headers, data=data)
        data = cls.processHTTPResponse(response)
        return data

    @classmethod
    def getSessionToken(cls, login, password):
        baseUrl = cls.getLoginUrl()

        url = "{0}/{1}".format(baseUrl,__getSessionURL__)
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        data = {'username': login, 'password': password}

        logger.debug('requests POST:%s', url)
        response = requests.post(url, headers=headers, data=json.dumps(data))
        data = cls.processHTTPResponse(response)
        temp_json_keeper = json.loads(response.text)
        return temp_json_keeper['sessionToken']

    @classmethod
    def getMFAfreePort(cls):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mfa_ports_predefined = [3000, 9090, 9091, 9092]
        for mfa_port in mfa_ports_predefined:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(("localhost", mfa_port))
                sock.close()
                return mfa_port
            except:
                logger.info('Local port : %s is busy', str(mfa_port))

        raise Exception("Authorization failed. No free ports among: " + str(mfa_ports_predefined))

    @classmethod
    def getLoginUrl(cls):
        return openbomConfig.openBoMUrl.replace("https://bom", "https://login")

    @classmethod
    def getSignoutUrl(cls):
        return cls.getLoginUrl() + '/login/signout'

    @classmethod
    def getCodeExchangeUrl(cls):
        return openbomConfig.openBoMUrl + '/code-exchange'

    @classmethod
    def getClientId(cls):
        return openbomConfig.clientId

    @classmethod
    def getAuthEndPoint(cls):
        return openbomConfig.authEndPoint

    @classmethod
    def MFAauthorize(cls, session_token):
        clientId = cls.getClientId()
        mfa_port = cls.getMFAfreePort()
        redirectUri = "http://localhost:{}".format(str(mfa_port))
        state = secrets.token_urlsafe(64)
        codeVerifier = pkce.generate_code_verifier(length=64)
        codeChallenge = pkce.get_code_challenge(codeVerifier)
        #
        MFAhandler.initialState = state
        MFAhandler.codeVerifier = codeVerifier
        MFAhandler.tokenRequestUri = cls.getCodeExchangeUrl()
        MFAhandler.port = mfa_port
        #
        server = HTTPServer(("localhost", mfa_port), MFAhandler)
        t = threading.Thread(target=server.serve_forever)
        t.daemon = True
        t.start()
        #
        baseUrl = cls.getLoginUrl()
        signOutURL = cls.getSignoutUrl()
        authEndPoint = cls.getAuthEndPoint()
        authorizationEndpoint = "{0}?fromURI={1}/oauth2/{2}/v1/authorize".format(signOutURL,baseUrl,authEndPoint)

        uriCallback = redirectUri
        codeChallengeMethod = "S256"
        authorizationRequest = "{0}?response_type=code&scope=openid%20profile&redirect_uri={1}&client_id={2}&state={3}&code_challenge={4}&code_challenge_method={5}&sessionToken={6}".format(authorizationEndpoint,uriCallback,clientId,state,codeChallenge,codeChallengeMethod,session_token)
        authorizationRequest = authorizationRequest.replace('&', '%26')
        logger.debug('webbrowser open auth request:%s', authorizationRequest)
        webbrowser.open(authorizationRequest)

        MFAhandler.access_token_available.wait(20) #wait until user will enter MFA pin

        server.shutdown()
        if (MFAhandler.accessToken) :
            return MFAhandler.accessTokenResponseObject

        raise Exception("Authorization failed. No access token obtained.")


    def __init__(self, access_token, refresh_token):
        if not access_token:
            raise OpenBOMAPIAuthorizationError("Unauthorize")

        self.baseUrl = self.getApiUrl()
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.baseHeaders = {"Content-Type": "application/json", "Accept": "application/json"}

        #check acess token
        userInfo = self.getUserInfo()
        if not userInfo.email:
            raise OpenBOMAPIAuthorizationError("invalid access token")

    def getUserInfo(self):
        if not self.access_token:
            raise OpenBOMAPIAuthorizationError("Unauthorized")
        url = "{}/me".format(openbomConfig.openBoMUrl)
        headers = self.baseHeaders.copy()
        headers["Authorization"] = "Bearer {}".format(self.access_token)

        logger.debug('requests GET:"%s"', url)
        response = requests.get(url, headers=headers)
        data = self.processHTTPResponse(response)
        if not data:
            raise OpenBOMAPIAuthorizationError("Unauthorized")

        logger.debug('connected as OpenBOM user:%s', data.account.email)
        return data.account

    def sendBOMDocument(self, bomDocument):
        if not self.access_token:
            raise OpenBOMAPIAuthorizationError("Unauthorized")

        url = "{}/v1/api/import/bom?token={}".format(self.baseUrl, self.access_token)

        bomStructure = BoMStructure()
        bomStructure.addBoM(bomDocument)
        bomJson = bomStructure.toJSON()
        logger.debug('JSON extracted:%s', bomJson)

        logger.debug('requests POST:"%s"', url)
        response = requests.post(url, headers=self.baseHeaders, data=bomJson)
        data = self.processHTTPResponse(response)
        return data[0]

    def sendCatalog(self, bomDocuments):
        if not self.access_token:
            raise OpenBOMAPIAuthorizationError("Unauthorized")

        url = "{}/v1/api/import/inventory?token={}".format(self.baseUrl, self.access_token)

        bomStructure = BoMStructure()
        for doc in bomDocuments:
            bomStructure.addPartCatalog(doc)
        bomJson = bomStructure.toJSON()
        logger.debug('JSON extracted:%s', bomJson)

        logger.debug('requests POST:"%s"', url)
        response = requests.post(url, headers=self.baseHeaders, data=bomJson)
        data = self.processHTTPResponse(response)
        return data

    def sendThumbnails(self, bomId, thumbnails):
        if not thumbnails:
            logger.warn('BOM/catalog "%s" has no images', bomId)
            return
        if not self.access_token:
            raise OpenBOMAPIAuthorizationError("Unauthorized")

        url = "{}/v1/api/import/bom/{}/image?contentType=image%2Fpng&token={}".format(self.baseUrl, bomId, self.access_token)

        files = []
        for filePath in thumbnails:
            if not os.path.exists(filePath):
                logger.warn('Preview is not exist. path:%s', filePath)
                continue

            fileName = os.path.basename(filePath)
            files.append(('file', (fileName, open(filePath, 'rb'), 'image/png')))
            logger.debug('file "%s" has been added to send image request. path:"%s"', fileName, filePath)

        logger.debug('requests POST:"%s". image count:"%d"', url, len(files))
        response = requests.post(url, files=files)
        data = self.processHTTPResponse(response)
        logger.debug('response POST:"%s" data:"%s"', url, data)

    def getBOMDocuments(self, product, sourceId):
        if not self.access_token:
            raise OpenBOMAPIAuthorizationError("Unauthorized")

        url = "{}/v1/api/document/product/Eagle?".format(self.baseUrl)
        logger.debug('requests GET:"%s"', url)

        params = [('sourceId', sourceId), ('token', self.access_token)]
        response = requests.get(url, headers=self.baseHeaders, params=params)

        data = self.processHTTPResponse(response)
        return data

    def getBOMCatalogs(self, product, sourceId):
        if not self.access_token:
            raise OpenBOMAPIAuthorizationError("Unauthorized")

        url = "{}/v1/api/inventory/product/Eagle?".format(self.baseUrl)
        logger.debug('requests GET:"%s"', url)

        params = [('sourceId', sourceId), ('token', self.access_token)]
        response = requests.get(url, headers=self.baseHeaders, params=params)

        data = self.processHTTPResponse(response)
        return data

    @classmethod
    def getLastAddinMetadata(cls):
        baseUrl = cls.getApiUrl()

        if 'darwin' == sys.platform:
            url = "{}/v1/api/import/plugin/info/Eagle-MAC".format(baseUrl)
        else:
            url = "{}/v1/api/import/plugin/info/Eagle-WIN".format(baseUrl)

        logger.debug('requests GET:"%s"', url)
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}

        response = requests.get(url, headers=headers)
        return cls.processHTTPResponse(response)
