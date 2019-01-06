from setuptools import setup

setup(name = 'charlotte_traffic_analysis',
    version = '0.1.0',
    description = 'Charlotte-metro traffic analysis helper including predictions, travel paths, and more',
    author = 'Dillon Mabry',
    author_email = 'rapid.dev.solutions@gmail.com',
    license = 'MIT',
    packages = ['cmpd_accidents', 'traffic_analyzer'],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    install_requires = ['pymongo', 'requests', 'lxml', 'bs4', 'sqlalchemy', 'pymysql', 'numpy', 'pandas', 'scikit-learn', 'xgboost', 'shapely'],
    include_package_data = True,
    data_files = [('', [
        'cmpd_accidents/resources/soap_descriptors/cmpd_soap_descriptor.xml',
        'cmpd_accidents/resources/db/mysql_create_accidents.sql',
        'traffic_analyzer/resources/census_income.csv',
        'traffic_analyzer/resources/census_population.csv',
        'traffic_analyzer/resources/roads.csv',
        'traffic_analyzer/resources/signals.csv',
        'traffic_analyzer/resources/traffic_volumes.csv'
    ])],
    zip_safe = False)