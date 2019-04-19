"""
Module for helper functions
"""


def loadFileAsString(filepath):
    try:
        with open(filepath, 'r') as myfile:
            data = myfile.read()
            return data
    except FileNotFoundError as e:
        raise e
