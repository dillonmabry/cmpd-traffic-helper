"""
Main module for data mining/gathering, persistence
"""
import argparse
import pkg_resources
import os
from cmpd_accidents import MongoDBConnect
from cmpd_accidents import RestService
from cmpd_accidents import WeatherService
from cmpd_accidents import CMPDService


def update_traffic_data(host, port, weatherApi):
    """
    Updates traffic data for persistence Mongo connector
    Args:
        host: db host to connect to
        port: db port
        weatherApi: api key for OpenWeatherAPI
    """
    # DB Service
    db = MongoDBConnect(host, port)
    # REST Service
    endpoint = 'https://cmpdinfo.charlottenc.gov/api/v2/traffic'
    service = RestService(endpoint)
    # Weather Service
    weather = WeatherService(
        endpoint='https://api.openweathermap.org/data/2.5/weather', apiKey=weatherApi)
    # CMPD Service
    cmpd = CMPDService(db, service, weather)
    cmpd.update_traffic_data()


def main():
    if os.getenv('HOST') and os.getenv('PORT') and os.getenv('WEATHER_API'):
        """ From Environment variables """
        update_traffic_data(os.getenv('HOST'), int(
            os.getenv('PORT')), os.getenv('WEATHER_API'))
    else:
        """ From Main argparse for command line """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'host', help='Enter the db host to connect, full connection string')
        parser.add_argument(
            'port', help='Enter the db port to connect', type=int)
        parser.add_argument(
            'weatherApi', help='Enter OpenWeatherAPI key to use for weather info')
        args = parser.parse_args()
        update_traffic_data(args.host, args.port, args.weatherApi)


if __name__ == '__main__':
    main()
