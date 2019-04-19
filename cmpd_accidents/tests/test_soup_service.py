from unittest import TestCase
from unittest.mock import patch
import cmpd_accidents


class TestSoapService(TestCase):
    """ bs4/Soup service integration tests """
    @patch('cmpd_accidents.SoupService')
    def test_soup_sanity_check(self, SoupMock):
        SoupMock.return_value.findAll.return_value = "test"
        mock = cmpd_accidents.SoupService('<tag>test</tag>', 'lxml')
        result = mock.findAll('tag')
        self.assertTrue(SoupMock is cmpd_accidents.SoupService)
        self.assertEqual(result, "test")

    def test_soup_init(self):
        mock_soup = cmpd_accidents.SoupService('<tag>test</tag>', 'lxml')
        self.assertTrue(type(mock_soup) == cmpd_accidents.SoupService)
        self.assertTrue(hasattr(mock_soup, '__init__'))
        self.assertTrue(hasattr(mock_soup, 'findAll'))
        self.assertTrue(hasattr(mock_soup, 'get_text'))
        self.assertTrue(hasattr(mock_soup, 'get_json'))

    def test_soup_operations(self):
        mock_soup = cmpd_accidents.SoupService("""<?xml version="1.0" encoding="UTF-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><soap:Body><CMPDAccidentsResponse xmlns="http://maps.cmpd.org/"><CMPDAccidentsResult><ACCIDENTS><EVENT_NO>string</EVENT_NO><DATETIME_ADD>dateTime</DATETIME_ADD><DIVISION>string</DIVISION><ADDRESS>string</ADDRESS><EVENT_TYPE>string</EVENT_TYPE><EVENT_DESC>string</EVENT_DESC><X_COORD>decimal</X_COORD><Y_COORD>decimal</Y_COORD><LATITUDE>decimal</LATITUDE><LONGITUDE>decimal</LONGITUDE></ACCIDENTS><ACCIDENTS><EVENT_NO>string</EVENT_NO><DATETIME_ADD>dateTime</DATETIME_ADD><DIVISION>string</DIVISION><ADDRESS>string</ADDRESS><EVENT_TYPE>string</EVENT_TYPE><EVENT_DESC>string</EVENT_DESC><X_COORD>decimal</X_COORD><Y_COORD>decimal</Y_COORD><LATITUDE>decimal</LATITUDE><LONGITUDE>decimal</LONGITUDE></ACCIDENTS></CMPDAccidentsResult></CMPDAccidentsResponse></soap:Body></soap:Envelope>""", 'lxml')
        results = mock_soup.findAll('accidents')
        self.assertTrue(results is not None)
        text = mock_soup.get_text('event_no')
        self.assertTrue(text is not None)
        self.assertTrue(type(text) == list)
        self.assertTrue('string' in text)
        json = mock_soup.get_json(results)
        self.assertTrue(type(json) == list)
        self.assertTrue(len(json) != 0)
        self.assertTrue('event_no' in json[0])
