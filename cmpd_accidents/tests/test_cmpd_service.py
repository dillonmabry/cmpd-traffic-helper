from unittest import TestCase
from unittest.mock import patch
import cmpd_accidents

class TestCMPDService(TestCase):
    """ Database integration tests """
    def test_cmpd_init(self):
        # SOAP
        wsdl = 'http://maps.cmpd.org/datafeeds/gisservice.asmx?op=CMPDAccidents'
        body = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><CMPDAccidents xmlns="http://maps.cmpd.org/" /></soap:Body></soap:Envelope>"""
        headers = {'Content-Type': 'text/xml', 'accept': 'application/xml'}
        mock_soap = cmpd_accidents.SoapService(wsdl, body, headers)
        # DB
        mock_db = cmpd_accidents.MongoDBConnect("localhost", 27017, "accidents")
        # Weather
        weather = cmpd_accidents.WeatherService(
            endpoint='https://samples.openweathermap.org/data/2.5/weather',
            apiKey='b6907d289e10d714a6e88b30761fae22'
            ) # fake API key via OpenWeatherAPI
        # CMPD
        mock_cmpd = cmpd_accidents.CMPDService(mock_db, mock_soap, weather)
        self.assertTrue(hasattr(mock_cmpd, 'database'))
        self.assertTrue(hasattr(mock_cmpd, 'soap_service'))
        self.assertTrue(hasattr(mock_cmpd, 'weather_service'))
        self.assertTrue(hasattr(mock_cmpd, 'update_traffic_data'))