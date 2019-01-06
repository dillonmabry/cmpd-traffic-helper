"""
Module for helper functions
"""
import pandas as pd
import numpy as np
from sklearn.externals import joblib
import pkg_resources

def load_model(filename):
    """
    Method to load ML pipeline model via pickle
    Args:
        filename: the file name of the .pkl model
    Returns model loaded
    """
    model_path = pkg_resources.resource_filename('traffic_analyzer', 'models/')
    with (open(model_path + filename, "rb")) as f:
        try:
            return joblib.load(f)
        except Exception as e:
            raise e

def load_csv(filename):
    """
    Method to load csv files
    Args:
        filename: the file name of the .csv
    Returns Pandas dataframe from csv
    """
    file_path = pkg_resources.resource_filename('traffic_analyzer', 'resources/')
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
    m = 6367000 * c # meters
    return m