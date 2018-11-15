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
		self.logger = Logger('log', self.__class__.__name__, maxbytes=10*1024*1024).get()

	def post(self):
		"""
		Send SOAP request (POST)
		"""
		try:
			res = requests.post(self.wsdl, data=self.body, headers=self.headers)
			self.logger.info("Successfully processed request, response: {0}".format(res))
			return res.text
		except Exception as e:
			self.logger.exception(str(e))
			raise e
