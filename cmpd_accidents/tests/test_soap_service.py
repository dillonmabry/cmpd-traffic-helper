from unittest import TestCase
from unittest.mock import patch
import requests
import cmpd_accidents


class TestSoapService(TestCase):
    """ Soap service integration tests """
    @patch('cmpd_accidents.SoapService')
    def test_soap_sanity_check(self, SoapMock):
        SoapMock.return_value.post.return_value = "test"
        mock = cmpd_accidents.SoapService(
            'http://example.com', 'test', {"content-type": "text/xml"})
        result = mock.post()
        self.assertTrue(SoapMock is cmpd_accidents.SoapService)
        self.assertEqual(result, "test")

    def test_soap_init(self):
        wsdl = 'http://maps.cmpd.org/datafeeds/gisservice.asmx?op=CMPDAccidents'
        body = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><CMPDAccidents xmlns="http://maps.cmpd.org/" /></soap:Body></soap:Envelope>"""
        headers = {'Content-Type': 'text/xml', 'accept': 'application/xml'}
        soap = cmpd_accidents.SoapService(wsdl, body, headers)
        self.assertTrue(hasattr(soap, 'rest_service'))
        self.assertTrue(hasattr(soap, 'body') and soap.body == body)
        self.assertTrue(hasattr(soap, 'headers') and soap.headers == headers)

    def test_soap_req(self):
        wsdl = 'http://maps.cmpd.org/datafeeds/gisservice.asmx?op=CMPDAccidents'
        body = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><CMPDAccidents xmlns="http://maps.cmpd.org/" /></soap:Body></soap:Envelope>"""
        headers = {'Content-Type': 'text/xml', 'accept': 'application/xml'}
        soap = cmpd_accidents.SoapService(wsdl, body, headers)
        result = soap.post()
        self.assertTrue(result is not None and type(result) == str)
        self.assertTrue('ACCIDENTS' in result)

    def test_soap_not_found(self):
        wsdl = 'http://maps.cmpd.org/datafeeds/gisservice.badreq'  # not found
        body = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><CMPDAccidents xmlns="http://maps.cmpd.org/" /></soap:Body></soap:Envelope>"""
        headers = {'Content-Type': 'text/xml', 'accept': 'application/xml'}
        soap = cmpd_accidents.SoapService(wsdl, body, headers)
        with self.assertRaises(Exception) as mockexception:
            result = soap.post()

    def test_soap_internal_error(self):
        wsdl = 'http://maps.cmpd.org/datafeeds/gisservice.asmx?op=CMPDAccidents'  # not found
        body = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"></soap:Envelope>"""
        headers = {'Content-Type': 'text/xml', 'accept': 'application/xml'}
        soap = cmpd_accidents.SoapService(wsdl, body, headers)
        with self.assertRaises(Exception) as mockexception:
            result = soap.post()
