from unittest import TestCase
from unittest.mock import patch
import cmpd_accidents


class TestCMPDService(TestCase):
    """ CMPD Service integration tests """
    @classmethod
    def setUpClass(self):
        """ Setup """
        # REST
        endpoint = 'https://cmpdinfo.charlottenc.gov/api/v2/traffic'
        mock_rest = cmpd_accidents.RestService(endpoint)
        # DB
        mock_db = cmpd_accidents.MongoDBConnect("localhost")
        # Weather
        weather = cmpd_accidents.WeatherService(
            endpoint='https://samples.openweathermap.org/data/2.5/weather',
            apiKey='b6907d289e10d714a6e88b30761fae22'
        )  # fake API key via OpenWeatherAPI
        # CMPD
        self.mock_cmpd = cmpd_accidents.CMPDService(
            mock_db, mock_rest, weather)

    def test_cmpd_service_init(self):
        self.assertTrue(hasattr(self.mock_cmpd, 'database'))
        self.assertTrue(hasattr(self.mock_cmpd, 'rest_service'))
        self.assertTrue(hasattr(self.mock_cmpd, 'weather_service'))
        self.assertTrue(hasattr(self.mock_cmpd, 'update_traffic_data'))

    @patch('cmpd_accidents.MongoDBConnect')
    def test_cmpd_service_update(self, DBMock):
        """ Test mock db for integration """
        # REST
        endpoint = 'https://cmpdinfo.charlottenc.gov/api/v2/traffic'
        mock_rest = cmpd_accidents.RestService(endpoint)
        # DB
        mock_db = cmpd_accidents.MongoDBConnect("localhost")
        # Weather
        weather = cmpd_accidents.WeatherService(
            endpoint='https://samples.openweathermap.org/data/2.5/weather',
            apiKey='b6907d289e10d714a6e88b30761fae22'
        )  # fake API key via OpenWeatherAPI
        # CMPD
        mock_cmpd = cmpd_accidents.CMPDService(mock_db, mock_rest, weather)
        self.assertTrue(hasattr(mock_cmpd, "update_traffic_data"))
        mock_cmpd.update_traffic_data()
