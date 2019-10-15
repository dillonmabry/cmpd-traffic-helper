""" Util module to gather training data, create sampling sets, and preprocess data
"""
# Modules
from cmpd_accidents import MongoDBConnect
from traffic_analyzer import load_csv
from traffic_analyzer import haversine_np
from traffic_analyzer import feature_map as features
# Essentials
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import re
# Spatial features
from shapely.geometry import Point, LineString, Polygon
# Sklearn
from sklearn.model_selection import train_test_split
# Base libs
import random
import itertools
import datetime as datetime

from traffic_analyzer import Logger
_logger = Logger(__name__).get()


def load_reference_data():
    """ Load reference data for other features
    Returns:
        Tuple of multiple reference datasets
    """
    population = load_csv("census_population.csv")
    roads = load_csv("roads.csv")
    signals = load_csv("signals.csv")
    traffic_vol = load_csv("traffic_volumes.csv")
    return population, roads, signals, traffic_vol


def clean_data(data):
    """
    Args:
        data: dataframe to clean based on known data issues
    Returns cleaned dataframe based on set features updated
    Features cleaned:
        - Address, known issue with reporting via CMPD as "&" for error address
    """
    cleansed_data = data.fillna(data.mean())
    _logger.info('Cleaned data... Filled NAs with mean values')
    return cleansed_data


def find_first_word(address):
    """
    Find first matched street word identifying possible roads/addresses
    Args:
        address: address to perform matching against known state roads
    Returns first word of the case of matched words in an address
    """
    major_highways = ["85", "77", "485"]
    hw_matches = re.findall(r"[0-9]+", address)
    matches = re.findall(r"[A-Za-z]+", address)
    words = [word for word in matches if len(word) > 3]
    hw_words = [word for word in hw_matches if word in major_highways]
    hw_word = hw_words[0] if hw_words else None
    first_word = words[0] if words else None
    if hw_word:
        return hw_word
    else:
        return first_word


def extract_speed(address):
    """
    Generate generic speed limits for known roads
    Args:
        address: the address/road to analyze
    """
    if "HY" in address or "FR" in address:  # Highways/freeways
        return 70
    elif "RD" in address:  # Generic roads
        return 45
    elif "RP" in address:  # Ramps
        return 35
    elif re.search("([0-9]+)(ST|ND|RD|TH)", str(address)):  # Ordinal streets
        return 35
    else:
        return 45  # Generic speed limit


def extract_pop_info(polygons, row):
    """ Extract population information for single instance
    Based on polygons coordinates from reference data
    Args:
        polygons: Shapely polygons to inspect (list)
        row: the dataset training row
    Returns:
        tuple: median_age, median_pop for instance
    """
    for poly_obj in polygons:
        median_age = None
        median_pop = None
        if poly_obj["poly"].contains(Point(row[features.get('lat')], row[features.get('long')])):
            median_age = poly_obj["median_age"]
            median_pop = poly_obj["pop_sq_mile"]
            break
    return median_age, median_pop


def extract_signals(signals, row):
    """ Extract signal proximity using haversine distance
    Args:
        signals: list of valid signal X,Y coords
        row: the dataset training row
    Returns:
        number of signals nearby
    """
    dists = haversine_np(
        signals["Y"], signals["X"], row[features.get('lat')], row[features.get('long')])
    signals_near = len(dists[dists < 500])
    return signals_near


def extract_road_info(volumes, roads, row):
    """ Extract road info (volumes, curves, lengths, names)
    Args:
        volumes: grouped objects based on reference data
        roads: roads info created from reference data
        row: the dataset training row
    Returns:
        road volumes, curves, lengths, names
    """
    first_word = find_first_word(row[features.get('address')])
    # Road information
    if first_word:
        vols = volumes[volumes["ROUTE"].str.contains(
            first_word, na=False)]["2016"]
        curves = roads[roads["STREETNAME"].str.contains(
            first_word, na=False)]["curve"]
        lengths = roads[roads["STREETNAME"].str.contains(
            first_word, na=False)]["ShapeSTLength"]
        roads_matched = roads[roads["STREETNAME"].str.contains(
            first_word, na=False)]["STREETNAME"]
        freq_roads = roads_matched.mode()

        road_name = (freq_roads.iloc[0]
                     if freq_roads.any() else "GENERIC_STREET")
        return vols.mean(), curves.mean(), lengths.mean(), road_name
    else:
        return None, None, None, "GENERIC_STREET"


def create_polygons(population):
    """ Create section polygons from census information
    Args:
        population: dataframe from census reference data
    Returns:
        Shapely list of polygons to be used for extraction
    """
    polygons = []
    for _, row in population.iterrows():
        xs = [float(x) for x in row["coordinates"].split(',')[1::2]]
        ys = [float(y) for y in row["coordinates"].split(',')[0::2]]
        coords = zip(xs, ys)
        polygon = Polygon(list(coords))
        polygons.append(
            {'poly': polygon, 'pop_sq_mile': row["PopSqMi"], 'median_age': row["MedianAge"]})
    return polygons


