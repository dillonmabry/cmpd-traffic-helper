"""
Main module for traffic analysis, predictions, API
"""
import argparse
from traffic_analyzer import XGBModel
from traffic_analyzer import create_train_test_data
from traffic_analyzer import dump_model
from traffic_analyzer import load_model, load_csv

from sklearn.metrics import f1_score, average_precision_score, roc_auc_score, accuracy_score
import time


def create_xg_model(trainset, labels, numeric, categorical, feature_names):
    """
    Args:
        model_type: Type of model to train: xgb/rf
    Returns XGBoost trained model
    """
    model = XGBModel(feature_names)
    model.train_grid(trainset, labels, numeric, categorical)
    return model


def main():
    """
    Main argparse for command line utils
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Enter existing or new model')
    exist_parser = subparsers.add_parser('existing')
    new_parser = subparsers.add_parser('new')
    exist_parser.add_argument(
        "model", help='Enter model to use for existing model')
    new_parser.add_argument(
        "model_type", help='Enter the type of model to train for new model', choices=['xgb', 'rf'])
    new_parser.add_argument(
        'host', help='Enter the db host to connect, full connection string for training data')
    new_parser.add_argument(
        'port', help='Enter the db port to connect, for training data', type=int)
    args = parser.parse_args()
    if 'model_type' in args:  # Select model type
        if args.model_type == 'xgb':
            models = []
            start = time.time()
            # Re-run for iterations to train best CV model
            for i in range(0, 3):
                X_train, y_train, X_test, y_test, feature_names = create_train_test_data(
                    datasize=5000, host=args.host, port=args.port, imbalance_multiplier=3, test_size=0.1)
                model = create_xg_model(
                    trainset=X_train,
                    labels=y_train,
                    # pipeline numeric indexes
                    numeric=(1, 2, 3, 4, 5, 17, 18, 19, 20),
                    # pipeline categorical indexes
                    categorical=(0, 6, 7, 8, 9, 10, 11, 12,
                                 13, 14, 15, 16, 21, 22),
                    feature_names=feature_names
                )
                preds = model.predict(X_test)
                predictions = [pred[1] for pred in preds]
                _score_f1 = f1_score(y_test, predictions)
                _score_average_prec = average_precision_score(y_test, predictions)
                _score_auc_ = roc_auc_score(y_test, predictions)
                _score_accuracy = accuracy_score(y_test, predictions)
                print('Iter: {0}, F1 Score: {1}'.format(i, _score_f1))
                models.append({'model': model, 
                               'f1_score': _score_f1,
                               'average_score': _score_average_prec, 
                               'auc_score': _score_auc_,
                               'accuracy_score': _score_accuracy})
 
            best_model = max(models, key=lambda model: model['f1_score'])
            model_name = "xgb_cv_optimal.joblib"
            dump_model(best_model['model'], model_name)
            bst = best_model['model']
            print('Best estimator params: {0}'.format(bst.model.best_params_))
            mapper = {'f{0}'.format(i): v for i,
                      v in enumerate(bst.feature_names)}
            mapped = {mapper.get(
                k, None): v for k, v in bst.model.best_estimator_.named_steps["clf"].get_booster().get_fscore().items()}
            print('Best model f1 score: {0}'.format(best_model['f1_score']))
            print('Best model avg precision score: {0}'.format(best_model['average_score']))
            print('Best model auc score: {0}'.format(best_model['auc_score']))
            print('Best model accuracy score: {0}'.format(best_model['accuracy_score']))
            end = time.time()
            print('End processing time: {0}'.format(end - start))
            XGBModel.plot_model_importance(mapped)
        else:
            print('RF')
    else:  # Existing model
        model = load_model(args.model)
        print('Model information: {0}'.format(model.model.best_estimator_.named_steps["clf"]))
        XGBModel.plot_model_importance(model.model.best_estimator_.named_steps["clf"])


if __name__ == '__main__':
    main()
