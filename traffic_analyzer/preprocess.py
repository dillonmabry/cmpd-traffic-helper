"""
Util module to gather training data, create sampling sets, and preprocess data
"""
from cmpd_accidents import MongoDBConnect
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np

def get_join_information(data):
    """
    Args:
        data: data to join based on
    Joins and returns based on census information as well as city-based features to dataset
    """


def generate_non_accidents(start_date, end_date, iterations):
    """
    Args:
        start_date: starting date to setup temporal training data
        end_date: end date for temporal data, these dates will be constrained as dates to be used
        iterations: iterations to perform for generating training data, ie, (1, 2, ...)
    Returns dataset of non-accidents
    """
    return None

def create_train_test_data(host, port, holdout_size=0.2):
    """
    Args:
        host: the host for the connection string of data
        port: the port for the host
        holdout_size: Size in proportion to training data for validation set
    Returns train set and test sets with corresponding labels
    """
    # Get the accidents data
    database = MongoDBConnect(host, port)
    with database as db:
        cursor = db.get_all(collection='accidents', limit=3000)
        df = json_normalize(list(cursor)) # flatten weather json
    return df
    # Append any joined information (new.street_name, new.speed_limit, new.mean_curve, new.mean_length, new.signals_near, new.mean_vol, new.month, new.day, new.day_of_week, new.hour, new.minute, pop_sq_mile, median_age)

    # Create the oversampling of non-accidents

    # Join final training dataset (accidents with non-accidents)

    # Return train set and final holdout set based on defined percent
    