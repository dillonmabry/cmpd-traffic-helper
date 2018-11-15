from setuptools import setup

setup(name = 'cmpd_accidents',
    version = '0.1.0',
    description = 'Get CMPD Traffic Data via SOAP GIS Service',
    author = 'Dillon Mabry',
    author_email = 'rapid.dev.solutions@gmail.com',
    license = 'MIT',
    packages = ['cmpd_accidents'],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
    install_requires = ['pymongo', 'requests', 'bs4'],
    include_package_data = True,
    data_files = [('', [
        'cmpd_accidents/resources/cmpd_soap_descriptor.xml'
    ])],
    zip_safe = False)