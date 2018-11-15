"""
Module for SOAP interface
"""
import requests
from cmpd_accidents import Logger

class SoapService(object):
    """
    Class for SOAP operations
    Args:
        wsdl: The web service to use with method as parameter
        body: The web service descriptor
        headers: headers to send
    """
    def __init__(self, wsdl, body, headers):
        self.wsdl = wsdl
        self.body = body
        self.headers = headers
        self.logger = Logger('log', self.__class__.__name__, maxbytes=10 * 1024 * 1024).get()

    def post(self):
        """
        Send SOAP request (POST)
        """
        try:
            res = requests.post(self.wsdl, data=self.body, headers=self.headers)
            if res.status_code == requests.codes.ok:
                self.logger.info('Successfully processed request, response: {0}'.format(res.status_code))
                return res.text
            elif res.status_code == requests.codes.bad_request:
                self.logger.error('Bad request, response: {0}'.format(res.status_code))
                raise Exception('Bad Request')
            elif res.status_code == requests.codes.server_error:
                self.logger.error('Internal Server error, response: {0}'.format(res.status_code))
                raise Exception('Internal Server Error')
            else:
                raise Exception('Something went wrong, check status or logs: {0}'.format(res.status_code))
        except Exception as e:
            self.logger.exception(str(e))
            raise e