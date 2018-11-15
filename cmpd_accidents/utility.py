"""
Module for helper functions
"""
def loadFileAsString(filepath):
    try:
        with open(filepath, 'r') as myfile:
            data = myfile.read()
            return data
    except IOError as e:
        raise e
    except Exception as ex:
        raise ex