def create_roads(roads):
    """ Create roads information from roads reference data
    Args:
        roads: dataframe from roads reference data
    Returns:
        list of road curves for all roads
    """
    road_curves = []
    for _, row in roads.iterrows():
        splitcoords = row["coordinates"].split(",")
        longlats = list(zip(*[iter(splitcoords)]*2))
        latlongs = [tuple(reversed(item))
                    for item in longlats]  # correct to lat/long, reversed
        # LineString (Spatial Lines based on road coords)
        shape_points = []
        for point in latlongs:
            shape_point = Point(float(point[0]), float(point[1]))
            shape_points.append(shape_point)
        line = LineString(shape_points)
        # Road curvature/lengths based on line points
        dist = haversine_np(
            line.coords.xy[0][0],  # First X
            line.coords.xy[1][0],  # First Y
            line.coords.xy[0][len(line.coords.xy[0])-1],  # End X
            line.coords.xy[1][len(line.coords.xy[0])-1]  # End Y
        )
        curve = (line.length / dist) if dist != 0 else 0
        road_curves.append(curve)
    return road_curves


def join_features(data):
    """
    Args:
        data: dataframe to join based on
    Returns modified existing dataframe to join new features
    Features added:
        - Time series info
        - Traffic info (signals, traffic volumes, population)
        - Road info (curvature, length, KMeans grouping)
        - Any other census information
    """
    # Load reference data
    population, roads, signals, traffic_vol = load_reference_data()

    # Time information
    data[features.get('month')] = data[features.get('datetime')].dt.month
    data[features.get('day')] = data[features.get('datetime')].dt.day
    data[features.get('hour')] = data[features.get('datetime')].dt.hour
    data[features.get('minute')] = data[features.get('datetime')].dt.minute
    data[features.get('day_of_week')] = data[features.get(
        'datetime')].dt.dayofweek

    # Load road information
    roads["curve"] = create_roads(roads)

    # Load polygons from census information
    polygons = create_polygons(population)

    # Traffic info
    meck_vols = traffic_vol[(traffic_vol["COUNTY"] == "MECKLENBURG") & (
        traffic_vol["2016"] != ' ')][["ROUTE", "2016"]]
    meck_vols["2016"] = meck_vols["2016"].astype(int)
    grouped = meck_vols.groupby(["ROUTE"], as_index=False).mean()

    # Main data join with other features
    mean_vols, mean_curves, mean_lengths, signals_near, road_names, ages, pops = (
        [], [], [], [], [], [], [])

    for _, row in data.iterrows():

        # Road information (volumes, curves, lengths)
        vol, curve, length, name = extract_road_info(grouped, roads, row)
        mean_vols.append(vol)
        mean_curves.append(curve)
        mean_lengths.append(length)
        road_names.append(name)

        # Signals proximity
        signals_near.append(extract_signals(signals, row))

        # Population
        ages.append(extract_pop_info(polygons, row)[0])

        # Age
        pops.append(extract_pop_info(polygons, row)[1])

    data[features.get('road')] = road_names
    data[features.get('road_curve')] = mean_curves
    data[features.get('road_length')] = mean_lengths
    data[features.get('road_volume')] = mean_vols
    data[features.get('signals_near')] = signals_near
    data[features.get('road_speed')] = data[features.get(
        'address')].apply(lambda x: extract_speed(x))
    data[features.get('median_age')] = ages
    data[features.get('pop_sq_mile')] = pops

    # Clean data before further preprocessing
    cleansed_data = clean_data(data)

    # Weather
    cleansed_data[features.get('weatherCategory')] = cleansed_data[features.get(
        'weather')].values.tolist()[0][0]['main']
    cleansed_data[features.get('sunrise_hour')] = pd.DatetimeIndex(
        cleansed_data[features.get('sunrise')]).hour
    cleansed_data[features.get('sunrise_minute')] = pd.DatetimeIndex(
        cleansed_data[features.get('sunrise')]).minute
    cleansed_data[features.get('sunset_hour')] = pd.DatetimeIndex(
        cleansed_data[features.get('sunset')]).hour
    cleansed_data[features.get('sunset_minute')] = pd.DatetimeIndex(
        cleansed_data[features.get('sunset')]).minute

    _logger.info(
        'Added features... joined data features including spatial data')
    return cleansed_data


