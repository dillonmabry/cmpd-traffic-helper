"""
Module for ML Model types and wrapper for operations
Included: XGBoost, RandomForest (ensemble)
"""
import xgboost as xgb
from matplotlib import pyplot
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV
from traffic_analyzer import ColumnExtractor
from traffic_analyzer import Logger


class XGBModel(object):
    """
    XGBoost wrapper class 
    https://xgboost.readthedocs.io/en/latest/python/python_api.html
    """

    def __init__(self):
        self.model = None
        self.logger = Logger(self.__class__.__name__).get()
        self.feature_names = None

    def train_grid(self, X, y, X_numeric, X_categorical):
        """
        Trains hyperparameter grid
        Args:
            X: features set of observations to train
            y: train labels
            X_numeric: The list of column indexes of the numeric features
            X_categorical: The list of column indexes of the categorical features
            feature_names: The feature named representations
        """
        pipeline = Pipeline([
            ('preproc', FeatureUnion([
                ('continuous', Pipeline([
                    ('extract', ColumnExtractor(cols=X_numeric)),
                    ('impute', SimpleImputer()),
                    ('scaler', StandardScaler()),
                ])),
                ('factors', Pipeline([
                    ('extract', ColumnExtractor(cols=X_categorical)),
                    ('onehot', OneHotEncoder(handle_unknown='ignore')),
                ])),
            ])),
            ('clf', xgb.XGBClassifier())  # Boosted trees classifier
        ])
        self.logger.info('Created XGB Pipeline with the following steps: {0}'.format(
            pipeline.named_steps))
        """
        https://xgboost.readthedocs.io/en/latest/parameter.html
        """
        params = {
            'clf__max_depth': [3, 5, 7],
            'clf__learning_rate': [0.005, 0.05],
            'clf__n_estimators': [250, 500],
            'clf__min_child_weight': [3, 5],
            'clf__colsample_bytree': [0.7],
            'clf__scale_pos_weight': [1],
            'clf__reg_lambda': [0.0, 0.5],
        }
        gridsearch = GridSearchCV(
            estimator=pipeline,
            param_grid=params,
            scoring='recall',
            cv=10,
            n_jobs=4,  # Jobs for processing
            verbose=10
        )
        gridsearch.fit(X, y)
        self.model = gridsearch

    def predict(self, observations):
        """
        Predicts class from list of observations
        Args:
            observations: list of observations with appropriate features processed
        Returns list of tuples -> observations tagged with prediction 0 vs. 1
        """
        predictions = self.model.predict(observations)
        return list(zip(observations, predictions))

    @staticmethod
    def plot_model_importance(model):
        """
        Plot model importance
        """
        xgb.plot_importance(model)
        pyplot.show()

    @staticmethod
    def plot_model_features(model, feature_names):
        """
        Plot various model interpretations
        """
        mapper = {'f{0}'.format(i): v for i,
                  v in enumerate(feature_names)}
        # Overall importance
        mapped = {mapper.get(
            k, None): v for k, v in model.model.best_estimator_.named_steps["clf"].get_booster().get_fscore().items()}
        XGBModel.plot_model_importance(mapped)
        # Gain
        mapped_gain = {mapper.get(
            k, None): v for k, v in model.model.best_estimator_.named_steps["clf"].get_booster().get_score(importance_type='gain').items()}
        XGBModel.plot_model_importance(mapped_gain)
