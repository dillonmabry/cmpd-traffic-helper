"""
Module for helper functions
"""
import pandas as pd
import numpy as np
from joblib import dump, load
import pkg_resources


def load_model(filename):
    """
    Method to load ML pipeline model via pickle
    Args:
        filename: the file name of the .pkl model
    Returns model loaded
    """
    model_path = pkg_resources.resource_filename('traffic_analyzer', 'resources/models/')
    try:
        return load(model_path + filename)
    except FileNotFoundError:
        print("Model not found in model resources/models directory")
    except Exception as e:
        raise e


def dump_model(model, model_name):
    """
    Args:
        model_name: name to save model
    Dumps model for use
    """
    try:
        dump(model, model_name)
    except Exception as e:
        raise e


def load_csv(filename):
    """
    Method to load csv files
    Args:
        filename: the file name of the .csv
    Returns Pandas dataframe from csv
    """
    file_path = pkg_resources.resource_filename(
        'traffic_analyzer', 'resources/reference_data/')
    with (open(file_path + filename, "rb")) as f:
        try:
            return pd.read_csv(f)
        except Exception as e:
            raise e


def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    All args must be of equal length.    
    Resource: https://stackoverflow.com/questions/29545704/fast-haversine-approximation-python-pandas/29546836#29546836
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    m = 6367000 * c  # meters
    return m
