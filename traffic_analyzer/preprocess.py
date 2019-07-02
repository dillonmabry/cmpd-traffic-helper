"""
Util module to gather training data, create sampling sets, and preprocess data
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
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
# Base libs
import random
import itertools
import datetime as datetime

from traffic_analyzer import Logger
_logger = Logger(__name__).get()


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
    # Load static features
    income = load_csv("census_income.csv")
    population = load_csv("census_population.csv")
    roads = load_csv("roads.csv")
    signals = load_csv("signals.csv")
    traffic_vol = load_csv("traffic_volumes.csv")

    # Time Series info
    data[features.get('month')] = data[features.get('datetime')].dt.month
    data[features.get('day')] = data[features.get('datetime')].dt.day
    data[features.get('hour')] = data[features.get('datetime')].dt.hour
    data[features.get('minute')] = data[features.get('datetime')].dt.minute
    data[features.get('day_of_week')] = data[features.get(
        'datetime')].dt.dayofweek

    # Road curvature
    road_curves = []
    for i, row in roads.iterrows():
        splitcoords = row["coordinates"].split(",")
        longlats = list(zip(*[iter(splitcoords)]*2))
        latlongs = [tuple(reversed(item))
                    for item in longlats]  # correct to lat/long
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
    roads["curve"] = road_curves

    polygons = []
    # Load polygons from census information
    for i, row in income.iterrows():
        xs = [float(x) for x in row["coordinates"].split(',')[1::2]]
        ys = [float(y) for y in row["coordinates"].split(',')[0::2]]
        coords = zip(xs, ys)
        polygon = Polygon(list(coords))
        polygons.append(polygon)

    # Traffic info
    meck_vols = traffic_vol[(traffic_vol["COUNTY"] == "MECKLENBURG") & (
        traffic_vol["2016"] != ' ')][["ROUTE", "2016"]]
    meck_vols["2016"] = meck_vols["2016"].astype(int)
    grouped = meck_vols.groupby(["ROUTE"], as_index=False).mean()
    mean_vols = []
    mean_curves = []
    mean_lengths = []
    signals_near = []
    road_names = []
    # Process data
    for i, row in data.iterrows():
        first_word = find_first_word(row[features.get('address')])
        # Road information
        if first_word:
            vols = grouped[grouped["ROUTE"].str.contains(
                first_word, na=False)]["2016"]
            curves = roads[roads["STREETNAME"].str.contains(
                first_word, na=False)]["curve"]
            lengths = roads[roads["STREETNAME"].str.contains(
                first_word, na=False)]["ShapeSTLength"]
            roads_matched = roads[roads["STREETNAME"].str.contains(
                first_word, na=False)]["STREETNAME"]
            freq_roads = roads_matched.mode()
            road_names.append(
                freq_roads.iloc[0] if freq_roads.any() else "GENERIC_STREET")
            mean_vols.append(vols.mean())
            mean_curves.append(curves.mean())
            mean_lengths.append(lengths.mean())
        else:
            road_names.append("GENERIC_STREET")
            mean_vols.append(0)
            mean_curves.append(0)
            mean_lengths.append(0)
        # Signals proximity
        dists = haversine_np(
            signals["Y"], signals["X"], row[features.get('lat')], row[features.get('long')])
        near = len(dists[dists < 500])
        signals_near.append(near)

    data[features.get('road')] = road_names
    data[features.get('road_curve')] = mean_curves
    data[features.get('road_length')] = mean_lengths
    data[features.get('road_volume')] = mean_vols
    data[features.get('signals_near')] = signals_near
    data[features.get('road_speed')] = data[features.get(
        'address')].apply(lambda x: extract_speed(x))

    # Clean data before further preprocessing
    cleansed_data = clean_data(data)

    # KMeans road features, standardize road curvatures/lengths features before processing
    matrix = cleansed_data[[features.get('road_length'),
                            features.get('road_curve'), features.get('road_speed')]].values
    scaler = MinMaxScaler()
    scaled_matrix = scaler.fit_transform(matrix)
    kroad = KMeans(n_clusters=5, random_state=1234).fit(
        scaled_matrix)  # Optimal k = 5 based on SSE metrics
    labels = kroad.labels_
    cleansed_data[features.get('road_cluster')] = labels

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
        'Adding features... joined data features including spatial data')
    # Return finalized
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
    _logger.info('Getting data... Retrieved accident data from data source')

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
    Returns train, test, and feature names
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
                    features.get('weatherSnow1'),
                    features.get('weatherVisibility'),
                    features.get('weatherWindSpeed'),
                    features.get('sunrise_hour'),
                    features.get('sunset_hour'),
                    features.get('weatherCategory'),
                    features.get('month'),
                    features.get('hour'),
                    features.get('day_of_week'),
                    features.get('road_curve'),
                    features.get('road_length'),
                    features.get('road_volume'),
                    features.get('signals_near'),
                    features.get('road_speed'),
                    features.get('road_cluster'),
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
