from unittest import TestCase
from unittest.mock import patch
import cmpd_accidents


class TestWeatherService(TestCase):
    """ OpenWeatherAPI integration tests """
    @patch('cmpd_accidents.WeatherService')
    def test_weather_sanity_check(self, WeatherMock):
        WeatherMock.return_value.get.return_value = "test"
        mock = cmpd_accidents.WeatherService(
            endpoint='http://samples.openweathermap.org/data/2.5/weather',
            apiKey='b6907d289e10d714a6e88b30761fae22'
        )  # fake API key via OpenWeatherAPI
        result = mock.get(params={'lat': 35, 'lon': 139})
        self.assertTrue(WeatherMock is cmpd_accidents.WeatherService)
        self.assertEqual(result, "test")

    def test_weather_init(self):
        mock_weather = cmpd_accidents.WeatherService(
            endpoint='http://samples.openweathermap.org/data/2.5/weather',
            apiKey='b6907d289e10d714a6e88b30761fae22'
        )  # fake API key via OpenWeatherAPI
        self.assertTrue(type(mock_weather) == cmpd_accidents.WeatherService)
        self.assertTrue(hasattr(mock_weather, '__init__'))
        self.assertTrue(hasattr(mock_weather, 'get'))

    def test_weather_operations(self):
        mock_weather = cmpd_accidents.WeatherService(
            endpoint='http://samples.openweathermap.org/data/2.5/weather',
            apiKey='b6907d289e10d714a6e88b30761fae22'
        )  # fake API key via OpenWeatherAPI
        results = mock_weather.get(params={'lat': 35, 'lon': 139})
        self.assertTrue(results is not None)
