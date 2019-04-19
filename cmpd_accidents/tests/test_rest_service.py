from unittest import TestCase
from unittest.mock import patch, Mock
import requests
import cmpd_accidents


class TestRestService(TestCase):
    """ REST service integration tests """
    @patch('cmpd_accidents.RestService')
    def test_rest_sanity_check(self, RestMock):
        RestMock.return_value.get.return_value.text = "test"
        mock = cmpd_accidents.RestService('https://www.google.com')
        result = mock.get(params={})
        self.assertTrue(RestMock is cmpd_accidents.RestService)
        self.assertEqual(result.text, "test")

    def test_rest_init(self):
        mock_rest = cmpd_accidents.RestService('https://www.google.com')
        self.assertTrue(hasattr(mock_rest, 'endpoint'))
        self.assertTrue(hasattr(mock_rest, 'session'))
        self.assertTrue(hasattr(mock_rest, '__enter__'))
        self.assertTrue(hasattr(mock_rest, '__exit__'))
        self.assertTrue(hasattr(mock_rest, 'get'))
        self.assertTrue(hasattr(mock_rest, 'post'))

    def test_rest_operations(self):
        mock_rest = cmpd_accidents.RestService('https://www.google.com')
        inst = mock_rest.__enter__()
        print(type(inst))
        self.assertTrue(type(inst) == type(mock_rest))
        mock_rest.__exit__(None, None, None)
