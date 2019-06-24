"""
Main module for traffic analysis, predictions, API
"""
import argparse
from traffic_analyzer import XGBModel
from traffic_analyzer import create_train_test_data
from traffic_analyzer import dump_model
from traffic_analyzer import load_model, load_csv

from sklearn.metrics import f1_score, average_precision_score, roc_auc_score, accuracy_score, recall_score
import time
from datetime import datetime
from numpy import array as nparray
import pandas as pd


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
            for i in range(0, 1):
                X_train, y_train, X_test, y_test, feature_names = create_train_test_data(
                    datasize=10000, host=args.host, port=args.port, imbalance_multiplier=1, test_size=0.2)
                model = create_xg_model(
                    trainset=X_train,
                    labels=y_train,
                    # pipeline numeric indexes
                    numeric=(1, 2, 3, 4, 5, 12, 13, 14, 15, 16),
                    # pipeline categorical indexes
                    categorical=(0, 6, 7, 8, 9, 10, 11, 17),
                    feature_names=feature_names
                )
                preds = model.predict(X_test)
                predictions = [pred[1] for pred in preds]
                _score_f1 = f1_score(y_test, predictions)
                _score_average_prec = average_precision_score(
                    y_test, predictions)
                _score_auc_ = roc_auc_score(y_test, predictions)
                _score_accuracy = accuracy_score(y_test, predictions)
                _score_recall = recall_score(y_test, predictions)
                print('Iter: {0}, Recall Score: {1}'.format(i, _score_recall))
                models.append({'model': model,
                               'f1_score': _score_f1,
                               'average_score': _score_average_prec,
                               'auc_score': _score_auc_,
                               'accuracy_score': _score_accuracy,
                               'recall_score': _score_recall})

            best_model = max(models, key=lambda model: model['f1_score'])
            model_name = 'xgb_cv_optimal_{0}.joblib'.format(
                datetime.now().strftime('%Y-%m-%d'))
            dump_model(best_model['model'], model_name)
            bst = best_model['model']
            print('Best estimator params: {0}'.format(bst.model.best_params_))
            mapper = {'f{0}'.format(i): v for i,
                      v in enumerate(bst.feature_names)}
            mapped = {mapper.get(
                k, None): v for k, v in bst.model.best_estimator_.named_steps["clf"].get_booster().get_fscore().items()}
            print('Best model f1 score: {0}'.format(best_model['f1_score']))
            print('Best model avg precision score: {0}'.format(
                best_model['average_score']))
            print('Best model auc score: {0}'.format(best_model['auc_score']))
            print('Best model accuracy score: {0}'.format(
                best_model['accuracy_score']))
            print('Best model recall score: {0}'.format(
                best_model['recall_score']))
            end = time.time()
            print('End processing time: {0}'.format(end - start))
            XGBModel.plot_model_importance(mapped)
        else:
            print('RF')
    else:  # Existing model
        model = load_model(args.model)
        # test_vals = nparray([
        #     ['PROVIDENCE', 276.972, 0.405, 0.0, 14180.811764705883, 1.51, 12, 22, 'Clouds',
        #         11, 23, 6, 3.78252697184816e-05, 494.81508556891293, 23361.74603174603, 5, 45, 3]
        # ], dtype='O')
        df = pd.read_csv("trainset.csv")
        test_vals = df.values
        print(test_vals)
        preds = model.predict(test_vals)
        pred_prob = model.model.predict_proba(test_vals)
        print(pred_prob)
        predictions = [pred[1] for pred in preds]
        print(predictions)


if __name__ == '__main__':
    main()
