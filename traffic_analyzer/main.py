"""
Main module for traffic analysis, predictions, API
"""
import argparse
from traffic_analyzer import XGBModel
from traffic_analyzer import create_train_test_data
from traffic_analyzer import load_model, dump_model, load_csv

from sklearn.metrics import f1_score, average_precision_score, roc_auc_score, accuracy_score, recall_score
import pandas as pd


def validate_model(model, X_test, y_test, feature_names):
    """
    Test model with validation set
    Args:
        model: model to test
        X_test: features of validation data
        y_test: labels of validation data
    """
    preds = model.predict(X_test)
    predictions = [pred[1] for pred in preds]
    _score_f1 = f1_score(y_test, predictions)
    _score_average_prec = average_precision_score(
        y_test, predictions)
    _score_auc_ = roc_auc_score(y_test, predictions)
    _score_accuracy = accuracy_score(y_test, predictions)
    _score_recall = recall_score(y_test, predictions)
    print("Best params: {0}".format(model.model.best_params_))
    print("Scores: F1: {0}, Precision: {1}, AUC: {2}, Accuracy: {3}, Recall: {4}".format(
        _score_f1, _score_average_prec, _score_auc_, _score_accuracy, _score_recall))
    XGBModel.plot_model_features(model, feature_names)


def existing_model_test(model_name, testset):
    """
    Load existing model to test probabilities
    Args:
        model: the model name from integrated resources/models
        testset: the csv file location of test set data
    """
    model = load_model(
        model_name)  # load from package resources existing models
    df = pd.read_csv(testset)
    pred_prob = model.model.predict_proba(df.values)
    print(pred_prob)


def train_model(size, host, port):
    """
    Main argparse for training model
    Args:
        size: the total data size to train
        host: the host of the database with data
        port: the port of the database with data
    """
    X_train, y_train, X_test, y_test, feature_names = create_train_test_data(
        datasize=size, host=host, port=port, imbalance_multiplier=1, test_size=0.2)
    # Train model
    model = XGBModel()
    model.train_grid(X=X_train, y=y_train, X_numeric=(
        1, 2, 3, 4, 5, 12, 13, 14, 15, 16), X_categorical=(0, 6, 7, 8, 9, 10, 11, 17))
    return model.model  # Return gridsearch pipeline object


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'model_name', help='Enter the name of the model to be generated')
    parser.add_argument(
        'size', help='Enter the training datasize for the model', type=int)
    parser.add_argument(
        'host', help='Enter the db host to connect, full connection string for training data')
    parser.add_argument(
        'port', help='Enter the db port to connect, for training data', type=int)
    args = parser.parse_args()
    # Model train/dump
    model = train_model(args.size, args.host, args.port)
    dump_model(model, args.model_name)
