"""
Module for ML Model types and wrapper for operations
Included: XGBoost, RandomForest (ensemble)
"""
from xgboost.sklearn import XGBClassifier
from xgboost import plot_importance
from matplotlib import pyplot
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from traffic_analyzer import ColumnExtractor
from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import SelectKBest, f_classif, VarianceThreshold


class XGBModel(object):
    """
    XGBoost wrapper class 
    https://xgboost.readthedocs.io/en/latest/python/python_api.html
    """

    def __init__(self, feature_names):
        self.model = None
        self.feature_names = feature_names

    def train_grid(self, X, y, X_numeric, X_categorical, cv=10):
        """
        Trains hyperparameter grid
        Args:
            X: features set of observations to train
            y: train labels
            X_numeric: The list of column indexes of the numeric features
            X_categorical: The list of column indexes of the categorical features
            cv: cross-validations to perform
        """
        pipeline = Pipeline([
            ('preproc', FeatureUnion([
                ('continuous', Pipeline([
                    ('extract', ColumnExtractor(cols=X_numeric)),
                    ('impute', SimpleImputer()),
                    ('scaler', StandardScaler())
                ])),
                ('factors', Pipeline([
                    ('extract', ColumnExtractor(cols=X_categorical)),
                    ('onehot', OneHotEncoder(handle_unknown='ignore')),
                ])),
            ])),
            ('clf', XGBClassifier())  # Boosted trees classifier
        ])
        """
        https://xgboost.readthedocs.io/en/latest/parameter.html
        """
        params = {  # Params to be defined based on testing
            'clf__max_depth': [3, 5, 10],
            'clf__learning_rate': [0.005, 0.05, 0.5],
            'clf__n_estimators': [1000, 3000],
            'clf__min_child_weight': [1, 3, 5],
            'clf__colsample_bytree': [0.8],
            'clf__colsample_bylevel': [0.8]
        }
        gridsearch = GridSearchCV(
            estimator=pipeline,
            param_grid=params,
            scoring='f1',  # F1 scoring for imbalanced data
            cv=cv,
            n_jobs=4 # Parallel
        )
        gridsearch.fit(X, y)
        self.model = gridsearch

    def predict(self, observations):
        """
        Predicts class from list of observations
        Args:
            observations: list of observations with appropriate features processed
        Returns list of tuples -> observa;tions tagged with prediction 0 vs. 1
        """
        predictions = self.model.predict(observations)
        return list(zip(observations, predictions))

    @staticmethod
    def plot_model_importance(model):
        """
        Plot model importance
        """
        plot_importance(model)
        pyplot.show()


class RFModel(object):
    """
    RandomForest wrapper class 
    https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
    """

    def __init__(self, model):
        self.model = None
