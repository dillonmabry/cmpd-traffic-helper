"""
Module for SOAP interface
"""
from cmpd_accidents import RestService


class SoapService(object):
    """
    Class for SOAP operations
    Args:
        wsdl: The web service to use with method as parameter
        body: The web service descriptor
        headers: headers to send
    """

    def __init__(self, wsdl, body, headers):
        self.body = body
        self.headers = headers
        self.rest_service = RestService(endpoint=wsdl)

    def post(self):
        """
        Send SOAP request (POST) and receive response
        """
        res = self.rest_service.post(payload=self.body, headers=self.headers)
        return res.text
