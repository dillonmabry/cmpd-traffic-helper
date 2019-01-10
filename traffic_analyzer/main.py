"""
Main module for traffic analysis, predictions, API
"""
import argparse
from traffic_analyzer import XGModel
from traffic_analyzer import create_train_test_data

from sklearn.metrics import accuracy_score

def create_xg_model(trainset, labels, numeric, categorical):
    """
    Args:
        model_type: Type of model to train: xgb/rf
    Returns XGBoost trained model
    """
    model = XGModel()
    model.train_grid(trainset, labels, numeric, categorical)
    return model

def main():
    """
    Main argparse for command line utils
    """
    parser = argparse.ArgumentParser()
    # Subparse
    subparsers = parser.add_subparsers(help="Enter existing or new model")
    exist_parser = subparsers.add_parser("existing")
    new_parser = subparsers.add_parser("new")
    # Args
    exist_parser.add_argument("model", help="Enter model to use for existing model")
    new_parser.add_argument("model_type", help="Enter the type of model to train for new model", choices=["xgb","rf"])
    new_parser.add_argument('host', help='Enter the db host to connect, full connection string for training data')
    new_parser.add_argument('port', help='Enter the db port to connect, for training data', type=int)
    args = parser.parse_args()
    if 'model_type' in args: # New model
        if args.model_type == 'xgb':
            X_train, y_train, X_test, y_test = create_train_test_data(host=args.host, port=args.port, holdout_size=0.2)
            model = create_xg_model(
                trainset = X_train, 
                labels = y_train, 
                numeric = (10, 16, 17, 18, 20, 24, 26, 30, 31, 33, 37, 46, 47, 48), # assign numeric columns
                categorical = (3, 40, 41, 42, 44, 45, 49, 50) # assign categorical columns
            )
            preds = model.predict(X_test)
            predictions = [pred[1] for pred in preds]
            accuracy = accuracy_score(y_test, predictions)
            print(accuracy)
        else:
            print("RF")
    else: # Existing model
        return None

    # Predicting setup
    #parser.add_argument('predict',
    #    help='Enter the csv file of the observations/test data to predict'
    #)
    # preds = model.predict(load_csv('./predictions'))
    # predictions = [pred[1] for pred in preds]
    # accuracy = accuracy_score(y_test, predictions)
    # print(accuracy)

if __name__ == '__main__':
    main()