"""
Module for Weather API (OpenWeatherAPI)
https://openweathermap.org/api
"""
from cmpd_accidents import RestService


class WeatherService(object):
    """
    Class for Weather API operations
    Args:
        endpoint: endpoint for requests
        apiKey: the API key to use
        headers: headers to send
    """

    def __init__(self, endpoint, apiKey):
        self.apiKey = apiKey
        self.rest_service = RestService(endpoint=endpoint)

    def get(self, params):
        """
        Get request
        Args:
            params: the parameters for the request in dictionary
            Example parameters:
            https://api.openweathermap.org/data/2.5/weather?lat=35&lon=139&appid=<apiKey>
        """
        params["appid"] = self.apiKey
        res = self.rest_service.get(params=params)
        return res.json()
