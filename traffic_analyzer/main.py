"""
Main module for traffic analysis, predictions, API
"""
import argparse
#from traffic_analyzer import load_model
from traffic_analyzer import XGModel
from traffic_analyzer import create_train_test_data

#from sklearn.datasets import load_iris
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import accuracy_score

# Predictions based on geographic points x, y?
# Aggregate counts for roads?
# Heatmap for geo coords?

def create_xg_model(trainset, labels):
    """
    Args:
        model_type: Type of model to train: xgb/rf
    Returns XGBoost trained model
    """
    model = XGModel()
    model.train_and_update(trainset, labels)
    return model

def main():
    """
    Main argparse for command line utils
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Enter existing or new model")
    exist_parser = subparsers.add_parser("existing")
    new_parser = subparsers.add_parser("new")
    exist_parser.add_argument(
        "model",
        help="Enter model to use for existing model"
    )
    new_parser.add_argument(
        "model_type",
        help="Enter the type of model to train for new model",
        choices=["xgb","rf"]
    )
    new_parser.add_argument(
        'host',
        help='Enter the db host to connect, full connection string for training data'
    )
    new_parser.add_argument(
        'port',
        help='Enter the db port to connect, for training data',
        type=int
    )
    args = parser.parse_args()
    print(args)
    if 'model_type' in args: # Train new model
        if args.model_type == 'xgb': # XGB
            data = create_train_test_data(host=args.host, port=args.port, holdout_size=0.2)
            print(data.columns)
            #trainset, testset = create_train_test_data(host='', port='', holdout_size=0.2)
            #labels = trainset[:, ]
            #model = create_xg_model(trainset, labels)
        else: # RandomForest
            print("RF")
    else: # Load existing model from pkg_resources
        return None


    # Predicting setup

    #parser.add_argument('predict',
    #    help='Enter the csv file of the observations/test data to predict'
    #)
    # preds = model.predict(load_csv('./predictions'))
    # predictions = [pred[1] for pred in preds]
    # accuracy = accuracy_score(y_test, predictions)
    # print(accuracy)

    # Iris testing

    # model = XGModel()
    # X, y = load_iris(return_X_y=True)
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=1234)
    # model.train_and_update(X_train, y_train)
    # preds = model.predict(X_test)
    # predictions = [pred[1] for pred in preds] # actual predicted class values
    # accuracy = accuracy_score(y_test, predictions)
    # print(predictions)
    # print(y_test)
    # print(accuracy)
    
if __name__ == '__main__':
    main()