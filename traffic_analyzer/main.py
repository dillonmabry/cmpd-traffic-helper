"""
Main module for traffic analysis, predictions, API
"""
import argparse
from traffic_analyzer import XGModel
from traffic_analyzer import create_train_test_data

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
    if 'model_type' in args:
        if args.model_type == 'xgb':
            #trainset, trainlabels, testset, testlabels = create_train_test_data(host=args.host, port=args.port, holdout_size=0.2)
            test = create_train_test_data(host=args.host, port=args.port, holdout_size=0.2)
        else:
            print("RF")
    else: # Load existing model from pkg_resources
        return None

if __name__ == '__main__':
    main()