"""
Main module for traffic analysis, predictions, API
"""
import argparse
from traffic_analyzer import XGBModel
from traffic_analyzer import create_train_test_data
from traffic_analyzer import load_model, dump_model, load_csv

from sklearn.metrics import f1_score, average_precision_score, roc_auc_score, accuracy_score, recall_score
import pandas as pd


def train_model():
    """
    Main argparse for command line utils
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'host', help='Enter the db host to connect, full connection string for training data')
    parser.add_argument(
        'port', help='Enter the db port to connect, for training data', type=int)
    args = parser.parse_args()
    X_train, y_train, X_test, y_test, feature_names = create_train_test_data(
        datasize=10000, host=args.host, port=args.port, imbalance_multiplier=1, test_size=0.2)
    # Train model
    model = XGBModel()
    model.train_grid(X=X_train, y=y_train, X_numeric=(
        1, 2, 3, 4, 5, 12, 13, 14, 15, 16), X_categorical=(0, 6, 7, 8, 9, 10, 11, 17))
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
    mapper = {'f{0}'.format(i): v for i,
              v in enumerate(feature_names)}
    # Overall importance
    mapped = {mapper.get(
        k, None): v for k, v in model.model.best_estimator_.named_steps["clf"].get_booster().get_fscore().items()}
    dump_model(model, "xgb_cv_optimal.joblib")
    XGBModel.plot_model_importance(mapped)
    # Gain
    mapped_gain = {mapper.get(
        k, None): v for k, v in model.model.best_estimator_.named_steps["clf"].get_booster().get_score(importance_type='gain').items()}
    XGBModel.plot_model_importance(mapped_gain)


def test_model():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'model', help='Enter the model name from resources/models')
    parser.add_argument(
        'testset', help='Enter the test set csv file name')
    args = parser.parse_args()
    model = load_model(args.model)
    df = pd.read_csv(args.testset)
    pred_prob = model.model.predict_proba(df.values)
    print(pred_prob)


if __name__ == '__main__':
    train_model()
