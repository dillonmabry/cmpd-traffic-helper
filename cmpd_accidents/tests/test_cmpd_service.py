from unittest import TestCase
from unittest.mock import patch
import cmpd_accidents

class TestCMPDService(TestCase):
    """ CMPD Service integration tests """
    @classmethod
    def setUpClass(self):
        """ Setup """
        # SOAP
        wsdl = 'http://maps.cmpd.org/datafeeds/gisservice.asmx?op=CMPDAccidents'
        body = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><CMPDAccidents xmlns="http://maps.cmpd.org/" /></soap:Body></soap:Envelope>"""
        headers = {'Content-Type': 'text/xml', 'accept': 'application/xml'}
        mock_soap = cmpd_accidents.SoapService(wsdl, body, headers)
        # DB
        mock_db = cmpd_accidents.MongoDBConnect("localhost", 27017)
        # Weather
        weather = cmpd_accidents.WeatherService(
            endpoint='https://samples.openweathermap.org/data/2.5/weather',
            apiKey='b6907d289e10d714a6e88b30761fae22'
            ) # fake API key via OpenWeatherAPI
        # CMPD
        self.mock_cmpd = cmpd_accidents.CMPDService(mock_db, mock_soap, weather)

    def test_cmpd_service_init(self):
        self.assertTrue(hasattr(self.mock_cmpd, 'database'))
        self.assertTrue(hasattr(self.mock_cmpd, 'soap_service'))
        self.assertTrue(hasattr(self.mock_cmpd, 'weather_service'))
        self.assertTrue(hasattr(self.mock_cmpd, 'update_traffic_data'))

    @patch('cmpd_accidents.MongoDBConnect')
    def test_cmpd_service_update(self, DBMock):
        """ Test mock db for integration """
        # SOAP
        wsdl = 'http://maps.cmpd.org/datafeeds/gisservice.asmx?op=CMPDAccidents'
        body = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><CMPDAccidents xmlns="http://maps.cmpd.org/" /></soap:Body></soap:Envelope>"""
        headers = {'Content-Type': 'text/xml', 'accept': 'application/xml'}
        mock_soap = cmpd_accidents.SoapService(wsdl, body, headers)
        print(mock_soap)
        # DB
        mock_db = cmpd_accidents.MongoDBConnect("localhost", 27017)
        print(mock_db)
        # Weather
        weather = cmpd_accidents.WeatherService(
            endpoint='https://samples.openweathermap.org/data/2.5/weather',
            apiKey='b6907d289e10d714a6e88b30761fae22'
            ) # fake API key via OpenWeatherAPI
        # CMPD
        mock_cmpd = cmpd_accidents.CMPDService(mock_db, mock_soap, weather)
        self.assertTrue(hasattr(mock_cmpd, "update_traffic_data"))
        result = mock_cmpd.update_traffic_data()
        self.assertTrue(result == None)