def generate_non_accidents(data, iterations):
    """
    Args:
        data: dataframe of existing accidents to utilize for generation
        iterations: iterations to perform for generating training data, ie, (1, 2, ...)
    Returns dataset of non-accidents
    Method of generation:
    For each positive sample (accident) change value of one feature from the following features:
    ( hour, day, road )
    If the result is negative, we add to negative pool of samples
    Dataset should contain at least 3-4 times negative samples to positive for proper oversampling
    """
    choices = [features.get('hour'), features.get('day'), features.get('road')]
    hours = data[features.get('hour')].unique()
    days = data[features.get('day')].unique()
    roads = data[features.get('road')].unique()
    feature_choice = random.choice(choices)
    cols = data.columns.tolist()
    non_accidents = pd.DataFrame(columns=cols)
    for _ in itertools.repeat(None, iterations):
        non_accs = pd.DataFrame(columns=cols)
        for i, row in data.iterrows():
            acc_rec = row
            if feature_choice == features.get('hour'):
                random_choice = np.asscalar(np.random.choice(hours, 1))
                acc_rec[feature_choice] = random_choice
            elif feature_choice == features.get('day'):
                random_choice = np.asscalar(np.random.choice(days, 1))
                acc_rec[feature_choice] = random_choice
            else:
                random_choice = np.asscalar(np.random.choice(roads, 1))
                acc_rec[feature_choice] = random_choice
            if ((data[features.get('day')] == acc_rec[features.get('day')]) &
                (data[features.get('hour')] == acc_rec[features.get('hour')]) &
                    (data[features.get('road')] == acc_rec[features.get('road')])).any():
                continue
            else:
                non_accs.loc[i] = acc_rec
        non_accidents = non_accidents.append(non_accs, ignore_index=True)

    _logger.info(
        "Generated {0} non-accidents to go with {1} accidents".format(len(non_accidents), len(data)))
    return non_accidents


def get_accidents(datasize, host, port):
    """
    Args:
        datasize: number of positively identified items to generate
        host: the host for the dataset (accidents)
        port: the port for the host
    Returns accidents dataset
    """
    # Get the accidents data
    database = MongoDBConnect(host, port)
    with database as db:
        cursor = db.get_all(collection='accidents',
                            limit=datasize, order=1)  # asc
        db_accidents = json_normalize(list(cursor))  # flatten weather json
    _logger.info('Retrieved accident data from data source')

    # Set correct data types as necessary
    db_accidents[features.get('lat')] = pd.to_numeric(
        db_accidents[features.get('lat')])
    db_accidents[features.get('long')] = pd.to_numeric(
        db_accidents[features.get('long')])
    db_accidents[features.get('datetime')] = pd.to_datetime(
        db_accidents[features.get('datetime')])
    db_accidents[features.get('sunrise')] = pd.to_datetime(
        db_accidents[features.get('weatherSunrise')], unit='s')
    db_accidents[features.get('sunset')] = pd.to_datetime(
        db_accidents[features.get('weatherSunset')], unit='s')

    # Append any joined information (new.street_name, new.speed_limit, pop_sq_mile, median_age)
    accidents = join_features(db_accidents)
    return accidents


def create_train_test_data(datasize, host, port, imbalance_multiplier, test_size):
    """
    Args:
        datasize: number of positively identified items to generate
        host: the host for the dataset (accidents)
        port: the port for the host
        imbalance_multiplier: Multiplier of the non-accident size
        test_size: test data size proportion
    Returns X_train, y_train, X_test, y_test, and feature names
    """
    # Get actual accidents
    accidents = get_accidents(datasize, host, port)

    # Create the oversampling of non-accidents
    non_accidents = generate_non_accidents(
        data=accidents,
        iterations=imbalance_multiplier
    )
    # Identify accidents vs. non-accidents
    accidents[features.get('is_accident')] = 1
    non_accidents[features.get('is_accident')] = 0

    # Join final training dataset (accidents with non-accidents) with key features
    trainset = pd.concat([accidents, non_accidents])
    feature_cols = [features.get('division'),
                    features.get('weatherTemp'),
                    features.get('weatherRain3'),
                    features.get('weatherVisibility'),
                    features.get('weatherWindSpeed'),
                    features.get('sunrise_hour'),
                    features.get('month'),
                    features.get('hour'),
                    features.get('day_of_week'),
                    features.get('day'),
                    features.get('road_curve'),
                    features.get('road_length'),
                    features.get('road_volume'),
                    features.get('signals_near'),
                    features.get('road_speed'),
                    features.get('pop_sq_mile'),
                    features.get('median_age'),
                    features.get('is_accident')]
    try:
        trainset = trainset[feature_cols]
    except KeyError:
        _logger.error(
            'Feature key not found in dataset, adding missing features...')
        trainset = trainset.reindex(columns=feature_cols)
        pass

    # Return train set and final holdout set based on defined percent
    X = trainset.iloc[:, :-1].values
    y = trainset[features.get('is_accident')].values
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=1234)

    return X_train, y_train, X_test, y_test, trainset.columns.values[:-1]
