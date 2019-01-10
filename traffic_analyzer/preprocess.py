"""
Util module to gather training data, create sampling sets, and preprocess data
"""
from cmpd_accidents import MongoDBConnect # Connect to database for train data
from traffic_analyzer import load_csv # Load pkg_resources, extra featuresets
from traffic_analyzer import haversine_np # Coordinates distances
import pandas as pd # Dataframes
from pandas.io.json import json_normalize # Flatten Mongo JSON for dataframe
import re # Text filtering
import numpy as np # Continuous features
from shapely.geometry import Point, LineString # Spatial features
from sklearn.model_selection import train_test_split # Train/test split
from sklearn.preprocessing import MinMaxScaler # Feature scaling for K-Means
from sklearn.cluster import KMeans # Feature generation
import random # Base libs
import itertools # Base libs
import datetime as datetime # Base libs

def clean_data(data):
    """
    Args:
        data: dataframe to clean based on known data issues
    Returns cleaned dataframe based on set features updated
    Features cleaned:
        - Address, known issue with reporting via CMPD as "&" for error address
    """
    cleansed_data = data.fillna(data.mean())
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
        road_type: the road to analyze
    """
    if "HY" in address or "FR" in address: # Highways/freeways
        return 70
    elif "RD" in address: # Generic roads
        return 45
    elif "RP" in address: # Ramps
        return 35
    elif re.search("([0-9]+)(ST|ND|RD|TH)", str(address)): # Ordinal streets
        return 35
    else:
        return 45 # Generic speed limit

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
    pop = load_csv("census_population.csv")
    roads = load_csv("roads.csv")
    signals = load_csv("signals.csv")
    traffic_vol = load_csv("traffic_volumes.csv")

    # Time Series info
    data["new.month"] = data["datetime_add"].dt.month
    data["new.day"] = data["datetime_add"].dt.day
    data["new.hour"] = data["datetime_add"].dt.hour
    data["new.minute"] = data["datetime_add"].dt.minute
    data["new.day_of_week"] = data["datetime_add"].dt.dayofweek

    # Road curvature
    road_curves = []
    for i, row in roads.iterrows():
        splitcoords = row["coordinates"].split(",")
        longlats = list(zip(*[iter(splitcoords)]*2))
        latlongs = [tuple(reversed(item)) for item in longlats] # correct to lat/long
        # LineString (Spatial Lines based on road coords)
        shape_points = []
        for point in latlongs:
            shape_point = Point(float(point[0]), float(point[1]))
            shape_points.append(shape_point)
        line = LineString(shape_points)
        # Road curvature/lengths
        dist = haversine_np(
            line.coords.xy[0][0], 
            line.coords.xy[1][0], 
            line.coords.xy[0][len(line.coords.xy[0])-1],
            line.coords.xy[1][len(line.coords.xy[0])-1]
        )
        curve = (line.length / dist) if dist != 0 else 0
        road_curves.append(curve)
    roads["curve"] = road_curves

    # Traffic info
    meck_vols = traffic_vol[(traffic_vol["COUNTY"] == "MECKLENBURG") & (traffic_vol["2016"] != ' ')][["ROUTE", "2016"]]
    meck_vols["2016"] = meck_vols["2016"].astype(int)
    grouped = meck_vols.groupby(["ROUTE"], as_index=False).mean()
    mean_vols = []
    mean_curves = []
    mean_lengths = []
    signals_near = []
    road_names = []
    for i, row in data.iterrows():
        first_word = find_first_word(row["address"])
        # Road information
        if first_word:
            vols = grouped[grouped["ROUTE"].str.contains(first_word, na=False)]["2016"]
            curves = roads[roads["STREETNAME"].str.contains(first_word, na=False)]["curve"]
            lengths = roads[roads["STREETNAME"].str.contains(first_word, na=False)]["ShapeSTLength"]
            roads_matched = roads[roads["STREETNAME"].str.contains(first_word, na=False)]["STREETNAME"]
            freq_roads = roads_matched.mode()
            road_names.append(freq_roads.iloc[0] if freq_roads.any() else "GENERIC_STREET")
            mean_vols.append(vols.mean())
            mean_curves.append(curves.mean())
            mean_lengths.append(lengths.mean())
        else:
            road_names.append("GENERIC_STREET")
            mean_vols.append(0)
            mean_curves.append(0)
            mean_lengths.append(0)
        # Signals
        dists = haversine_np(signals["Y"], signals["X"], row["latitude"], row["longitude"])
        near = len(dists[dists < 500])
        signals_near.append(near)

    data["new.road_name"] = road_names
    data["new.mean_curve"] = mean_curves
    data["new.mean_length"] = mean_lengths
    data["new.mean_vol"] = mean_vols
    data["new.signals_near"] = signals_near
    data["new.speed_limit"] = data["address"].apply(lambda x: extract_speed(x))

    # TODO: Add census information to be joined spatially via accident coordinates
    # Census info
    census_info = pd.merge(income, pop, how="left", on=["coordinates"])

    # Clean data before further preprocessing
    cleansed_data = clean_data(data)

    # KMeans road features, standardize road curvatures/lengths features before processing
    matrix = cleansed_data[["new.mean_length", "new.mean_curve", "new.speed_limit"]].values
    scaler = MinMaxScaler()
    scaled_matrix = scaler.fit_transform(matrix)
    kroad = KMeans(n_clusters=5, random_state=1234).fit(scaled_matrix) # Optimal k = 5 based on SSE metrics
    labels = kroad.labels_
    cleansed_data["new.road_cluster"] = labels

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
    choices = ["new.hour", "new.day", "new.road_name"]
    hours = data["new.hour"].unique()
    days = data["new.day"].unique()
    roads = data["new.road_name"].unique()
    feature_choice = random.choice(choices)
    cols = data.columns.tolist()
    non_accidents = pd.DataFrame(columns=cols)
    data_matrix = data.as_matrix().tolist()
    for _ in itertools.repeat(None, iterations):
        non_accs = pd.DataFrame(columns=cols)
        for i, row in data.iterrows():
            acc_rec = row
            if feature_choice == "new.hour":
                random_choice = np.asscalar(np.random.choice(hours, 1))
                acc_rec[feature_choice] = random_choice
            elif feature_choice == "new.day":
                random_choice = np.asscalar(np.random.choice(days, 1))
                acc_rec[feature_choice] = random_choice
            else:
                random_choice = np.asscalar(np.random.choice(roads, 1))
                acc_rec[feature_choice] = random_choice
            if acc_rec.tolist() in data_matrix:
                continue
            else:
                non_accs.loc[i] = acc_rec
        non_accidents = non_accidents.append(non_accs, ignore_index=True)

    print("Generated {0} non-accidents to go with {1} accidents".format(len(non_accidents), len(data)))
    return non_accidents

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
        db_accidents = json_normalize(list(cursor)) # flatten weather json

    # Set correct data types as necessary
    db_accidents["latitude"] = pd.to_numeric(db_accidents["latitude"])
    db_accidents["longitude"] = pd.to_numeric(db_accidents["longitude"])
    db_accidents["datetime_add"] = pd.to_datetime(db_accidents["datetime_add"])

    # Append any joined information (new.street_name, new.speed_limit, pop_sq_mile, median_age)
    accidents = join_features(db_accidents)

    # Create the oversampling of non-accidents
    non_accidents = generate_non_accidents(
       data = accidents,
       iterations = 3
    )
    accidents["is_accident"] = 1
    non_accidents["is_accident"] = 0

    # Join final training dataset (accidents with non-accidents)
    trainset = pd.concat([accidents, non_accidents])

    # Return train set and final holdout set based on defined percent
    X = trainset.iloc[:, :-1].values
    y = trainset["is_accident"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=1234)
    return X_train, y_train, X_test, y_test