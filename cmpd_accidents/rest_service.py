import requests
from requests.exceptions import RequestException
from cmpd_accidents import Logger


class RestService(object):
    """
    Service helper class for API requests
    Args:
        endpoint: URL endpoint
    """

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers.update(
            {'Content-Type': 'application/json'})  # default app/json
        self.logger = Logger('log', self.__class__.__name__,
                             maxbytes=10*1024*1024).get()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def get(self, params):
        """
        GET
        Args:
            params: parameters for request
        """
        try:
            r = self.session.request(
                method='get', url=self.endpoint, params=params)
            if (r.status_code == requests.codes.ok):
                self.logger.info(
                    "GET API endpoint request received, endpoint: {0}".format(self.endpoint))
                return r
            elif (r.status_code == requests.codes.bad_request):
                self.logger.error(
                    "Status: {0} | Bad Request. Check API Key or connectivity".format(r.status_code))
                raise Exception("Bad Request")
            elif (r.status_code == requests.codes.unauthorized):
                self.logger.error(
                    "Status: {0} | API Key is incorrect or restricted".format(r.status_code))
                raise Exception("Unauthorized")
            elif (r.status_code == requests.codes.forbidden):
                self.logger.error(
                    "Status: {0} | API Key is incorrect or restricted".format(r.status_code))
                raise Exception("Forbidden")
            elif (r.status_code == requests.codes.not_found):
                self.logger.error(
                    "Status: {0} | Not found".format(r.status_code))
                raise Exception("Not Found")
            else:
                self.logger.error(
                    "Status: {0} | An error has occurred".format(r.status_code))
                raise Exception("Internal server error")
        except RequestException as e:
            self.logger.exception(str(e))
            raise

    def post(self, payload, headers):
        """
        POST
        Args:
            payload: payload for request
            headers: headers for request (provides option to override headers for text/xml)
        """
        try:
            r = self.session.request(
                method='post', url=self.endpoint, data=payload, headers=headers)
            if (r.status_code == requests.codes.ok):
                self.logger.info(
                    "POST API endpoint request received, endpoint: {0}".format(self.endpoint))
                return r
            elif (r.status_code == requests.codes.bad_request):
                self.logger.error(
                    "Status: {0} | Bad Request. Check API Key or connectivity".format(r.status_code))
                raise Exception("Bad Request")
            elif (r.status_code == requests.codes.unauthorized):
                self.logger.error(
                    "Status: {0} | API Key is incorrect or restricted".format(r.status_code))
                raise Exception("Unauthorized")
            elif (r.status_code == requests.codes.forbidden):
                self.logger.error(
                    "Status: {0} | API Key is incorrect or restricted".format(r.status_code))
                raise Exception("Forbidden")
            elif (r.status_code == requests.codes.not_found):
                self.logger.error(
                    "Status: {0} | Not found".format(r.status_code))
                raise Exception("Not Found")
            else:
                self.logger.error(
                    "Status: {0} | An error has occurred".format(r.status_code))
                raise Exception("Internal server error")
        except RequestException as e:
            self.logger.exception(str(e))
            raise
