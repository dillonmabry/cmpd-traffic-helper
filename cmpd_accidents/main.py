"""
Main module for data mining/gathering, persistence
"""
import argparse
import pkg_resources
from cmpd_accidents import MongoDBConnect
from cmpd_accidents import SoapService
from cmpd_accidents import WeatherService
from cmpd_accidents import CMPDService
from cmpd_accidents import loadFileAsString


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
    # SOAP Service
    wsdl = 'http://maps.cmpd.org/datafeeds/gisservice.asmx?op=CMPDAccidents'
    path = pkg_resources.resource_filename(
        'cmpd_accidents', 'resources/soap_descriptors/')
    body = loadFileAsString(path + 'cmpd_soap_descriptor.xml')
    headers = {'Content-Type': 'text/xml', 'accept': 'application/xml'}
    soap = SoapService(wsdl=wsdl, body=body, headers=headers)
    # Weather Service
    weather = WeatherService(
        endpoint='https://api.openweathermap.org/data/2.5/weather', apiKey=weatherApi)
    # CMPD Service
    cmpd = CMPDService(db, soap, weather)
    cmpd.update_traffic_data()


def main():
    """
    Main argparse for command line
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'host', help='Enter the db host to connect, full connection string')
    parser.add_argument('port', help='Enter the db port to connect', type=int)
    parser.add_argument(
        'weatherApi', help='Enter OpenWeatherAPI key to use for weather info')
    args = parser.parse_args()
    update_traffic_data(args.host, args.port, args.weatherApi)


if __name__ == '__main__':
    main()
