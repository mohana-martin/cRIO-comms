class URLError(Exception):
    pass


class cRIOBadRequest(Exception):
    def __init__(self, cRIOresponse):
        self.msg = cRIOresponse["400 (Bad Request) response"]["message"]
        self.labView = cRIOresponse["400 (Bad Request) response"]["LabVIEW error"]

class cRIOWebServiceInactive(Exception):
    def __init__(self, cRIOresponse):
        self.msg = cRIOresponse["403 (Forbidden) response"]["message"]
