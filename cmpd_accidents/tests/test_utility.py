from unittest import TestCase
import pkg_resources
from cmpd_accidents import loadFileAsString

class TestUtility(TestCase):
    """ Test utilities """
    def test_load_file_string(self):
        path = pkg_resources.resource_filename('cmpd_accidents', 'resources/soap_descriptors/')
        string = loadFileAsString(path + 'cmpd_soap_descriptor.xml')
        self.assertTrue(type(string) == str)
        self.assertTrue(len(string) != 0)

    def test_load_file_string_invalid(self):
        path = pkg_resources.resource_filename('cmpd_accidents', 'resources/soap_descriptors/')
        with self.assertRaises(FileNotFoundError) as exception:
            string = loadFileAsString(path + 'invalid_descriptor.xml')