"""
Module for helper functions
"""
from sklearn.externals import joblib
import pkg_resources

def load_model(filename):
    """
    Method to load ML pipeline model via pickle
    Args:
        file_path: the file path of the .pkl model
    """
    model_path = pkg_resources.resource_filename('traffic_analyzer', 'models/')
    with (open(model_path + filename, "rb")) as f:
        try:
            return joblib.load(f)
        except Exception as e:
            raise e